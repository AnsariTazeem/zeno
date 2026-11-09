**Proposal 3 of 3; unverified.** Proposal 2 added little gain and reduced bandwidth, so this revision removes its input-stage cascodes. It instead cascades the output devices to increase second-stage gain, uses wide PMOS devices for pull-up headroom, and revises compensation. Compliance remains unresolved pending evaluation.

```spice
.subckt dut iref inp inn out
* Reference and NMOS output-cascode bias
Rref iref nb 15000
Xref nb nb 0 0 sky130_fd_pr__nfet_01v8_lvt W=40 L=1 nf=1 m=1

* PMOS reference and offset cascode bias
Xbias pcb nb 0 0 sky130_fd_pr__nfet_01v8_lvt W=20 L=1 nf=1 m=1
Xpref pb pb vdd vdd sky130_fd_pr__pfet_01v8_lvt W=50 L=0.5 nf=1 m=1
Rpc pb pcb 6000

* Differential input stage
Xtail tail nb 0 0 sky130_fd_pr__nfet_01v8_lvt W=120 L=1 nf=1 m=1
Xin_p stage inp tail 0 sky130_fd_pr__nfet_01v8_lvt W=30 L=1.5 nf=1 m=1
Xin_n mirror inn tail 0 sky130_fd_pr__nfet_01v8_lvt W=30 L=1.5 nf=1 m=1
Xload_ref mirror mirror vdd vdd sky130_fd_pr__pfet_01v8_lvt W=30 L=0.6 nf=1 m=1
Xload_out stage mirror vdd vdd sky130_fd_pr__pfet_01v8_lvt W=30 L=0.6 nf=1 m=1

* Cascoded NMOS output driver
Xdrive nd stage 0 0 sky130_fd_pr__nfet_01v8_lvt W=100 L=0.7 nf=1 m=1
Xncas out iref nd 0 sky130_fd_pr__nfet_01v8_lvt W=120 L=0.5 nf=1 m=1

* Low-overdrive cascoded PMOS pull-up
Xpullup ps pb vdd vdd sky130_fd_pr__pfet_01v8_lvt W=400 L=0.5 nf=1 m=2
Xpcas out pcb ps vdd sky130_fd_pr__pfet_01v8_lvt W=400 L=0.5 nf=1 m=2

* Miller compensation
Rcomp stage comp 1800
Ccomp comp out 1.05p
.ends dut
```