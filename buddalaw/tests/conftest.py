"""Configurazione comune dei test BuddaLaw."""
import sys
from pathlib import Path

STRUMENTI = Path(__file__).resolve().parent / "tools"
if str(STRUMENTI) not in sys.path:
    sys.path.insert(0, str(STRUMENTI))


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "sorveglianza: comportamento del server non documentato o anomalo; "
        "se cambia, il test diventa rosso per far rivedere la skill",
    )


def pytest_terminal_summary(terminalreporter):
    """Al termine del livello C stampa numero di chiamate e costo totale."""
    modulo = sys.modules.get("chiama_mcp")
    if not modulo or not getattr(modulo, "REGISTRO", None):
        return
    reg = modulo.REGISTRO
    totale = sum(r["costo_usd"] for r in reg)
    terminalreporter.write_sep("-", "BuddaLaw livello C")
    for r in reg:
        terminalreporter.write_line(f"  {r['tool']:<22} {r['costo_usd']:.4f} $")
    terminalreporter.write_line(f"  chiamate: {len(reg)}  costo totale: {totale:.4f} $")
