"""Compile a bounded component-only DUT; never execute supplied SPICE commands."""
import math
import re

MODELS = {"sky130_fd_pr__nfet_01v8_lvt", "sky130_fd_pr__pfet_01v8_lvt"}
NODE = re.compile(r"(?:0|[a-z][a-z0-9_]{0,31})\Z")
NAME = re.compile(r"[xrc][a-z0-9_]{0,31}\Z")
NUMBER = re.compile(r"([+]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?)(meg|[tgkmunpf])?\Z")
SCALE = {None:1,"t":1e12,"g":1e9,"meg":1e6,"k":1e3,"m":1e-3,"u":1e-6,"n":1e-9,"p":1e-12,"f":1e-15}


class InvalidCircuit(ValueError):
    pass


def number(token, low, high, suffix=True):
    match = NUMBER.fullmatch(token)
    if match is None or (not suffix and match[2] is not None):
        raise InvalidCircuit("Use finite numeric values; no expressions or model directives")
    value = float(match[1])*SCALE[match[2]]
    if not math.isfinite(value) or not low <= value <= high:
        raise InvalidCircuit(f"Component value outside [{low:g}, {high:g}]")
    return value


def compile_dut(text):
    if not isinstance(text,str) or not text or len(text)>30000:
        raise InvalidCircuit("DUT must be nonempty text below 30000 characters")
    lines=[]
    for line in text.splitlines():
        line=line.strip().lower()
        if not line or line.startswith("*"):
            continue
        lines.append(line.split(";",1)[0].strip())
    if len(lines)<3 or lines[0].split()!=[".subckt","dut","iref","inp","inn","out"] or lines[-1].split()!=[".ends","dut"]:
        raise InvalidCircuit("Exactly one .subckt dut iref inp inn out ... .ends dut is required")
    names=set()
    counts={"x":0,"r":0,"c":0}
    output=["* Compiled component-only pilot DUT; no supplied simulator commands.",".subckt dut iref inp inn out"]
    for line in lines[1:-1]:
        tokens=line.split()
        if not tokens or not NAME.fullmatch(tokens[0]):
            raise InvalidCircuit("Only MOS instances, resistors and capacitors are allowed")
        name=tokens[0]
        if name in names:
            raise InvalidCircuit("Duplicate instance name")
        names.add(name)
        typ=name[0]
        counts[typ]+=1
        if counts[typ] > {"x":80,"r":32,"c":32}[typ]:
            raise InvalidCircuit("Component count exceeds the disclosed pilot bound")
        if typ=="x":
            if len(tokens) not in (8,9,10) or tokens[5] not in MODELS or not all(NODE.fullmatch(n) for n in tokens[1:5]):
                raise InvalidCircuit("MOS format: Xname drain gate source bulk MODEL W=... L=... [nf=1] [m=integer]")
            params={}
            for token in tokens[6:]:
                pair=token.split("=")
                if len(pair)!=2 or pair[0] not in ("w","l","nf","m") or pair[0] in params:
                    raise InvalidCircuit("Invalid or duplicate MOS parameter")
                params[pair[0]]=pair[1]
            if not {"w","l"}.issubset(params):
                raise InvalidCircuit("MOS W and L are required in micrometres")
            w=number(params["w"],1,1000,False)
            length=number(params["l"],0.15,10,False)
            nf=number(params.get("nf","1"),1,1,False)
            mult=number(params.get("m","1"),1,100,False)
            if not mult.is_integer():
                raise InvalidCircuit("m must be an integer")
            nmos=tokens[5]=="sky130_fd_pr__nfet_01v8_lvt"
            if nmos and tokens[4]!="0":
                raise InvalidCircuit("NMOS bulk must be 0; no deep-n-well assumptions")
            if not nmos and tokens[4] not in ("vdd",tokens[3]):
                raise InvalidCircuit("PMOS bulk must be vdd or its own source")
            output.append(" ".join(tokens[:6])+f" W={w:.17g} L={length:.17g} nf=1 m={int(mult)}")
        else:
            if len(tokens)!=4 or not all(NODE.fullmatch(n) for n in tokens[1:3]) or tokens[1]==tokens[2]:
                raise InvalidCircuit("R/C format: name node1 node2 positive_value, with distinct nodes")
            bounds=(1,1e7) if typ=="r" else (1e-15,1e-10)
            value=number(tokens[3],*bounds)
            output.append(" ".join(tokens[:3])+f" {value:.17g}")
    if not counts["x"]:
        raise InvalidCircuit("A MOS amplifier is required")
    output.append(".ends dut")
    return "\n".join(output)+"\n",counts
