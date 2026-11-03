
.subckt dut iref inp inn out
xnbref iref iref 0 0 sky130_fd_pr__nfet_01v8_lvt W=30 L=2 nf=1 m=1
xntail ntail iref 0 0 sky130_fd_pr__nfet_01v8_lvt W=135 L=2 nf=1 m=1
xnbias vpb iref 0 0 sky130_fd_pr__nfet_01v8_lvt W=30 L=2 nf=1 m=1
xpbias vpb vpb vdd vdd sky130_fd_pr__pfet_01v8_lvt W=300 L=2 nf=1 m=1
xpcb vcas vpb vdd vdd sky130_fd_pr__pfet_01v8_lvt W=150 L=2 nf=1 m=1
xncb vcas vcas 0 0 sky130_fd_pr__nfet_01v8_lvt W=35 L=1 nf=1 m=1
xn1 nref inn ntail 0 sky130_fd_pr__nfet_01v8_lvt W=300 L=2 nf=1 m=1
xn2 n1 inp ntail 0 sky130_fd_pr__nfet_01v8_lvt W=300 L=2 nf=1 m=1
xp1 psrc1 nref vdd vdd sky130_fd_pr__pfet_01v8_lvt W=35 L=0.35 nf=1 m=1
xp2 psrc2 nref vdd vdd sky130_fd_pr__pfet_01v8_lvt W=35 L=0.35 nf=1 m=1
xpc1 nref vcas psrc1 psrc1 sky130_fd_pr__pfet_01v8_lvt W=350 L=0.5 nf=1 m=1
xpc2 n1 vcas psrc2 psrc2 sky130_fd_pr__pfet_01v8_lvt W=350 L=0.5 nf=1 m=1
xpout out vpb vdd vdd sky130_fd_pr__pfet_01v8_lvt W=400 L=3 nf=1 m=5
xnout nmid n1 0 0 sky130_fd_pr__nfet_01v8_lvt W=40 L=0.5 nf=1 m=1
xncas out vcasn nmid 0 sky130_fd_pr__nfet_01v8_lvt W=80 L=1 nf=1 m=1
rbtop vdd vcasn 200000
rbbot vcasn 0 450000
cbn vcasn 0 1e-11
cbp vcas 0 1e-11
rz n1 nc 3900
cc nc out 1.25e-12
.ends dut
