---
name: agente-personal
description: Arma, paso a paso y con preguntas, un agente personal propio que se maneja desde Telegram (texto y notas de voz) y pone a trabajar a Claude Code en el computador de la persona, con conectores (Gmail, Google Drive, Calendar, Microsoft 365, Notion, Nextcloud...), memoria, entregas en Word/PDF, arranque automático, mantenimiento semanal y permisos seguros; al final genera la guía de configuración y la guía de uso. Úsala siempre que alguien quiera "mi propio agente", "un asistente que me responda por Telegram", "hablarle a Claude desde el celular", "una alternativa a OpenClaw", "un bot que trabaje en mi PC mientras estoy en la calle", o pida actualizar, reparar o agregar conectores a un agente creado con esta skill, aunque no mencione Telegram ni la palabra agente.
---

# Agente personal por Telegram con Claude Code

Vas a construir con la persona su propio asistente: le escribe o le habla por Telegram desde el celular, un bot en su computador transcribe el audio, corre Claude Code con permisos por lista blanca en su carpeta de trabajo y le responde por el chat. La plantilla viene de un agente real que ya funciona; tu trabajo es adaptarla a esta persona con una conversación guiada, instalarla, probarla y dejarle sus guías.

## Cómo conducir la conversación
- **Una o dos preguntas a la vez**, en lenguaje simple. Mucha gente que llega aquí no programa. Si tienes la herramienta AskUserQuestion, úsala para las preguntas con opciones (sistema, conectores, destino de documentos); marca la recomendada.
- **Explica el porqué en una línea** cuando una pregunta no sea obvia («te pregunto cómo suena su nombre porque el transcriptor a veces lo escribe mal»).
- **Tú haces el trabajo técnico.** La persona solo decide, autoriza conectores en la web y escribe sus secretos en su propia terminal.
- **Nunca pidas ni aceptes secretos en el chat** (token del bot, contraseñas, claves de aplicación). Si la persona pega uno, dile que lo revoque/cambie y úsalo como ejemplo de por qué existe `configurar.py`.
- **Avanza por fases y di en qué vas** («Vamos en la 5 de 9: conectores»). Guarda las respuestas en un `respuestas.json` a medida que avanzas, así una conversación interrumpida se retoma.
- Si la persona ya tiene un agente creado con esta skill y quiere actualizarlo, agregar conectores o arreglar algo, salta a «Mantener un agente existente».

Rutas: `<skill>` es la carpeta de esta skill. Los scripts se corren con el Python de la persona (`py` en Windows, `python3` en macOS/Linux).

## Fase 0 · Presentación (sin preguntas técnicas aún)
Explica en 4-5 líneas qué van a construir y qué necesita:
- Plan de Claude **Pro o Max** con Claude Code (el agente consume de ese plan).
- **Telegram** en el celular.
- Un computador que pueda quedar **encendido** cuando quiera usar el agente.
- Unos 30-45 minutos.
Pregunta si arrancan.

## Fase 1 · El computador
1. Corre `<skill>/scripts/verificar_entorno.py --probar-claude` y lee el JSON.
2. Confirma el sistema que detectaste: «Veo que usas Windows 11, ¿correcto?». Si la conversación corre en otro equipo distinto del que alojará el agente, detente: la instalación debe hacerse en el computador donde vivirá.
3. Resuelve `pendientes` uno por uno con `references/sistemas.md` (Python, Claude Code, sesión iniciada, LibreOffice para PDF). Instala paquetes cuando lleguen a la fase 8.

## Fase 2 · La persona
- ¿Cómo te llamas y cómo quieres que te llame el asistente?
- ¿Prefieres que te trate de **tú** o de **usted**?
- ¿En qué idioma te responde? (por defecto español; la detección de órdenes está pensada para español)

## Fase 3 · El asistente
- ¿Cómo quieres que se llame? Sugiere nombres cortos de 1-2 sílabas si duda: se dicen fácil en un audio.
- Genera 3-5 **variantes de voz** (cómo lo podría escribir mal el transcriptor: «Fore» → fora, fori, for; «Luna» → luma, una). Muéstralas y pregunta si agrega alguna. Sirven para reconocer «Oye Luna, recuerda...».

