.subckt dut iref inp inn out
rb iref nb 27000
xnb nb nb 0 0 sky130_fd_pr__nfet_01v8_lvt W=20 L=2 nf=1 m=1
rbt nb pcb 140000
rbb pcb 0 420000
cbn nb 0 5e-11
cbnc iref 0 5e-11
cbpc pcb 0 5e-11

xnt tail nb 0 0 sky130_fd_pr__nfet_01v8_lvt W=80 L=2 nf=1 m=1

xni1 na inp tail 0 sky130_fd_pr__nfet_01v8_lvt W=75 L=1.5 nf=1 m=1
xni2 nbm inn tail 0 sky130_fd_pr__nfet_01v8_lvt W=75 L=1.5 nf=1 m=1
xnc1 stage iref na 0 sky130_fd_pr__nfet_01v8_lvt W=120 L=0.5 nf=1 m=1
xnc2 mirror iref nbm 0 sky130_fd_pr__nfet_01v8_lvt W=120 L=0.5 nf=1 m=1

xpl1 pa mirror vdd vdd sky130_fd_pr__pfet_01v8_lvt W=140 L=1 nf=1 m=1
xpl2 pb mirror vdd vdd sky130_fd_pr__pfet_01v8_lvt W=140 L=1 nf=1 m=1
xpc1 mirror pcb pa pa sky130_fd_pr__pfet_01v8_lvt W=140 L=1 nf=1 m=1
xpc2 stage pcb pb pb sky130_fd_pr__pfet_01v8_lvt W=140 L=1 nf=1 m=1

xpo out stage vdd vdd sky130_fd_pr__pfet_01v8_lvt W=180 L=0.35 nf=1 m=1
xno out nb 0 0 sky130_fd_pr__nfet_01v8_lvt W=125 L=2 nf=1 m=1

rz na comp 500
cc comp out 1.8e-12
.ends dut
