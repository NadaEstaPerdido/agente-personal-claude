# Problemas frecuentes (síntoma → causa → arreglo)

Empieza siempre por: `python servicio.py estado` y las últimas 30 líneas de `logs/agente.log`.

## El bot no responde
- **Computador suspendido o sin internet.** El log muestra «Sin conexión con Telegram». Arreglo: ver `references/sistemas.md` › mantener despierto.
- **El proceso no está corriendo.** `servicio.py estado` lo dice. Arreglo: correr `python agente.py` en una terminal para ver el error en vivo; corregir y `servicio.py iniciar`.
- **Conflict: terminated by other getUpdates request.** Dos copias con el mismo token (otro computador, o una terminal abierta además de la tarea). Arreglo: dejar una sola; cada computador con su propio bot.
- **El bot arranca y se cae enseguida tras un cambio de código.** Correr `python agente.py` a mano muestra la traza.

## Responde con error
- **«Not logged in» / «Invalid API key».** Claude Code perdió la sesión. La persona abre una terminal, `claude`, `/login`.
- **Límite de uso alcanzado.** Es el mismo límite del plan de Claude; esperar al reinicio o subir de plan.
- **«La tarea se pasó del tiempo máximo».** Dividir la tarea o subir `limites` en `config.json`.

## Dice que no tiene acceso a un conector
1. `claude mcp list` en la carpeta de trabajo: ¿dice ✔ Connected?
   - «Needs authentication» → autorizar en claude.ai › Conectores.
   - ✘ Failed → revisar el comando del servidor local.
2. Si en la terminal conecta pero dentro del bot no: el conector falla solo cuando lo arranca la tarea programada. Mira el registro del servidor en
   - Windows: `%LOCALAPPDATA%\claude-cli-nodejs\Cache\<carpeta-codificada>\mcp-logs-<servidor>\`
   - macOS: `~/Library/Caches/claude-cli-nodejs/<carpeta-codificada>/mcp-logs-<servidor>/`
   - Linux: `~/.cache/claude-cli-nodejs/<carpeta-codificada>/mcp-logs-<servidor>/`
   Caso conocido en Windows con la **app de escritorio de Claude**: la app viene empaquetada (MSIX) y Windows redirige su `AppData\Roaming` a `%LOCALAPPDATA%\Packages\Claude_<id>\LocalCache\Roaming`. Lo que se instale desde una sesión de la app en `AppData\Roaming` (por ejemplo `uv tool install`) solo existe para la app: el bot, que corre fuera, ve «uv trampoline failed to canonicalize script path» o «El sistema no puede encontrar la ruta especificada». Arreglo: instalar o copiar el servidor a una carpeta normal fuera de AppData (por ejemplo `~/.nextcloud-mcp`, copiando la carpeta de `LocalCache\Roaming\uv\tools\<servidor>`) y registrar el comando con su `Scripts\python.exe` (ver `references/conectores.md`). Para comprobarlo desde el entorno del bot, no desde la app: la tarea programada debe poder ejecutar ese `python.exe`.
3. Si conecta pero la herramienta no está permitida: falta en `herramientas.json`. Volver a listar y clasificar.
4. Prueba aislada: `python agente.py --probar "usa <herramienta> y dime qué ves"`.

## Notas de voz
- **No reconoce las órdenes** («recuerda», «haz») porque el transcriptor escribe mal el nombre del asistente: agregar esas variantes en `asistente.variantes_voz` y reiniciar.
- **Transcribe lento:** usar el modelo `base` en `voz.modelo`.
- **Error al cargar el modelo la primera vez:** necesita internet para descargarlo (unos 500 MB para `small`).

## Entregas
- **«No pude crear el PDF».** Falta Word o LibreOffice; o pedir el documento en Word.
- **Nextcloud 401.** Contraseña de aplicación mal copiada: `python configurar.py` y volver a escribirla.
- **Carpeta sincronizada no existe.** Revisar la ruta en `config.json > entregas.carpeta`.

## El token apareció en algún lado
BotFather › `/revoke` › `python configurar.py` con el token nuevo › `servicio.py reiniciar`. El log ya oculta secretos; si un log viejo lo tiene, bórralo.
