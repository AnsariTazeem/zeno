.subckt dut iref inp inn out
* Proposal 1: NMOS-input two-stage amplifier
* Reference and bias generation
xnb iref iref 0 0 sky130_fd_pr__nfet_01v8_lvt W=20 L=1 nf=1 m=1
xnbp vbp iref 0 0 sky130_fd_pr__nfet_01v8_lvt W=20 L=1 nf=1 m=1
xpb vbp vbp vdd vdd sky130_fd_pr__pfet_01v8_lvt W=40 L=1 nf=1 m=1

* Input pair and current-mirror load
xnt tail iref 0 0 sky130_fd_pr__nfet_01v8_lvt W=60 L=1 nf=1 m=1
xni1 mir inn tail 0 sky130_fd_pr__nfet_01v8_lvt W=200 L=2 nf=1 m=1
xni2 vg inp tail 0 sky130_fd_pr__nfet_01v8_lvt W=200 L=2 nf=1 m=1
xpl1 mir mir vdd vdd sky130_fd_pr__pfet_01v8_lvt W=52 L=0.65 nf=1 m=1
xpl2 vg mir vdd vdd sky130_fd_pr__pfet_01v8_lvt W=52 L=0.65 nf=1 m=1

* Output gain stage
xno out vg 0 0 sky130_fd_pr__nfet_01v8_lvt W=40 L=0.5 nf=1 m=1
xpo out vbp vdd vdd sky130_fd_pr__pfet_01v8_lvt W=240 L=1 nf=1 m=1

* Miller compensation and zero placement
rz vg cz 1800
cc cz out 1.2p
.ends dut
