"""Lista las herramientas de conectores (MCP) tal como las verá el agente en modo headless.

Los nombres cambian según dónde corra Claude (la app de escritorio usa otros prefijos), por eso se
preguntan al mismo `claude -p` que usará el bot.

  python listar_herramientas.py --agente <carpeta del agente>
Guarda <agente>/herramientas_disponibles.json y muestra el estado de cada conector.
"""
import argparse
import json
import os
import re
import subprocess
from pathlib import Path

PROMPT = (
    "Devuelve SOLO un arreglo JSON con los nombres exactos de TODAS las herramientas cuyo nombre empieza por "
    "\"mcp__\" que tienes disponibles, incluidas las diferidas que solo conoces por nombre. "
    "Sin explicación, sin bloque de código, sin nada más."
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agente", required=True)
    args = ap.parse_args()
    agente = Path(args.agente).expanduser()
    cfg = json.loads((agente / "config.json").read_text(encoding="utf-8"))
    claude = cfg["claude"]
    trabajo = Path(cfg["carpeta_trabajo"]).expanduser()
    sin_ventana = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    entorno = dict(os.environ)
    entorno.pop("CLAUDECODE", None)

    print("Estado de los conectores:")
    estado = subprocess.run(claude + ["mcp", "list"], capture_output=True, text=True, encoding="utf-8",
                            errors="replace", cwd=trabajo, timeout=180, creationflags=sin_ventana, env=entorno)
    for linea in estado.stdout.splitlines():
        if ":" in linea and ("✔" in linea or "✘" in linea or "!" in linea):
            print("  " + re.sub(r"(PASSWORD|TOKEN|KEY)=\S+", r"\1=***", linea))

    p = subprocess.run(claude + ["-p", "--output-format", "json", "--permission-mode", "dontAsk"], input=PROMPT,
                       capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=trabajo,
                       timeout=300, creationflags=sin_ventana, env=entorno)
    resultado = json.loads(p.stdout).get("result", "")
    m = re.search(r"\[.*\]", resultado, re.S)
    nombres = sorted(set(json.loads(m.group(0)))) if m else []
    nombres = [n for n in nombres if isinstance(n, str) and n.startswith("mcp__")]
    (agente / "herramientas_disponibles.json").write_text(json.dumps(nombres, indent=2), encoding="utf-8")

    por_servidor = {}
    for n in nombres:
        por_servidor.setdefault(n.split("__")[1], 0)
        por_servidor[n.split("__")[1]] += 1
    print(f"\n{len(nombres)} herramientas de conectores:")
    for s, c in sorted(por_servidor.items()):
        print(f"  {s}: {c}")
    if not nombres:
        print("  (ninguna: revisa que los conectores estén autorizados y conectados)")


if __name__ == "__main__":
    main()
