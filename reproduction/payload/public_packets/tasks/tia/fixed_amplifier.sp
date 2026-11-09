* Compiled component-only pilot DUT; no supplied simulator commands.
.subckt dut iref inp inn out
r0 iref vnc 1
rn vnc vnb 13000
xnr3 vnb vnc nr1 0 sky130_fd_pr__nfet_01v8_lvt W=20 L=0.5 nf=1 m=1
xnr1 nr1 vnb 0 0 sky130_fd_pr__nfet_01v8_lvt W=40 L=2 nf=1 m=1
xns1 vpc vnb 0 0 sky130_fd_pr__nfet_01v8_lvt W=10 L=2 nf=1 m=1
rp vpb vpc 34000
xpr3 vpb vpc pr1 vdd sky130_fd_pr__pfet_01v8_lvt W=20 L=0.5 nf=1 m=1
xpr1 pr1 vpb vdd vdd sky130_fd_pr__pfet_01v8_lvt W=10 L=1 nf=1 m=1
xnt tail vnb 0 0 sky130_fd_pr__nfet_01v8_lvt W=50 L=2 nf=1 m=1
xni1 fa inp tail 0 sky130_fd_pr__nfet_01v8_lvt W=40 L=0.5 nf=1 m=1
xni2 fb inn tail 0 sky130_fd_pr__nfet_01v8_lvt W=40 L=0.5 nf=1 m=1
xps1 fa vpb vdd vdd sky130_fd_pr__pfet_01v8_lvt W=10 L=1 nf=1 m=6
xps2 fb vpb vdd vdd sky130_fd_pr__pfet_01v8_lvt W=10 L=1 nf=1 m=6
xpc1 o1 vpc fa vdd sky130_fd_pr__pfet_01v8_lvt W=70 L=0.5 nf=1 m=1
xpc2 d1 vpc fb vdd sky130_fd_pr__pfet_01v8_lvt W=70 L=0.5 nf=1 m=1
xnl3 d1 vnc nl1 0 sky130_fd_pr__nfet_01v8_lvt W=20 L=0.5 nf=1 m=1
xnl1 nl1 d1 0 0 sky130_fd_pr__nfet_01v8_lvt W=10 L=0.5 nf=1 m=1
xnl4 o1 vnc nl2 0 sky130_fd_pr__nfet_01v8_lvt W=20 L=0.5 nf=1 m=1
xnl2 nl2 d1 0 0 sky130_fd_pr__nfet_01v8_lvt W=10 L=0.5 nf=1 m=1
xn6 out o1 0 0 sky130_fd_pr__nfet_01v8_lvt W=40 L=0.5 nf=1 m=1
xp7 out vpb vdd vdd sky130_fd_pr__pfet_01v8_lvt W=10 L=1 nf=1 m=19
rz o1 cz 2000
cc cz out 5.2000000000000001e-13
.ends dut
