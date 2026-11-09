"""Regression checks for collection recovery and prepared runtime boundaries."""

from copy import deepcopy
from pathlib import Path
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
PAYLOAD = ROOT / "reproduction/payload"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


collection = load("integrity_collection", ROOT / "tools/collect_trials.py")
qualification = load("integrity_qualification", PAYLOAD / "qualification.py")
core = load("integrity_core", PAYLOAD / "eval_core_v6/run_eval.py")


class RuntimeIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.candidate = self.root / "candidate.sp"
        self.candidate.write_text("captured circuit")
        self.runner = self.root / "eval_core_v6/run_eval.py"
        self.runner.parent.mkdir()
        self.runner.write_text("runner identity")
        self.runner.with_name("dependency_lock.json").write_text("{}")
        self.run = self.root / "eval_core_v6/runs/supply/recovery"
        self.run.mkdir(parents=True)
        (self.run / "candidate_original.sp").write_bytes(self.candidate.read_bytes())
        self.result = {
            "category": "pass",
            "score": 100,
            "task_id": "SUPPLY-P01-v2",
            "run_id": "recovery",
            "proposal": 1,
            "numerics": "refined",
            "evidence_mode": "fresh_native_simulation",
            "candidate_sha256": collection.sha(self.candidate),
            "runner_sha256": collection.sha(self.runner),
            "dependency_lock_sha256": collection.sha(
                self.runner.with_name("dependency_lock.json")
            ),
        }
        self.save_result()

    def save_result(self):
        (self.run / "result.json").write_text(json.dumps(self.result))
        rows = [
            {
                "path": name,
                "bytes": (self.run / name).stat().st_size,
                "sha256": collection.sha(self.run / name),
            }
            for name in ("result.json", "candidate_original.sp")
        ]
        (self.run / "manifest.json").write_text(json.dumps({"files": rows}))

    def evaluate(self):
        return collection.native_evaluate(
            self.root, "supply", self.candidate, "recovery", 1, True
        )

    def test_complete_matching_run_is_reused_without_launch(self):
        with patch.object(collection.subprocess, "run") as launch:
            result, receipt = self.evaluate()
        launch.assert_not_called()
        self.assertEqual(result, self.result)
        self.assertEqual(receipt["evaluator"], "eval_core_v6")

    def test_recovery_rejects_wrong_evaluation_identity(self):
        for key in self.result.keys() - {"category", "score"}:
            with self.subTest(field=key):
                before = self.result[key]
                self.result[key] = "wrong"
                self.save_result()
                with self.assertRaisesRegex(ValueError, "identity"):
                    self.evaluate()
                self.result[key] = before
        self.save_result()

    def test_recovery_rejects_changed_and_incomplete_artifacts(self):
        (self.run / "result.json").write_text(json.dumps({**self.result, "score": 0}))
        with self.assertRaisesRegex(ValueError, "artifact changed"):
            self.evaluate()
        self.save_result()
        (self.run / "manifest.json").write_text('{"files": []}')
        with self.assertRaisesRegex(ValueError, "incomplete"):
            self.evaluate()
        self.save_result()
        manifest = json.loads((self.run / "manifest.json").read_text())
        manifest["files"][0]["path"] = "../outside"
        (self.run / "manifest.json").write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, "manifest path"):
            self.evaluate()

    def test_feedback_retains_safe_reason_and_rejects_private_reason(self):
        check = {
            "metric": "gm_dB",
            "value": None,
            "operator": ">=",
            "limit": 10,
            "pass": True,
            "reason": "no_finite_crossover_in_sweep",
        }
        result = {
            "category": "pass",
            "points": [{"condition": "test", "pass": True, "checks": [check]}],
        }
        self.assertIn(check["reason"], collection.feedback(result, 1))
        check["reason"] = "/Users/" + "example/private"
        with self.assertRaisesRegex(ValueError, "Private metadata"):
            collection.feedback(result, 1)

    def test_qualification_compares_scalars_lists_nulls_and_classification(self):
        point = {
            "condition": "test",
            "pass": True,
            "checks": [
                {
                    "metric": "margin",
                    "operator": ">=",
                    "limit": 55,
                    "pass": True,
                    "value": [60.0, 70.0],
                },
                {
                    "metric": "gm",
                    "operator": ">=",
                    "limit": 10,
                    "pass": True,
                    "value": None,
                },
            ],
        }
        self.assertEqual(len(qualification.compare_measurements([point], [point])), 2)
        small = deepcopy(point)
        small["checks"][0]["value"][0] += 1e-6
        qualification.compare_measurements([small], [point])
        for value in ([60.0, 80.0], [60.0], [60.0, True], [60.0, float("nan")]):
            bad = deepcopy(point)
            bad["checks"][0]["value"] = value
            with self.assertRaises(ValueError):
                qualification.compare_measurements([bad], [point])
        bad = deepcopy(point)
        bad["checks"][1]["value"] = 0
        with self.assertRaises(ValueError):
            qualification.compare_measurements([bad], [point])
        bad = deepcopy(point)
        bad["pass"] = False
        with self.assertRaises(ValueError):
            qualification.compare_measurements([bad], [point])

    def test_prepared_exports_match_repository_for_all_revisions(self):
        exporter = load("integrity_exporter", ROOT / "tools/export_task.py")
        prepared = load(
            "integrity_prepared_exporter",
            PAYLOAD / "public_packets/tools/export_task.py",
        )
        for task in ("supply", "load", "tia"):
            for revision in (None, "recorded", "clarified-1", "clarified-2"):
                name = task + "_" + str(revision)
                a, b = self.root / (name + "a"), self.root / (name + "b")
                self.assertEqual(
                    exporter.export(task, a, revision=revision),
                    prepared.export(task, b, revision=revision),
                )
                self.assertEqual(
                    {p.name: p.read_bytes() for p in a.iterdir()},
                    {p.name: p.read_bytes() for p in b.iterdir()},
                )

    def test_optimized_runtime_fails_before_native_execution(self):
        result = subprocess.run(
            [
                sys.executable,
                "-I",
                "-B",
                "-O",
                str(PAYLOAD / "eval_core_v6/run_eval.py"),
                "inspect",
                "--task",
                "supply",
            ],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("without Python optimization", result.stderr)

    def test_serialization_rejects_nonfinite_without_partial_result(self):
        for writer in (core.save, qualification.write):
            target = self.root / (writer.__module__ + '.json')
            with self.assertRaises(ValueError):
                writer(target, {'extra_metric': float('nan')})
            self.assertFalse(target.exists())

    def test_nonfinite_measurement_becomes_unscored_infrastructure_result(self):
        source = self.root / 'replay.json'
        source.write_text('{}')
        output = self.root / 'outputs'
        output.mkdir()
        (output / 'dependency_lock.json').write_text('{}')
        result = {'category': 'pass', 'score': 100, 'success': True,
                  'points': [{'condition': 'test', 'extra': float('nan')}]}
        with patch.object(core, 'HERE', output), patch.object(core, 'verify', return_value=1), \
             patch.object(core, 'assess', return_value=result), \
             patch('sys.argv', ['run_eval.py', 'replay', '--task', 'load',
                                '--source', str(source), '--run-id', 'nonfinite']):
            self.assertEqual(core.main(), 3)
        run = output / 'runs/load/nonfinite'
        data = json.loads((run / 'result.json').read_text())
        self.assertEqual(data['category'], 'infrastructure_error')
        self.assertIsNone(data['score'])
        self.assertIn('Non-finite', data['error'])
        self.assertTrue((run / 'manifest.json').is_file())
        self.assertNotIn('points', data)

    def test_manifest_refresh_excludes_cached_python_files(self):
        refresh = load('refresh_test', ROOT / 'tools/refresh_manifests.py')
        root = self.root / 'fixture'
        kit = root / 'reproduction'
        payload = kit / 'payload'
        v5 = payload / 'eval_core_v5'
        v6 = payload / 'eval_core_v6'
        public = payload / 'public_packets/tools'
        for folder in (v5, v6, public, root / 'evidence'):
            folder.mkdir(parents=True)
        for name in ('run_eval.py', 'supply_adapter.py', 'tia_adapter.py'):
            (v6 / name).write_text('test')
        (public / 'export_task.py').write_text('test')
        (public / 'export_task.pyc').write_bytes(b'cache')
        cache = public / '__pycache__'
        cache.mkdir()
        (cache / 'export_task.pyc').write_bytes(b'cache')
        for path in (v5 / 'dependency_lock.json', kit / 'source_manifest.json', kit / 'kit_manifest.json'):
            path.write_text('{"files": []}')
        (root / 'evidence/path_redactions.json').write_text('{"records": []}')
        with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'KIT', kit), \
             patch.object(refresh, 'PAYLOAD', payload):
            refresh.main()
        for path in (v6 / 'dependency_lock.json', kit / 'source_manifest.json', kit / 'kit_manifest.json'):
            files = [row['path'] for row in json.loads(path.read_text())['files']]
            self.assertTrue(files)
            self.assertFalse(any('__pycache__' in name or name.endswith(('.pyc', '.pyo')) for name in files))

    def test_replay_references_remain_valid_markdown_links(self):
        body = (ROOT / 'docs/task-validation.md').read_text()
        target = '(../evidence/task_contract_audit_clarified2_v5.json)'
        for label in ('recorded v5 task-contract audit', 'Recorded v5 audit record'):
            self.assertIn('[' + label + ']' + target, body)

    def test_successful_stage_cleanup_and_failed_stage_retention(self):
        # Test the actual CLI control flow with a synthetic native producer.
        for category in ("pass", "infrastructure_error", "nonfinite"):
            stage = self.root / category
            stage.mkdir()
            native = stage / "analog_supply_pilot_v1/runs/s"
            native.mkdir(parents=True)
            (native / "result.json").write_text("{}")
            script = self.root / ("stub_" + category + ".py")
            script.write_text("")
            with patch.object(
                core, "HERE", self.root / "outputs" / category
            ), patch.object(core, "verify", return_value=1), patch.object(
                core, "sha", return_value="identity"
            ), patch.object(
                core, "read", return_value={}
            ), patch.object(
                core, "compile_candidate", return_value=("compiled", {})
            ), patch.object(
                core, "stage_runtime", return_value=stage
            ), patch.object(
                core,
                "assess",
                return_value={
                    "category": "pass" if category == "nonfinite" else category,
                    "score": 100 if category in ("pass", "nonfinite") else None,
                    **({"points": [{"unused": float("nan")}]} if category == "nonfinite" else {}),
                },
            ), patch.object(
                core.subprocess, "Popen"
            ) as process, patch.object(
                core, "write_outputs"
            ), patch(
                "sys.argv",
                [
                    "run_eval.py",
                    "evaluate",
                    "--task",
                    "supply",
                    "--candidate",
                    str(self.candidate),
                    "--run-id",
                    "cleanup",
                ],
            ):
                (self.root / "outputs" / category).mkdir(parents=True)
                process.return_value.returncode = 0
                self.assertEqual(core.main(), 0 if category == "pass" else 3)
            self.assertEqual(stage.exists(), category != "pass")


if __name__ == "__main__":
    unittest.main()
