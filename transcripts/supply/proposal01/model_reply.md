The starter’s PMOS input pair has limited headroom at the reduced supplies and 0.9 V input common mode. This proposal uses an NMOS input pair, longer first-stage channels for gain, and a PMOS output stage with series-R Miller compensation.

All performance is **unmeasured**. Adequate headroom, gain, and stability are design estimates requiring verification at all three supplies.

```spice
.subckt dut iref inp inn out
xnb iref iref 0 0 sky130_fd_pr__nfet_01v8_lvt W=20 L=2 nf=1 m=1
xnt tail iref 0 0 sky130_fd_pr__nfet_01v8_lvt W=80 L=2 nf=1 m=1

xni1 stage inp tail 0 sky130_fd_pr__nfet_01v8_lvt W=150 L=1.5 nf=1 m=1
xni2 mirror inn tail 0 sky130_fd_pr__nfet_01v8_lvt W=150 L=1.5 nf=1 m=1

xpl1 mirror mirror vdd vdd sky130_fd_pr__pfet_01v8_lvt W=140 L=1 nf=1 m=1
xpl2 stage mirror vdd vdd sky130_fd_pr__pfet_01v8_lvt W=140 L=1 nf=1 m=1

xpo out stage vdd vdd sky130_fd_pr__pfet_01v8_lvt W=180 L=0.7 nf=1 m=1
xno out iref 0 0 sky130_fd_pr__nfet_01v8_lvt W=100 L=2 nf=1 m=1

rz stage comp 2400
cc comp out 1.3e-12
.ends dut
```