Proposal 1 passed bandwidth and phase margin, but failed DC gain, gain margin, and rising settling. Proposal 2 adds cascodes to both sides of the input stage to increase its output resistance. A shorter PMOS mirror and increased compensation capacitance target stability. These changes have not yet been simulated.

```spice
.subckt dut iref inp inn out
* Reference and cascode biases
Rref iref nb 22500
Xref nb nb 0 0 sky130_fd_pr__nfet_01v8_lvt W=40 L=1 nf=1 m=1
Rpc1 nb pc 1meg
Rpc2 pc 0 1meg

* Translate the reference into a PMOS bias
Xbias pb nb 0 0 sky130_fd_pr__nfet_01v8_lvt W=20 L=1 nf=1 m=1
Xpb pb pb vdd vdd sky130_fd_pr__pfet_01v8_lvt W=20 L=1 nf=1 m=1

* NMOS differential pair and tail
Xtail tail nb 0 0 sky130_fd_pr__nfet_01v8_lvt W=120 L=1 nf=1 m=1
Xin_p ndp inp tail 0 sky130_fd_pr__nfet_01v8_lvt W=30 L=1.5 nf=1 m=1
Xin_n ndn inn tail 0 sky130_fd_pr__nfet_01v8_lvt W=30 L=1.5 nf=1 m=1

* NMOS cascodes
Xnc_p stage iref ndp 0 sky130_fd_pr__nfet_01v8_lvt W=40 L=0.3 nf=1 m=1
Xnc_n mirror iref ndn 0 sky130_fd_pr__nfet_01v8_lvt W=40 L=0.3 nf=1 m=1

* Cascoded PMOS mirror load
Xload_ref pr mirror vdd vdd sky130_fd_pr__pfet_01v8_lvt W=30 L=0.6 nf=1 m=1
Xload_out po mirror vdd vdd sky130_fd_pr__pfet_01v8_lvt W=30 L=0.6 nf=1 m=1
Xpc_ref mirror pc pr vdd sky130_fd_pr__pfet_01v8_lvt W=40 L=0.5 nf=1 m=1
Xpc_out stage pc po vdd sky130_fd_pr__pfet_01v8_lvt W=40 L=0.5 nf=1 m=1

* Output stage
Xdrive out stage 0 0 sky130_fd_pr__nfet_01v8_lvt W=100 L=1 nf=1 m=1
Xpullup out pb vdd vdd sky130_fd_pr__pfet_01v8_lvt W=270 L=1 nf=1 m=1

* Series-resistor Miller compensation
Rcomp stage comp 2400
Ccomp comp out 1p
.ends dut
```