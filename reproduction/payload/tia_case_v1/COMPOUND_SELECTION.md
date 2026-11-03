# Reference selection after the bounded Rg screen

All three Rg values pass the endpoint AC screen. Per EXTENSION_01.md, choose
Rg=1000 ohm as the main candidate: it gives the largest minimum endpoint phase
margin (about 70.308 degrees, versus 62.568 for 2000 and 55.920 for 5000).
Choose Rg=2000 ohm as the distinct alternative because it also passes both
endpoints with more margin than 5000. Both retain Rf=10000 ohm and Cf=8.2 pF.
Now test those two unchanged networks through the compiler at all six
conditions and full transients. Only an actual all-check pass is a reference.

Before freezing any model task, an additional adversarial trace exposed a
measurement coverage weakness: overshoot was inspected only after the 5 ns
source ramp completed, although the plan did not exempt early peaks. Extend
that check to the full edge window, preserve the earlier apparatus code and
fixtures, and re-extract earlier raw traces separately at closure. No model
has received this provisional task and no original scored model trial changes.
The physical conditions, stated limits and passing-circuit search are unchanged.

This extension's extra resistor has a noise cost. Noise performance and a
physical reference buffer are outside the current task's measured envelope;
the case cannot be sold as a complete optical receiver or low-noise design.
