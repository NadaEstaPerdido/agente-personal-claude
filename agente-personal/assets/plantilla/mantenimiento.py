"""Mantenimiento semanal del agente.

1. Cierre de la semana: revisa qué se movió, actualiza la memoria (y el Cerebro si existe) y resume logros y pendientes.
2. Tareas extra definidas en config.json > mantenimiento.tareas_extra.
3. Reinicia la conversación del bot y manda el resumen por Telegram.
"""
import datetime
import json
import subprocess
import time

import agente as ag

SEMANA = (
    "Es el cierre semanal. Revisa qué se movió en los últimos 7 días en tu carpeta de trabajo (archivos modificados) "
    "y, si tienes conectores de calendario, tareas o correo, lo más importante de esa semana y de la próxima.\n"
    "1. Actualiza la memoria con lo que cambió de fondo (proyectos nuevos, decisiones, preferencias), sin datos sensibles.\n"
    "2. Si existe un Cerebro, actualiza el estado y los pendientes de cada proyecto que se movió y añade una línea a su log.\n"
    "Termina con un resumen de máximo 12 líneas: qué avanzó, qué quedó pendiente y qué vence pronto."
)


def correr(claude, permitidas, prohibidas, prompt, carpeta, minutos):
    cmd = claude + [
        "-p", "--output-format", "json",
        "--permission-mode", "dontAsk",
        "--allowedTools", ",".join(permitidas),
        "--disallowedTools", ",".join(prohibidas),
        "--append-system-prompt", ag.instrucciones(),
    ]
    p = subprocess.run(
        cmd, input=prompt, capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=carpeta, timeout=minutos * 60, creationflags=ag.SIN_VENTANA, env=ag.entorno_claude(),
    )
    try:
        j = json.loads(p.stdout)
    except json.JSONDecodeError:
        return f"no se pudo correr: {(p.stderr or p.stdout or '').strip()[-300:]}", True
    return (j.get("result") or "").strip(), bool(j.get("is_error"))


def main():
    env = ag.cargar_env()
    ag.configurar_log(env)
    token, chat = env.get("TELEGRAM_BOT_TOKEN"), env.get("TELEGRAM_OWNER_ID")
    tg = ag.Telegram(token) if token and chat else None
    claude = ag.comando_claude()
    h = ag.cargar_herramientas()
    config = ag.CFG.get("mantenimiento", {})
    estado = ag.Estado()

    tareas = []
    if config.get("cierre_semanal", True):
        tareas.append(("Cierre de la semana", SEMANA, ag.BASE, [], 30))
    for extra in config.get("tareas_extra", []):
        tareas.append((extra["nombre"], extra["prompt"], ag.Path(extra.get("carpeta") or ag.BASE).expanduser(),
                       extra.get("herramientas_extra", []), int(extra.get("minutos", 60))))

    partes = [f"🗓️ Mantenimiento semanal de {ag.NOMBRE} · {datetime.date.today().strftime('%d/%m/%Y')}"]
    for nombre, prompt, carpeta, extra, minutos in tareas:
        ag.log.info("Mantenimiento: %s", nombre)
        permitidas = h["trabajo"] + extra
        # Una tarea que pide Bash(comando) concreto necesita quitar el bloqueo general de Bash.
        prohibidas = [x for x in h["prohibidas"] if not (x == "Bash" and any(e.startswith("Bash(") for e in extra))]
        inicio = time.time()
        try:
            texto, error = correr(claude, permitidas, prohibidas, prompt, carpeta, minutos)
        except subprocess.TimeoutExpired:
            texto, error = f"se pasó de {minutos} minutos y la detuve", True
        except Exception as e:  # noqa: BLE001
            texto, error = str(e)[:300], True
        ag.log.info("%s terminó en %.0f min (error=%s)", nombre, (time.time() - inicio) / 60, error)
        partes.append(f"\n{'⚠️' if error else '✅'} {nombre}\n{texto}")

    estado.set("sesion", None)
    estado.set("ultima_limpieza", datetime.date.today().isoformat())
    partes.append("\n🧹 Conversación reiniciada: arrancamos limpios.")
    resumen = "\n".join(partes)
    print(resumen)
    if tg:
        try:
            tg.enviar(int(chat), resumen)
        except Exception:  # noqa: BLE001
            ag.log.exception("No pude enviar el resumen por Telegram")


if __name__ == "__main__":
    main()
