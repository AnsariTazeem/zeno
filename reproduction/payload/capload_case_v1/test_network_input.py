"""Accept equivalent passive circuits; reject executable input before ngspice."""
from pathlib import Path
from network_input import InvalidNetwork,compile_network

BASE=Path(__file__).resolve().parent
for name in ('reference','alternative'):
    compiled,counts=compile_network((BASE/f'private/{name}.sp').read_text())
    assert counts['R']==3 and counts['C']==0
    assert compile_network(compiled)==(compiled,counts)
valid='.subckt feedback drive load fb\nRloadpath drive load 1000\nRfeedback drive fb 1000\nRground fb 0 100000\n.ends feedback\n'
compile_network(valid)
compile_network('.subckt feedback drive load fb\nRg fb 0 100000\nRf drive fb 1000\nRi drive load 1000\n.ends feedback')
private='.subckt feedback drive load fb\nR1 drive vdd 1000\nR2 vdd load 1\nR3 drive fb 1\n.ends feedback'
assert 'net_vdd' in compile_network(private)[0]  # Does not bind the global supply.
bad=[valid.replace('Rground fb 0 100000',x) for x in (
    '.include secret.sp','.control','V1 fb 0 0.9','B1 fb 0 v=1','L1 fb 0 1e-6',
    'Rground fb 0 {10*10000}','Rground fb 0 100k','Rground fb 0 nan','Rground fb 0 1e999',
    'Rground fb 0 -1','Rground fb 0 0','Rground fb 0 1e8','Cground fb 0 1',
    'Rground fb 0 100000 extra','Rloadpath fb 0 100000','Rground fb ../secret 100000')]
bad += [valid+'\n.end\n',valid.replace('.ends feedback','.ends other'),valid.replace('.subckt feedback drive load fb','.subckt feedback drive load fb vdd')]
for text in bad:
    try:compile_network(text)
    except InvalidNetwork:pass
    else:raise AssertionError('Accepted invalid network')
print('Equivalent valid circuits and private-node isolation accepted;',len(bad),'unsafe/invalid cases rejected without simulation.')
