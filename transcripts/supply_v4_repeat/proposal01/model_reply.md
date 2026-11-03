The starter’s PMOS input pair has little headroom with VCM=0.9 V and VDD=1.15 V. This proposal uses an NMOS input pair, a PMOS mirror load, and a PMOS output gain stage. Long NMOS channels support DC gain; series-RC Miller compensation controls the loop response.

```spice
.subckt dut iref inp inn out
xnb iref iref 0 0 sky130_fd_pr__nfet_01v8_lvt W=20 L=2 nf=1 m=1
xnt tail iref 0 0 sky130_fd_pr__nfet_01v8_lvt W=60 L=2 nf=1 m=1

xni1 nd inn tail 0 sky130_fd_pr__nfet_01v8_lvt W=120 L=2 nf=1 m=1
xni2 ng inp tail 0 sky130_fd_pr__nfet_01v8_lvt W=120 L=2 nf=1 m=1
xpm1 nd nd vdd vdd sky130_fd_pr__pfet_01v8_lvt W=100 L=1 nf=1 m=1
xpm2 ng nd vdd vdd sky130_fd_pr__pfet_01v8_lvt W=100 L=1 nf=1 m=1

xpo out ng vdd vdd sky130_fd_pr__pfet_01v8_lvt W=300 L=0.5 nf=1 m=1
xno out iref 0 0 sky130_fd_pr__nfet_01v8_lvt W=140 L=2 nf=1 m=1

rz ng nc 1800
cc nc out 1.2e-12
.ends dut
```

**Unmeasured first proposal.** Ideal current-mirror ratios estimate 60 µA input-tail current and 140 µA output bias, giving approximately 220 µA total, including Iref, or 253–275 µW across the three supplies. Actual currents will depend on device operating points. Gain, stability, saturation margins, and command-relative settling require the simulator feedback; no passing performance is claimed.