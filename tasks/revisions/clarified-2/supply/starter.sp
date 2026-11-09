* Compiled component-only pilot DUT; no supplied simulator commands.
.subckt dut iref inp inn out
r0 iref vnc 1
rn vnc vnb 15000
xnr3 vnb vnc nr1 0 sky130_fd_pr__nfet_01v8_lvt W=20 L=0.5 nf=1 m=1
xnr1 nr1 vnb 0 0 sky130_fd_pr__nfet_01v8_lvt W=40 L=2 nf=1 m=1
xns3 vpb vnc ns1 0 sky130_fd_pr__nfet_01v8_lvt W=5 L=0.5 nf=1 m=1
xns1 ns1 vnb 0 0 sky130_fd_pr__nfet_01v8_lvt W=10 L=2 nf=1 m=1
xpr1 vpb vpb vdd vdd sky130_fd_pr__pfet_01v8_lvt W=10 L=1 nf=1 m=1
xpt tail vpb vdd vdd sky130_fd_pr__pfet_01v8_lvt W=10 L=1 nf=1 m=5
xpi1 ia inp tail tail sky130_fd_pr__pfet_01v8_lvt W=160 L=0.5 nf=1 m=1
xpi2 ib inn tail tail sky130_fd_pr__pfet_01v8_lvt W=160 L=0.5 nf=1 m=1
xpc1 o1 vnb ia ia sky130_fd_pr__pfet_01v8_lvt W=20 L=0.5 nf=1 m=1
xpc2 d1 vnb ib ib sky130_fd_pr__pfet_01v8_lvt W=20 L=0.5 nf=1 m=1
xnl3 d1 vnc nl1 0 sky130_fd_pr__nfet_01v8_lvt W=20 L=0.5 nf=1 m=1
xnl1 nl1 d1 0 0 sky130_fd_pr__nfet_01v8_lvt W=10 L=0.5 nf=1 m=1
xnl4 o1 vnc nl2 0 sky130_fd_pr__nfet_01v8_lvt W=20 L=0.5 nf=1 m=1
xnl2 nl2 d1 0 0 sky130_fd_pr__nfet_01v8_lvt W=10 L=0.5 nf=1 m=1
xn6 out o1 0 0 sky130_fd_pr__nfet_01v8_lvt W=40 L=0.5 nf=1 m=1
xp7 out vpb vdd vdd sky130_fd_pr__pfet_01v8_lvt W=10 L=1 nf=1 m=19
rz o1 cz 3000
cc cz out 3.8000000000000005e-13
.ends dut
