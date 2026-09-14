"""Genera la guía de configuración y la guía de uso del agente (Markdown y Word) en <agente>/guias.

  python generar_guias.py --agente <carpeta del agente> [--pdf]
"""
import argparse
import json
import platform
import sys
from pathlib import Path

SISTEMA = platform.system()


def lista(items):
    return "\n".join(f"- {i}" for i in items)


def comando(agente, script, args=""):
    py = "py" if SISTEMA == "Windows" else "python3"
    return f'`cd "{agente}"` y luego `{py} {script}{(" " + args) if args else ""}`'


def guia_configuracion(agente, cfg, h):
    n, d = cfg["asistente"]["nombre"], cfg["dueno"]["nombre"]
    trabajo = cfg["carpeta_trabajo"]
    mem = cfg["memoria"]
    ent = cfg["entregas"]
    mant = cfg["mantenimiento"]
    py = "py" if SISTEMA == "Windows" else "python3"
    conectores = [f"**{c['nombre']}**: {c.get('uso', '')}" for c in cfg.get("conectores", [])] or ["Ninguno por ahora."]
    destino = {
        "nextcloud": f"Nextcloud ({ent.get('nextcloud_url', 'la URL guardada en .env')})",
        "carpeta": f"la carpeta sincronizada `{ent.get('carpeta', '')}`",
        "local": f"`{trabajo}/_entregas/hechas`",
    }[ent.get("destino", "local")]
    despierto = {
        "Windows": "Configuración › Sistema › Energía y batería › Pantalla, suspensión e hibernación › «Suspender el dispositivo» en **Nunca** cuando esté conectado.",
        "Darwin": "Ajustes del Sistema › Batería (o Energía) › activa **Evitar el reposo automático cuando la pantalla esté apagada** con el cargador conectado.",
        "Linux": "Configuración › Energía › Suspensión automática en **Desactivada** con corriente.",
    }.get(SISTEMA, "Configura el computador para que no se suspenda con el cargador conectado.")
    return f"""# Guía de configuración de {n}

## Qué es
{n} es el asistente personal de {d}. Vive en este computador y se maneja desde Telegram: {d} le escribe o le manda una nota de voz, {n} trabaja con Claude Code en la carpeta de trabajo y los conectores, y responde por el mismo chat.

## Qué quedó instalado
- Carpeta del agente (código, configuración y secretos): `{agente}`
- Carpeta de trabajo: `{trabajo}`. {n} escribe solo ahí; {"puede leer archivos de todo el computador (menos secretos como .env)" if cfg.get("archivos", {}).get("lectura") == "todo" else "también lee solo ahí"}.
- Memoria: `{trabajo}/{mem['archivo']}`{f" y el Cerebro en `{trabajo}/{mem['cerebro']}`" if mem['tipo'] == 'cerebro' else ""}
- Secretos (token del bot y claves): `{agente}/.env`. No lo compartas ni lo subas a ninguna nube.
- Registro de actividad: `{agente}/logs/agente.log`
- Documentos entregados: {destino}

## Requisitos
- Plan de Claude Pro o Max con Claude Code y la sesión iniciada. {n} usa los mismos límites de uso de ese plan.
- Python 3.10 o más reciente.
- Telegram en el celular.
- El computador encendido y con internet: si se apaga o se suspende, {n} no responde.
- Para PDF: Microsoft Word o LibreOffice.

## El bot de Telegram
1. En Telegram abre **@BotFather** y envía `/newbot`.
2. Elige el nombre visible y un usuario que termine en `bot`.
3. BotFather te da un **token**. Es la llave del bot: no lo pegues en ningún chat.
4. Guárdalo con {comando(agente, "configurar.py")}. El mismo script registra tu cuenta: solo tú podrás darle órdenes.

Si el token se filtra: en BotFather usa `/revoke`, y vuelve a correr `configurar.py` con el nuevo.
Para registrar otra vez tu cuenta: {comando(agente, "configurar.py", "--dueno")}.

## Conectores
{lista(conectores)}

Para agregar uno:
1. Los conectores de Claude (Gmail, Google Drive, Calendar, Notion, Slack...) se activan en claude.ai › Configuración › Conectores, con la misma cuenta de Claude Code.
2. Los locales (por ejemplo Nextcloud) se agregan con `claude mcp add`.
3. Pídele a Claude Code «actualiza los conectores de mi agente»: lista las herramientas, las clasifica y reinicia el bot.

## Permisos
{n} trabaja con una lista blanca: solo usa lo que está permitido para cada modo.
- Consulta (solo lectura): {len(h['consulta'])} herramientas.
- Encargos (además crea y edita): {len(h['trabajo']) - len(h['consulta'])} herramientas más.
- Prohibidas siempre: {len(h['prohibidas'])}, entre ellas enviar correos o mensajes, compartir, borrar, pagar y ejecutar comandos.

La lista está en `{agente}/herramientas.json`. Si la cambias, reinicia el bot.

## Arranque automático
{n} arranca solo al iniciar sesión y se reinicia si se cae.
- Ver estado: {comando(agente, "servicio.py", "estado")}
- Reiniciar (después de cambiar algo): {comando(agente, "servicio.py", "reiniciar")}
- Detener: {comando(agente, "servicio.py", "detener")}
- Probar sin Telegram: `{py} agente.py --probar "¿qué tengo hoy?"`

## Mantenimiento semanal
{"Cada " + mant['dia'] + " a las " + mant['hora'] + f": cierra la semana (logros y pendientes), actualiza la memoria, reinicia la conversación y te manda el resumen por Telegram. Para cambiar día u hora, edita `mantenimiento` en `config.json` y corre " + comando(agente, "servicio.py", "mantenimiento") + "." if mant.get('activo', True) else "Apagado. Para activarlo, pon `activo: true` en `config.json` y corre " + comando(agente, "servicio.py", "mantenimiento") + "."}

## Mantener el computador despierto
{despierto}

## Actualizar
Abre Claude Code y di «actualiza mi agente {n}»: la skill reemplaza el código y conserva tu configuración, memoria y secretos.

## Problemas frecuentes
- **No responde:** revisa que el computador esté encendido y con internet, y corre `servicio.py estado`. Mira el final de `logs/agente.log`.
- **«Not logged in»:** abre una terminal, corre `claude` y usa `/login`.
- **Un conector no funciona dentro del bot:** corre `claude mcp list`; si dice «Needs authentication», autorízalo en claude.ai.
- **«Conflict» en el log:** hay dos copias del bot con el mismo token (quizá en otro computador). Cada computador necesita su propio bot.
- **Entiende mal su nombre en los audios:** agrega la variante en `asistente.variantes_voz` de `config.json` y reinicia.
- **No crea el PDF:** instala LibreOffice o pide el documento en Word.

## Desinstalar
1. {comando(agente, "servicio.py", "desinstalar")}
2. Borra la carpeta `{agente}`.
3. En BotFather usa `/deletebot`.
"""