## Fase 4 · Su información: cuántos computadores y cómo revisarla
Esta fase decide cuánto cuesta cada pregunta y si hace falta nube; tómala con calma. Detalle en `references/memoria.md`.
1. **¿En cuántos computadores está la información que quieres que revise?**
   - **Uno:** todo queda local. No hace falta subir nada a la nube ni programar sincronización; la memoria se mantiene con la limpieza semanal y listo.
   - **Dos o más:** la memoria (o el Cerebro) vive en una carpeta sincronizada y cada computador con agente tiene su propio bot.
2. **¿Cómo quieres que revise tu computador?** Explica las tres opciones con su costo:
   - **A. Acceso a una carpeta tal como está** (por ejemplo Documentos): no hay que preparar nada, pero en cada pregunta el agente busca a ciegas y gasta más tokens y tiempo.
   - **B. Una carpeta de trabajo organizada** por áreas y proyectos, cada uno con un CLAUDE.md corto: preparación moderada y búsquedas rápidas.
   - **C. Un Cerebro local:** un índice de proyectos, personas y decisiones que gasta tokens una sola vez al crearlo; después cada pregunta sale muy barata porque sabe dónde buscar.
   - **Recomienda:** si tiene muchísima información vieja que ya no usa, C no es rentable; B sí. Lo que mejor funciona es mezclar B y C: organizar solo lo activo y hacer el Cerebro de eso.
3. Propón la **carpeta de trabajo** según la opción (A: la carpeta existente, sin la carpeta personal completa; B/C: por ejemplo `Documentos/Proyectos`). El agente solo puede leer y escribir dentro de ella (más sus conectores), así que no conviene meter ahí lo que no quiera exponer.
4. **¿Quieres que además pueda leer archivos de cualquier parte del computador?** Explica el cambio:
   - **Solo su carpeta (recomendado para empezar):** lo más seguro; si algo está fuera, se lo dice.
   - **Todo el computador:** más útil para encontrar cualquier cosa, pero un correo o página con instrucciones escondidas podría intentar que lea algo privado. Los secretos conocidos (`.env`, sesión de Claude, llaves SSH) quedan bloqueados igual, y **escribir** sigue permitido solo dentro de la carpeta de trabajo.
5. La **carpeta del agente** (código y secretos) va aparte y fuera de la carpeta de trabajo; propón `~/Agentes/<Nombre>`.
Anota en `respuestas.json`: `memoria.tipo` = `simple` (A o B) o `cerebro` (C o B+C), `computadores` = número y `archivos.lectura` = `carpeta` o `todo`.

## Fase 5 · Conectores
Lee `references/conectores.md`. Pregunta primero por su ecosistema («¿tu correo y agenda son Google, Microsoft u otro?»), luego por notas/tareas y otros servicios. Recomendados: correo + agenda + archivos de su ecosistema; web y archivos locales ya vienen incluidos.
Para cada conector elegido:
1. Guíala a autorizarlo en claude.ai › Configuración › Conectores (o registra el MCP local).
2. Verifica con `claude mcp list` antes de seguir al siguiente.
Anota en `respuestas.json > conectores` el nombre y el uso en palabras simples («leer correos y crear borradores»).

## Fase 6 · Qué puede hacer (permisos)
Explica los tres modos con ejemplos usando el nombre del asistente:
- **Preguntar** («¿qué tengo mañana?»): solo lee.
- **Encargar** («Luna, haz…», «quiero que agendes…», «¿puedes…?»): además crea y edita.
- **Recordar** («recuerda que…»): guarda en su memoria.
Y lo que **nunca** hará por defecto: enviar correos o mensajes (deja borradores), borrar, compartir, publicar, pagar, ejecutar comandos. Pregunta si quiere prohibir algo más o si le preocupa algo. Si pide permitir algo prohibido, usa `references/seguridad.md` para explicarle el riesgo antes de aceptar.

## Fase 7 · Voz, documentos, memoria y rutina
Pregunta, de a una o dos:
- **Notas de voz** ¿sí o no? Modelo según `modelo_voz_recomendado` del informe (small por defecto, base si tiene poca RAM). Se transcribe en su computador, gratis y sin enviar el audio a otro servicio.
- **Documentos** (Word/PDF que le pida): ¿dónde los deja? Opciones: carpeta sincronizada de Google Drive/OneDrive/Dropbox (recomendada si usa alguna: aparece en su celular), Nextcloud, o solo en el computador.
- **Memoria compartida** (solo si en la fase 4 dijo dos o más computadores): ¿qué carpeta sincronizada usa (Nextcloud, Google Drive, OneDrive, Dropbox)? Ahí vivirá la memoria o el Cerebro.
- **Mantenimiento semanal**: ¿qué día y a qué hora? Explica que cierra la semana (logros, pendientes, vencimientos), limpia la memoria y le manda el resumen. Sugiere domingo en la noche o el día antes de que se reinicie su límite semanal de Claude.

