from copy import deepcopy
import unittest, importlib.util
import run_eval as c

spec = importlib.util.spec_from_file_location(
    "old_regressions", c.ROOT / "eval_core_v2/test_core.py"
)
previous = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous)


class ExistingAdapterTests(previous.CoreTests):
    pass


CONTRACT = c.read(c.ROOT / "tia_case_v1/public/contract.json")
GOOD = c.read(c.ROOT / "tia_case_v1/evaluations/reference_rg5000_refined01/result.json")
ALT = c.read(c.ROOT / "tia_case_v1/evaluations/TIA_T02_P02_refined/result.json")
BAD = c.read(c.ROOT / "tia_case_v1/evaluations/undercompensated_1p_01/result.json")


def grade(x):
    return c.assess("tia", x, CONTRACT)


class TIATests(unittest.TestCase):
    def test_reference_alternative_and_negative(self):
        self.assertTrue(grade(GOOD)["success"])
        self.assertTrue(grade(ALT)["success"])
        self.assertFalse(grade(BAD)["success"])

    def test_wrong_transfer_sign_fails(self):
        d = deepcopy(GOOD)
        d["cases"][0]["ac"]["dc_transimpedance_real_ohm"] = 10000
        self.assertEqual(grade(d)["category"], "specification_failure")

    def test_imaginary_boundary_inclusive(self):
        d = deepcopy(GOOD)
        d["cases"][0]["ac"]["dc_transimpedance_imag_ohm"] = 1
        self.assertTrue(grade(d)["success"])
        d["cases"][0]["ac"]["dc_transimpedance_imag_ohm"] = 1.0001
        self.assertFalse(grade(d)["success"])

    def test_first_bandwidth_crossing_not_a_later_one(self):
        d = deepcopy(GOOD)
        d["cases"][0]["ac"]["first_minus_3dB_Hz"] = 9e5
        d["cases"][0]["ac"]["all_minus_3dB_crossings_Hz"] = [9e5, 2e6]
        self.assertFalse(grade(d)["success"])

    def test_all_loop_crossings_must_pass(self):
        d = deepcopy(GOOD)
        ac = d["cases"][1]["ac"]
        ac["unity_downward_crossings_Hz"] = [1e6, 2e6]
        ac["phase_margins_deg"] = [70, 54]
        self.assertFalse(grade(d)["success"])

    def test_initial_accuracy_power_and_edge_regressions(self):
        d = deepcopy(GOOD)
        d["cases"][0]["transient"]["initial_error_V"] = 0.00101
        self.assertFalse(grade(d)["success"])
        d = deepcopy(GOOD)
        d["cases"][0]["ac"]["dc_delivered_power_uW"] = 301
        self.assertFalse(grade(d)["success"])
        for key, value in [("settle_ns", 501), ("overshoot_V", 0.0101)]:
            d = deepcopy(GOOD)
            d["cases"][0]["transient"]["edges"][2][key] = value
            self.assertFalse(grade(d)["success"])

    def test_none_is_not_settled_but_missing_is_invalid(self):
        d = deepcopy(GOOD)
        d["cases"][0]["transient"]["edges"][0]["settle_ns"] = None
        self.assertEqual(grade(d)["category"], "specification_failure")
        del d["cases"][0]["transient"]["edges"][0]["settle_ns"]
        self.assertIsNone(grade(d)["score"])

    def test_aggregate_pass_flags_cannot_override_measurements(self):
        d = deepcopy(BAD)
        d["all_points_pass"] = True
        for row in d["cases"]:
            row["pass"] = True
        self.assertFalse(grade(d)["success"])

    def test_nonfinite_and_bool_invalid(self):
        for v in [float("nan"), float("inf"), True]:
            d = deepcopy(GOOD)
            d["cases"][0]["ac"]["dc_delivered_power_uW"] = v
            self.assertIsNone(grade(d)["score"])

    def test_truncated_trace_or_duplicate_fixture_invalid(self):
        d = deepcopy(GOOD)
        d["cases"][0]["transient"]["stop_s"] = 4e-6
        self.assertIsNone(grade(d)["score"])
        d = deepcopy(GOOD)
        d["cases"][-1] = deepcopy(d["cases"][0])
        self.assertIsNone(grade(d)["score"])

    def test_row_and_edge_order_equivalent(self):
        d = deepcopy(GOOD)
        d["cases"].reverse()
        for row in d["cases"]:
            row["transient"]["edges"].reverse()
        self.assertTrue(grade(d)["success"])

    def test_wrong_target_invalid(self):
        d = deepcopy(GOOD)
        d["cases"][0]["transient"]["edges"][0]["target_V"] = 1.0
        self.assertIsNone(grade(d)["score"])

    def test_model_network_and_equivalent_case_compile(self):
        text = (
            c.ROOT / "tia_case_v1/trials/trial02/proposal02/candidate_rendered.sp"
        ).read_text()
        a, ac = c.compile_candidate("tia", text)
        b, bc = c.compile_candidate("tia", "* alternative case\n" + text.upper())
        self.assertEqual(a, b)
        self.assertEqual(ac, bc)

    def test_source_directive_rejected(self):
        with self.assertRaises(ValueError):
            c.compile_candidate(
                "tia", ".subckt feedback sense out vref\n.include nope\n.ends feedback"
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
