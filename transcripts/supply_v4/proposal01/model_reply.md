The starter’s PMOS input pair has limited headroom above the fixed 0.9 V common mode at these supplies. This proposal uses an NMOS input pair, a folded-cascode first stage, and a common-source output stage. Miller compensation includes a series resistor to improve phase margin.

**Unmeasured first proposal:** the nominal bias allocation estimates roughly 260 µW at 1.25 V, before model-dependent current variation. Gain, bandwidth, stability, saturation and command-relative settling remain unverified.

```spice
.subckt dut iref inp inn out
rref iref vnc 1
rbias vnc vnb 15000
xnr3 vnb vnc nr1 0 sky130_fd_pr__nfet_01v8_lvt W=20 L=0.5 nf=1 m=1
xnr1 nr1 vnb 0 0 sky130_fd_pr__nfet_01v8_lvt W=40 L=2 nf=1 m=1
xns3 vpb vnc ns1 0 sky130_fd_pr__nfet_01v8_lvt W=5 L=0.5 nf=1 m=1
xns1 ns1 vnb 0 0 sky130_fd_pr__nfet_01v8_lvt W=10 L=2 nf=1 m=1
xpr1 vpb vpb vdd vdd sky130_fd_pr__pfet_01v8_lvt W=10 L=1 nf=1 m=1

xpfbias vpf vpb vdd vdd sky130_fd_pr__pfet_01v8_lvt W=4 L=1 nf=1 m=1
rpf vpf 0 125000

xntail tail vnb 0 0 sky130_fd_pr__nfet_01v8_lvt W=120 L=2 nf=1 m=1
xni1 ia inp tail 0 sky130_fd_pr__nfet_01v8_lvt W=120 L=0.5 nf=1 m=1
xni2 ib inn tail 0 sky130_fd_pr__nfet_01v8_lvt W=120 L=0.5 nf=1 m=1

xpt1 ia vpb vdd vdd sky130_fd_pr__pfet_01v8_lvt W=10 L=1 nf=1 m=8
xpt2 ib vpb vdd vdd sky130_fd_pr__pfet_01v8_lvt W=10 L=1 nf=1 m=8
xpf1 o1 vpf ia ia sky130_fd_pr__pfet_01v8_lvt W=40 L=0.5 nf=1 m=1
xpf2 d1 vpf ib ib sky130_fd_pr__pfet_01v8_lvt W=40 L=0.5 nf=1 m=1

xnl3 d1 vnc nl1 0 sky130_fd_pr__nfet_01v8_lvt W=20 L=0.5 nf=1 m=1
xnl1 nl1 d1 0 0 sky130_fd_pr__nfet_01v8_lvt W=10 L=0.5 nf=1 m=1
xnl4 o1 vnc nl2 0 sky130_fd_pr__nfet_01v8_lvt W=20 L=0.5 nf=1 m=1
xnl2 nl2 d1 0 0 sky130_fd_pr__nfet_01v8_lvt W=10 L=0.5 nf=1 m=1

xnout out o1 0 0 sky130_fd_pr__nfet_01v8_lvt W=100 L=0.5 nf=1 m=1
xpout out vpb vdd vdd sky130_fd_pr__pfet_01v8_lvt W=10 L=1 nf=1 m=20

rz o1 cz 2700
cc cz out 9e-13
.ends dut
```