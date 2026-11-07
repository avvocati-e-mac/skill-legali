"""Validazione delle chiamate contro la fixture reale, senza dipendenze esterne."""
from __future__ import annotations
import json
import re
from pathlib import Path

SCHEMA = json.loads((Path(__file__).resolve().parents[1] / "fixtures/tool_schema.json").read_text())
TOOLS = {t["name"]: t for t in SCHEMA["tools"]}

_TIPI = {
    "string": lambda v: isinstance(v, str),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
    "array": lambda v: isinstance(v, list),
    "object": lambda v: isinstance(v, dict),
    "null": lambda v: v is None,
}


def _tipi_ammessi(spec: dict) -> set[str]:
    if "type" in spec:
        t = spec["type"]
        return set(t) if isinstance(t, list) else {t}
    return {a.get("type") for a in spec.get("anyOf", []) if a.get("type")}


def enum_di(tool: str, param: str) -> list[str] | None:
    """Valori ammessi: dal campo enum o dalla frase «Valori: a, b, c.» della description."""
    spec = TOOLS[tool]["parameters"]["properties"][param]
    if spec.get("enum"):
        return list(spec["enum"])
    m = re.search(r"Valori:\s*(.+?)\.(?:\s|$)", spec.get("description") or "")
    return [v.strip() for v in m.group(1).split(",")] if m else None


def _limiti(spec: dict) -> tuple[float, float] | None:
    m = re.search(r"\((\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\)", spec.get("description") or "")
    return (float(m.group(1)), float(m.group(2))) if m else None


def errori_chiamata(tool: str, argomenti: dict) -> list[str]:
    if tool not in TOOLS:
        return [f"tool inesistente: {tool!r}"]
    schema = TOOLS[tool]["parameters"]
    props = schema.get("properties", {})
    errori = []
    for p in schema.get("required", []):
        if p not in argomenti:
            errori.append(f"{tool}: manca il parametro obbligatorio {p!r}")
    for nome, valore in argomenti.items():
        if nome not in props:
            errori.append(f"{tool}: parametro inesistente {nome!r} (ammessi: {sorted(props)})")
            continue
        spec = props[nome]
        ammessi = _tipi_ammessi(spec)
        if ammessi and not any(_TIPI[t](valore) for t in ammessi if t in _TIPI):
            errori.append(f"{tool}.{nome}={valore!r}: tipo {type(valore).__name__}, ammessi {sorted(ammessi)}")
        valori = enum_di(tool, nome)
        if valori and isinstance(valore, str) and valore not in valori:
            errori.append(f"{tool}.{nome}={valore!r}: non è fra {valori}")
        lim = _limiti(spec)
        if lim and _TIPI["number"](valore) and not (lim[0] <= valore <= lim[1]):
            errori.append(f"{tool}.{nome}={valore!r}: fuori dall'intervallo {lim}")
        if isinstance(valore, list):
            for a in spec.get("anyOf", []) + [spec]:
                tipo_el = (a.get("items") or {}).get("type")
                if tipo_el and not all(_TIPI[tipo_el](x) for x in valore):
                    errori.append(f"{tool}.{nome}: elementi non di tipo {tipo_el}")
    return errori
