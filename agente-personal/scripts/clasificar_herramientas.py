"""Clasifica las herramientas de los conectores en consulta, trabajo o prohibidas.

Reglas (primero gana prohibida):
  prohibida  enviar, responder, reenviar, borrar, compartir, publicar, invitar, pagar, ejecutar... o desconocida
  consulta   leer, listar, buscar, obtener... y los borradores de correo (no salen de la bandeja)
  trabajo    crear, editar, mover, etiquetar, subir, completar...
Lo desconocido va a prohibidas y se marca en "_revisar" para decidirlo con la persona.

  python clasificar_herramientas.py --agente <carpeta> [--servidores gmail,nextcloud]
"""
import argparse
import json
import re
from pathlib import Path

# Verbos que siempre bloquean.
PROHIBIDAS = {
    "send", "reply", "forward", "delete", "trash", "destroy", "purge", "erase", "wipe", "unshare",
    "publish", "invite", "react", "spam", "pay", "purchase", "buy", "checkout", "transfer", "refund", "charge",
    "execute", "exec", "run", "deploy", "shell", "bulk", "manage", "broadcast", "empty", "revoke",
    "subscribe", "unsubscribe",
}
# Sustantivos delicados: bloquean salvo que la herramienta solo lea (listar enlaces compartidos está bien; crearlos no).
DELICADAS = {
    "share", "shared", "post", "meeting", "participant", "participants", "member", "members", "permission",
    "permissions", "public", "order", "invoice", "payment", "call", "sms", "conversation", "reaction", "link",
}
LECTURA = {
    "get", "list", "search", "find", "read", "fetch", "query", "describe", "view", "show", "check", "count",
    "download", "preview", "status", "lookup", "retrieve", "browse", "info", "health", "availability", "export",
}
ESCRITURA = {
    "create", "update", "add", "edit", "write", "set", "move", "copy", "rename", "upload", "assign", "unassign",
    "label", "unlabel", "mark", "unmark", "complete", "restore", "archive", "unarchive", "reorder", "tag", "comment",
    "attach", "import", "insert", "append", "modify", "save", "apply", "remove", "untrash", "star", "unstar",
    "pin", "unpin", "schedule", "duplicate", "mkdir", "draft",
}
REVISAR_SI = {"remove", "archive", "schedule", "untrash"}


def palabras(nombre):
    corto = nombre.split("__", 2)[-1]
    corto = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", corto)
    return [p for p in re.split(r"[_\-\s.]+", corto.lower()) if p]


def clasificar(nombre):
    p = palabras(nombre)
    if PROHIBIDAS & set(p):
        return "prohibidas", None
    # El primer verbo reconocible decide (los nombres suelen ir "servicio_verbo_objeto": deck_get_label).
    verbo = next((x for x in p if x in LECTURA or x in ESCRITURA), None)
    if DELICADAS & set(p) and verbo not in LECTURA:
        return "prohibidas", None
    if "draft" in p or "drafts" in p:
        return "consulta", None
    if verbo in LECTURA:
        return "consulta", None
    if verbo in ESCRITURA:
        return "trabajo_extra", ("revisar" if REVISAR_SI & set(p) else None)
    return "prohibidas", "desconocida"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agente", required=True)
    ap.add_argument("--servidores", default="", help="solo estos servidores (parte del nombre, separados por coma)")
    args = ap.parse_args()
    agente = Path(args.agente).expanduser()
    disponibles = json.loads((agente / "herramientas_disponibles.json").read_text(encoding="utf-8"))
    filtros = [s.strip().lower() for s in args.servidores.split(",") if s.strip()]

    salida = {"consulta": [], "trabajo_extra": [], "prohibidas": [], "_revisar": []}
    for nombre in disponibles:
        servidor = nombre.split("__")[1].lower() if nombre.count("__") >= 2 else ""
        if filtros and not any(f in servidor for f in filtros):
            continue
        grupo, nota = clasificar(nombre)
        salida[grupo].append(nombre)
        if nota:
            salida["_revisar"].append(f"{nombre} → {grupo} ({nota})")

    (agente / "herramientas.json").write_text(json.dumps(salida, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"consulta: {len(salida['consulta'])} · trabajo: {len(salida['trabajo_extra'])} · prohibidas: {len(salida['prohibidas'])}")
    if salida["_revisar"]:
        print("\nPara revisar con la persona:")
        for r in salida["_revisar"]:
            print("  " + r)


if __name__ == "__main__":
    main()
