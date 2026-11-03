.subckt dut iref inp inn out
xnb iref iref 0 0 sky130_fd_pr__nfet_01v8_lvt W=20 L=2 nf=1 m=1
xnt tail iref 0 0 sky130_fd_pr__nfet_01v8_lvt W=80 L=2 nf=1 m=1

rbias vdd vbtop 7500
xpbias vpc vpc vbtop vbtop sky130_fd_pr__pfet_01v8_lvt W=40 L=0.35 nf=1 m=1
xnbias vpc iref 0 0 sky130_fd_pr__nfet_01v8_lvt W=20 L=2 nf=1 m=1
cbtop vbtop vdd 10p
cbpc vpc vdd 10p

xni1 ni1 inp tail 0 sky130_fd_pr__nfet_01v8_lvt W=40 L=1 nf=1 m=1
xni2 ni2 inn tail 0 sky130_fd_pr__nfet_01v8_lvt W=40 L=1 nf=1 m=1
xnc1 nstage vbtop ni1 0 sky130_fd_pr__nfet_01v8_lvt W=50 L=0.5 nf=1 m=1
xnc2 nmirror vbtop ni2 0 sky130_fd_pr__nfet_01v8_lvt W=50 L=0.5 nf=1 m=1

xpm1 pmref nmirror vdd vdd sky130_fd_pr__pfet_01v8_lvt W=80 L=0.35 nf=1 m=1
xpm2 pmout nmirror vdd vdd sky130_fd_pr__pfet_01v8_lvt W=80 L=0.35 nf=1 m=1
xpc1 nmirror vpc pmref vdd sky130_fd_pr__pfet_01v8_lvt W=200 L=1 nf=1 m=1
xpc2 nstage vpc pmout vdd sky130_fd_pr__pfet_01v8_lvt W=200 L=1 nf=1 m=1

xpo out nstage vdd vdd sky130_fd_pr__pfet_01v8_lvt W=240 L=0.35 nf=1 m=1
xno out iref 0 0 sky130_fd_pr__nfet_01v8_lvt W=105 L=2 nf=1 m=1

rz nstage ncomp 1600
cc ncomp out 1.6p
.ends dut