## Fase 8 · Construcción
1. Escribe `respuestas.json` con la forma de `<skill>/assets/config.ejemplo.json`.
2. `crear_agente.py --respuestas respuestas.json --destino <carpeta del agente> --instalar-dependencias`
3. `listar_herramientas.py --agente <carpeta>` y `clasificar_herramientas.py --agente <carpeta>`.
4. Revisa con la persona solo lo que salga en «Para revisar», explicando en una frase qué hace cada herramienta. Ajusta `herramientas.json` (quita la clave `_revisar` al terminar).
5. Prueba sin Telegram desde la carpeta del agente: `agente.py --probar "¿qué archivos hay en mi carpeta de trabajo?"` y, si hay conectores, una consulta que los use. Corrige antes de seguir.

## Fase 9 · Telegram
1. Guíala en BotFather: `/newbot`, nombre visible, usuario terminado en `bot`. Recuérdale que el token es una llave y no va en el chat.
2. Pídele que abra **su propia terminal** en la carpeta del agente y corra `configurar.py`. El script oculta el token, lo valida, le pide escribirle «hola» al bot para registrar su cuenta como único dueño y, si las entregas van a Nextcloud, pide esos datos.
3. Cuando diga «ya configuré», corre `servicio.py instalar` y, si activó el mantenimiento, `servicio.py mantenimiento`.
4. Revisa `logs/agente.log`: debe decir «conectado como @...».

## Fase 10 · Guías y prueba final
1. `generar_guias.py --agente <carpeta> --pdf` → `guias/GUIA-CONFIGURACION` y `guias/GUIA-DE-USO` en .md, .docx (y .pdf si hay Word o LibreOffice). Si las entregas van a una carpeta sincronizada, copia las guías ahí también para que las tenga en el celular.
2. Prueba real, en este orden, mirando el log entre cada una:
   - Texto: «¿qué puedes hacer?»
   - Nota de voz: «Oye <nombre>, recuerda que me gusta el café sin azúcar» → debe caer en modo memoria.
   - Encargo: «<nombre>, haz un documento en Word con tres ideas para mi semana» → debe llegar el aviso de entrega.
3. Explica cómo mantener el computador despierto (`references/sistemas.md`); ese ajuste lo hace la persona.

## Cierre
Resume en pocas líneas: nombre y usuario del bot, conectores, qué nunca hará, dónde están las guías, cuándo corre el mantenimiento y los tres comandos que más usará (`servicio.py estado`, `servicio.py reiniciar`, `agente.py --probar`). Si algo quedó pendiente (un conector sin autorizar, PDF sin LibreOffice), dilo claro.

## Mantener un agente existente
- **Actualizar el código:** `crear_agente.py --destino <carpeta> --actualizar` y `servicio.py reiniciar`. Conserva config, herramientas, memoria y secretos.
- **Agregar o quitar conectores:** sigue «Después de agregar o quitar conectores» en `references/conectores.md`, luego regenera las guías.
- **Cambiar nombre, trato, voz, entregas o rutina:** edita `config.json`, `servicio.py mantenimiento` si cambió la rutina, `servicio.py reiniciar` y regenera las guías.
- **Algo falla:** `references/problemas.md`.

## Qué hay en la skill
- `assets/plantilla/`: el bot (`agente.py`), entregas, mantenimiento, `configurar.py` (secretos) y `servicio.py` (arranque en Windows, macOS y Linux). No se editan para personalizar: todo va en `config.json` y `herramientas.json`.
- `assets/config.ejemplo.json`: forma de las respuestas.
- `scripts/`: verificar entorno, crear agente, listar y clasificar herramientas, generar guías.
- `references/`: conectores, seguridad, sistemas operativos, memoria y Cerebro, problemas frecuentes. Léelas cuando llegues a la fase que las necesita, no todas al inicio.
