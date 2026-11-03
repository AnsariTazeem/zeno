# Bounded extension after two baseline full-grid failures

The exact 8.2 pF and 10 pF standard networks have now completed all six cases.
Both fail phase margin for the smallest sensor; the 10 pF network also misses
settling there. Neither is a reference solution. This is a useful warning that
the largest input capacitance screen did not represent all governing cases.

Keep the original plan's physical envelope and every numeric limit unchanged.
Test a single additional resistor from sense to the ideal reference, with the
same 10 kOhm feedback resistance and 8.2 pF feedback capacitance. This raises
input admittance/noise gain and may reduce the unfavorable crossover at the
small-capacitance end. In the ideal virtual-ground limit it draws no DC current
and leaves signal transimpedance at -Rf; finite gain/offset invalidate assuming
perfect cancellation, so actual accuracy, bandwidth and delivered power must
still pass. Resistor noise is an acknowledged added cost. This is a hypothesis,
not a proven repair or a low-noise photodetector claim.

The finite extension screen tests Rg=1000,2000,5000 ohm at both external input
capacitance extremes (10+2 pF and 150+10 pF), AC only: six points. If any value
passes both endpoints, choose the one with the largest minimum endpoint margin
and test all six conditions including full transients. If it passes, confirm
unchanged under refined numerics; if another screened value also passes both
endpoints, verify that as a distinct alternative. Stop this extension if none
passes endpoints or if these selected full-grid references fail. Do not add
more topologies, search indefinitely or change a success threshold.

The existing under/overcompensated controls are still evaluated and retained.
The original plan said not to add a compound network if an ordinary baseline
passed; neither passed, so the observed full-grid failure justifies this
additional component. All earlier inputs and results remain unchanged.
