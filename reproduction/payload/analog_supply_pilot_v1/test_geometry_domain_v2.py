"""Verify model-specific limits without launching a simulator."""
from pathlib import Path
from circuit_input import compile_dut,InvalidCircuit
from geometry_domain_v2 import compile_supported_dut

BASE=Path(__file__).resolve().parent
APP=BASE.parent/"analog_public_v1"
for version in ("1v2","1v8"):
    text=(APP/f"upstream/benchmark/golden/opamp_2stg_{version}.sp").read_text()
    assert compile_supported_dut(text)==compile_dut(text)
for number in (1,2):
    text=(BASE/f"trials/trial02/proposal{number:02d}/candidate_rendered.sp").read_text()
    assert compile_supported_dut(text)==compile_dut(text)
for model,length in (("nfet",0.15),("pfet",0.35)):
    for w,l in ((1,length),(1000,10)):
        text=f".subckt dut iref inp inn out\nX1 out inp 0 0 sky130_fd_pr__{model}_01v8_lvt W={w} L={l}\n.ends dut"
        compile_supported_dut(text)
bad=(BASE/"trials/trial02/proposal03/candidate_rendered.sp").read_text()
try:
    compile_supported_dut(bad)
except InvalidCircuit as exc:
    assert "xpmir1" in str(exc) and "xpmir2" in str(exc)
else:
    raise AssertionError("Accepted unsupported PMOS L=0.3")
print("References and both valid proposals preserved exactly; NMOS/PMOS boundary choices accepted; both unsupported final devices rejected.")
