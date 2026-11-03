"""Bounded R/C compiler adapted from this project's LOAD-P01 compiler."""
import math
import re

class InvalidNetwork(ValueError):
    pass


def compile_network(text):
    if not isinstance(text,str) or len(text.encode('utf-8'))>32768:
        raise InvalidNetwork('Network text too large')
    lines=[x.strip() for x in text.splitlines() if x.strip() and not x.lstrip().startswith('*')]
    if len(lines)<3 or len(lines)>66 or lines[0].lower().split()!=['.subckt','feedback','sense','out','vref'] or lines[-1].lower().split()!=['.ends','feedback']:
        raise InvalidNetwork('Exactly one .subckt feedback sense out vref ... .ends feedback required')
    counts={'R':0,'C':0};names=set();internal=set();ports=set()
    compiled=['.subckt feedback sense out vref']
    number=re.compile(r'[+]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?')
    node=re.compile(r'(?:0|[a-z][a-z0-9_]{0,31})')
    for line in lines[1:-1]:
        t=line.lower().split()
        if len(t)!=4 or not re.fullmatch(r'[rc][a-z0-9_]{0,31}',t[0]):
            raise InvalidNetwork('Only four-token literal R/C component lines permitted')
        if t[0] in names:
            raise InvalidNetwork('Duplicate component name')
        names.add(t[0]);kind=t[0][0].upper();counts[kind]+=1
        if counts[kind]>8:
            raise InvalidNetwork('At most eight resistors and eight capacitors')
        if not number.fullmatch(t[3]):
            raise InvalidNetwork('Values must be literal SI numbers; no suffixes or expressions')
        value=float(t[3]);lo,hi=(1,1e7) if kind=='R' else (1e-15,1e-7)
        if not math.isfinite(value) or not lo<=value<=hi:
            raise InvalidNetwork('Value outside declared bounds')
        mapped=[]
        for n in t[1:3]:
            if not node.fullmatch(n):
                raise InvalidNetwork('Invalid node name')
            if n in ('sense','out','vref','0'):
                mapped.append(n);ports.add(n)
            else:
                internal.add(n);mapped.append('net_'+n)
        if mapped[0]==mapped[1] or len(internal)>16:
            raise InvalidNetwork('Distinct component nodes and at most sixteen private nodes required')
        compiled.append(f'{t[0]} {mapped[0]} {mapped[1]} {value:.17g}')
    if not {'sense','out'}<=ports:
        raise InvalidNetwork('Both sense and out ports must appear; vref is optional')
    compiled.append('.ends feedback')
    return '\n'.join(compiled)+'\n',{**counts,'internal_nodes':len(internal)}