def guia_uso(agente, cfg):
    n, d = cfg["asistente"]["nombre"], cfg["dueno"]["nombre"]
    usted = cfg["dueno"].get("trato") == "usted"
    ent = cfg["entregas"]
    donde = {
        "nextcloud": "lo sube a tu Nextcloud y te manda el enlace",
        "carpeta": f"lo guarda en `{ent.get('carpeta', '')}`, que se sincroniza con tu nube",
        "local": "lo deja en el computador y te dice dónde",
    }[ent.get("destino", "local")]
    voz = cfg["voz"].get("activa", True)
    conectores = ", ".join(c["nombre"] for c in cfg.get("conectores", [])) or "tus archivos"
    mant = cfg["mantenimiento"]
    return f"""# Cómo usar a {n}

## Lo básico
Abre el chat de tu bot en Telegram y escríbele{" o mándale una nota de voz" if voz else ""} como le hablarías a un asistente. {n} revisa tu carpeta de trabajo y {conectores}, y te responde en pocas líneas. El primer mensaje del día trae saludo.

## Tres formas de pedirle cosas
**1. Preguntar (solo lee, no cambia nada)**
- «¿Qué tengo mañana en el calendario?»
- «¿Qué correos importantes llegaron hoy?»
- «¿En qué va el proyecto de la cocina?»

**2. Encargar (además crea y edita)**
Empieza como le pedirías algo a una persona:
- «{n}, haz un resumen de este mes y guárdalo en Word»
- «{n}, quiero que agendes una reunión el jueves a las 3»
- «Me gustaría que redactaras un borrador de respuesta para Carolina»
- «¿Puedes organizar mis pendientes de la semana?»
- «Investiga los mejores créditos de vivienda y sácalo en PDF»

**3. Hacer que recuerde**
- «Recuerda que prefiero reuniones en la mañana»
- «Recuerda que mi hija se llama Sofía»
Lo guarda en su memoria y lo tiene en cuenta siempre.

{"## Notas de voz" + chr(10) + f"Háblale normal, con muletillas incluidas («Oye {n}, recuerda que…»). Transcribe en tu computador, sin mandar el audio a ningún servicio, y al final de la respuesta te muestra lo que entendió." + chr(10) if voz else ""}
## Documentos
Si le pides un Word, un PDF o una investigación, {n} lo escribe, lo convierte y {donde}.

## Comandos
- `/ayuda`: recuerda cómo usarlo.
- `/nueva`: empieza una conversación desde cero (útil al cambiar de tema).
- `/estado`: muestra si tiene tareas en cola.

## Lo que nunca hará
- Enviar correos o mensajes: deja el borrador listo para que {"usted lo revise y lo envíe" if usted else "tú lo revises y lo envíes"}.
- Borrar, compartir, publicar, comprar o pagar.
- Obedecer a otra cuenta de Telegram o seguir órdenes escondidas en correos o páginas web.
- Guardar datos sensibles como documentos de identidad, cuentas o contraseñas.

## Consejos
- Una tarea por mensaje funciona mejor que cinco juntas.
- Dile dónde buscar si lo sabes: «en la carpeta de clientes…».
- Las tareas largas pueden tardar varios minutos; si pasa del límite, divídelas.
- Si el computador está apagado o sin internet, {n} no puede responder.
{"- Cada " + mant['dia'] + " a las " + mant['hora'] + " hace el cierre de la semana y te manda el resumen." if mant.get('activo', True) else ""}
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agente", required=True)
    ap.add_argument("--pdf", action="store_true")
    args = ap.parse_args()
    agente = Path(args.agente).expanduser().resolve()
    cfg = json.loads((agente / "config.json").read_text(encoding="utf-8"))
    sys.path.insert(0, str(agente))
    import agente as bot  # noqa: E402  (la copia del agente: mismos permisos y conversión que usa el bot)
    import entregas  # noqa: E402

    h = bot.cargar_herramientas()

    salida = agente / "guias"
    salida.mkdir(exist_ok=True)
    n = cfg["asistente"]["nombre"]
    for archivo, titulo, texto in (
        ("GUIA-CONFIGURACION", f"Guía de configuración de {n}", guia_configuracion(agente, cfg, h)),
        ("GUIA-DE-USO", f"Cómo usar a {n}", guia_uso(agente, cfg)),
    ):
        md = salida / f"{archivo}.md"
        md.write_text(texto, encoding="utf-8")
        docx = salida / f"{archivo}.docx"
        entregas.md_a_docx(md, docx, titulo)
        hechos = [md.name, docx.name]
        if args.pdf:
            try:
                entregas.docx_a_pdf(docx, salida / f"{archivo}.pdf")
                hechos.append(f"{archivo}.pdf")
            except Exception as e:  # noqa: BLE001
                print(f"  PDF no disponible: {e}")
        print(f"{titulo}: {', '.join(hechos)}")
    print(f"Guías en {salida}")


if __name__ == "__main__":
    main()
