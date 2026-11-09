.subckt dut iref inp inn out
* Reference and bias-current translation
Xref iref iref 0 0 sky130_fd_pr__nfet_01v8_lvt W=40 L=1 nf=1 m=1
Xbias pb iref 0 0 sky130_fd_pr__nfet_01v8_lvt W=20 L=1 nf=1 m=1
Xpb pb pb vdd vdd sky130_fd_pr__pfet_01v8_lvt W=20 L=1 nf=1 m=1

* NMOS differential input stage
Xtail tail iref 0 0 sky130_fd_pr__nfet_01v8_lvt W=120 L=1 nf=1 m=1
Xin_p stage inp tail 0 sky130_fd_pr__nfet_01v8_lvt W=30 L=1.5 nf=1 m=1
Xin_n mirror inn tail 0 sky130_fd_pr__nfet_01v8_lvt W=30 L=1.5 nf=1 m=1
Xload_ref mirror mirror vdd vdd sky130_fd_pr__pfet_01v8_lvt W=30 L=1 nf=1 m=1
Xload_out stage mirror vdd vdd sky130_fd_pr__pfet_01v8_lvt W=30 L=1 nf=1 m=1

* Common-source output stage
Xdrive out stage 0 0 sky130_fd_pr__nfet_01v8_lvt W=100 L=1 nf=1 m=1
Xpullup out pb vdd vdd sky130_fd_pr__pfet_01v8_lvt W=270 L=1 nf=1 m=1

* Miller compensation with series zero-setting resistor
Rcomp stage comp 2700
Ccomp comp out 0.85p
.ends dut
