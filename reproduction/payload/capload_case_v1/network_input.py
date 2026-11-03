"""Restricted passive-network language; reconstruct rather than execute raw text."""
import math
import re

class InvalidNetwork(ValueError):pass

def compile_network(text):
    if not isinstance(text,str) or len(text.encode('utf-8'))>32768:
        raise InvalidNetwork('Network text too large')
    lines=[x.strip() for x in text.splitlines() if x.strip() and not x.lstrip().startswith('*')]
    if len(lines)<3 or len(lines)>66 or lines[0].lower().split()!=['.subckt','feedback','drive','load','fb'] or lines[-1].lower().split()!=['.ends','feedback']:
        raise InvalidNetwork('Exactly one .subckt feedback drive load fb ... .ends feedback is required')
    counts={'R':0,'C':0};names=set();internal=set();ports=set();compiled=['.subckt feedback drive load fb']
    number=re.compile(r'[+]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?')
    node=re.compile(r'(?:0|[a-z][a-z0-9_]*)')
    for line in lines[1:-1]:
        t=line.lower().split()
        if len(t)!=4 or not re.fullmatch(r'[rc][a-z0-9_]*',t[0]):
            raise InvalidNetwork('Only four-token literal R/C component lines are permitted')
        if t[0] in names:raise InvalidNetwork('Duplicate component name')
        names.add(t[0]);kind=t[0][0].upper();counts[kind]+=1
        if counts[kind]>8:raise InvalidNetwork('At most eight resistors and eight capacitors')
        if not number.fullmatch(t[3]):raise InvalidNetwork('Values must be literal SI numbers without suffixes or expressions')
        value=float(t[3]);lo,hi=(1,1e7) if kind=='R' else (1e-15,1e-7)
        if not math.isfinite(value) or not lo<=value<=hi:raise InvalidNetwork('Component value outside declared limits')
        mapped=[]
        for n in t[1:3]:
            if not node.fullmatch(n):raise InvalidNetwork('Invalid node name')
            if n in ('drive','load','fb','0'):
                mapped.append(n);ports.add(n)
            else:
                internal.add(n);mapped.append('net_'+n)
        if len(internal)>16:raise InvalidNetwork('At most sixteen internal nodes')
        compiled.append(f'{t[0]} {mapped[0]} {mapped[1]} {value:.17g}')
    if not {'drive','load','fb'}<=ports:raise InvalidNetwork('All three interface ports must appear')
    compiled.append('.ends feedback')
    return '\n'.join(compiled)+'\n',{**counts,'internal_nodes':len(internal)}
