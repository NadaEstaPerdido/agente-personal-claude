"""Crea (o actualiza) la carpeta del agente a partir de las respuestas del onboarding.

  python crear_agente.py --respuestas respuestas.json --destino <carpeta del agente> [--instalar-dependencias]
  python crear_agente.py --destino <carpeta del agente> --actualizar     solo reemplaza el código, conserva config y secretos

respuestas.json tiene la forma de assets/config.ejemplo.json.
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
PLANTILLA = SKILL / "assets" / "plantilla"
CODIGO = ["agente.py", "entregas.py", "mantenimiento.py", "configurar.py", "servicio.py", "requirements.txt"]

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verificar_entorno import buscar_claude  # noqa: E402

DEFECTOS = {
    "idioma": "español",
    "max_lineas": 15,
    "conectores": [],
    "archivos": {"lectura": "carpeta"},
    "computadores": 1,
    "voz": {"activa": True, "modelo": "small", "idioma": "es"},
    "entregas": {"destino": "local"},
    "memoria": {"tipo": "simple", "archivo": "MEMORIA.md", "cerebro": "Cerebro"},
    "mantenimiento": {"activo": True, "dia": "domingo", "hora": "20:00", "cierre_semanal": True, "tareas_extra": []},
    "limites": {"consulta_min": 20, "trabajo_min": 45},
    "instrucciones_extra": "",
}


def mezclar(base, nuevo):
    salida = dict(base)
    for k, v in nuevo.items():
        salida[k] = mezclar(base[k], v) if isinstance(v, dict) and isinstance(base.get(k), dict) else v
    return salida


def dentro(hijo, padre):
    hijo, padre = hijo.resolve(), padre.resolve()
    return hijo == padre or padre in hijo.parents


def escribir_si_falta(ruta, texto):
    if not ruta.exists():
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(texto, encoding="utf-8")
        print(f"  creado {ruta}")


def preparar_carpeta_trabajo(cfg):
    base = Path(cfg["carpeta_trabajo"]).expanduser()
    base.mkdir(parents=True, exist_ok=True)
    nombre, dueno = cfg["asistente"]["nombre"], cfg["dueno"]["nombre"]
    memoria = cfg["memoria"]
    trato = "de tú" if cfg["dueno"].get("trato") != "usted" else "de usted"
    escribir_si_falta(base / "CLAUDE.md", (
        f"# Carpeta de trabajo de {dueno}\n"
        f"- Aquí trabaja {nombre}, su asistente personal. Trátalo {trato}; responde en {cfg['idioma']}.\n"
        f"- Lo que sabemos de {dueno}: @{memoria['archivo']}\n"
        + (f"- Índice de proyectos y en qué computador está cada cosa: `{memoria['cerebro']}/index.md`.\n"
           if memoria["tipo"] == "cerebro" else "")
        + "- Datos sensibles (documentos de identidad, cuentas, contraseñas) nunca van en la memoria.\n"
    ))
    escribir_si_falta(base / memoria["archivo"], (
        f"# Memoria de {dueno}\n"
        f"- Nombre: {dueno}. Trato: {trato}.\n"
        "- (Aquí se van guardando preferencias y datos útiles cuando se le dice «recuerda...».)\n"
    ))
    if memoria["tipo"] == "cerebro":
        cerebro = base / memoria["cerebro"]
        escribir_si_falta(cerebro / "index.md", (
            "# Índice\n## Proyectos\n(una línea por proyecto: [[Nombre]] · computador · carpeta · estado)\n"
            "## Personas y organizaciones\n## Decisiones\n"
        ))
        escribir_si_falta(cerebro / "log.md", "# Bitácora\n")
        for sub in ("01 Proyectos", "02 Personas y organizaciones", "03 Decisiones y aprendizajes"):
            (cerebro / sub).mkdir(parents=True, exist_ok=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--respuestas")
    ap.add_argument("--destino", required=True)
    ap.add_argument("--actualizar", action="store_true")
    ap.add_argument("--instalar-dependencias", action="store_true")
    args = ap.parse_args()
    destino = Path(args.destino).expanduser()

    if args.actualizar:
        if not (destino / "config.json").exists():
            raise SystemExit("No hay un agente en esa carpeta.")
        for f in CODIGO:
            shutil.copy2(PLANTILLA / f, destino / f)
        print(f"Código actualizado en {destino}. Reinicia el bot: python servicio.py reiniciar")
        return

    if not args.respuestas:
        raise SystemExit("Falta --respuestas")
    respuestas = json.loads(Path(args.respuestas).read_text(encoding="utf-8"))
    cfg = mezclar(DEFECTOS, respuestas)
    for campo in (("asistente", "nombre"), ("dueno", "nombre")):
        if not cfg.get(campo[0], {}).get(campo[1]):
            raise SystemExit(f"Falta {'.'.join(campo)} en las respuestas")
    if not cfg.get("carpeta_trabajo"):
        raise SystemExit("Falta carpeta_trabajo en las respuestas")
    trabajo = Path(cfg["carpeta_trabajo"]).expanduser()
    if dentro(destino, trabajo):
        raise SystemExit("La carpeta del agente no puede estar dentro de la carpeta de trabajo: ahí el agente podría leer sus propios secretos.")

    claude = buscar_claude()
    if not claude:
        raise SystemExit("No encuentro Claude Code. Instálalo antes de crear el agente.")
    cfg["claude"] = claude

    destino.mkdir(parents=True, exist_ok=True)
    for f in CODIGO:
        shutil.copy2(PLANTILLA / f, destino / f)
    (destino / "config.json").write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")
    escribir_si_falta(destino / "herramientas.json", json.dumps(
        {"consulta": [], "trabajo_extra": [], "prohibidas": []}, indent=2))
    for sub in ("logs", "guias"):
        (destino / sub).mkdir(exist_ok=True)
    (trabajo / "_entregas").mkdir(parents=True, exist_ok=True)
    print(f"Agente creado en {destino}")
    preparar_carpeta_trabajo(cfg)

    if args.instalar_dependencias:
        paquetes = [l.strip() for l in (destino / "requirements.txt").read_text().splitlines() if l.strip()]
        if not cfg["voz"].get("activa", True):
            paquetes = [p for p in paquetes if not p.startswith("faster-whisper")]
        print("Instalando dependencias:", " ".join(paquetes))
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", *paquetes], check=True)
    print("Siguiente: listar y clasificar herramientas, luego python configurar.py en la terminal de la persona.")


if __name__ == "__main__":
    main()
