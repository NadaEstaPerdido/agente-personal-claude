# Conectores

## Cómo llegan al agente
- **Conectores de Claude** (claude.ai › Configuración › Conectores): se autorizan una vez en la web con la cuenta de Claude y aparecen solos en Claude Code cuando la sesión es la misma cuenta. En modo headless se llaman `mcp__claude_ai_<Nombre>__<herramienta>`.
- **Servidores MCP locales**: se instalan en el computador y se registran con `claude mcp add --scope user ...`. Sirven para servicios sin conector oficial (Nextcloud, bases de datos propias).
- El catálogo de conectores de claude.ai cambia con el tiempo: muéstrale a la persona lo que ve en su propia pantalla de Conectores y usa esta lista como recomendación, no como promesa.

## Recomendados para un asistente personal
Ofrece primero el paquete de su ecosistema; los demás, si los usa.

| Para qué | Google | Microsoft | Otros |
|---|---|---|---|
| Correo (leer y borradores) | Gmail | Microsoft 365 (Outlook) | Nextcloud Mail |
| Agenda | Google Calendar | Microsoft 365 (Calendario) | Nextcloud Calendar |
| Archivos | Google Drive | Microsoft 365 (OneDrive, SharePoint) | Dropbox, Box, Nextcloud |
| Notas y tareas | — | Microsoft 365 (To Do) | Notion, Todoist, Asana, Linear |
| Equipo | — | Teams (solo lectura) | Slack (solo lectura) |
| Negocio | — | — | HubSpot, Stripe (solo lectura), Canva |
| Programación | — | — | GitHub |
| Puente a miles de apps | — | — | Zapier |

Siempre incluidos sin conector: búsqueda y lectura web, y los archivos de la carpeta de trabajo.

**Pregunta sugerida:** «¿Tu correo y calendario son de Google, de Microsoft u otro?» y luego «¿Usas alguna app de notas o tareas (Notion, Todoist, Asana…)?». Así se elige sin abrumar con 15 opciones.

## Conectar un conector de Claude
1. La persona abre claude.ai › Configuración › Conectores, busca el servicio y lo autoriza con su cuenta.
2. En la terminal: `claude mcp list`. Debe verse `claude.ai <Nombre>: ... ✔ Connected`. Si dice «Needs authentication», falta autorizarlo en la web.
3. Corre `scripts/listar_herramientas.py` para confirmar que el modo headless lo ve.

## Nextcloud (MCP local)
1. Instalar uv y el servidor: `uv tool install nextcloud-mcp-server`.
2. Crear una contraseña de aplicación en Nextcloud › Configuración personal › Seguridad.
3. Registrar (ajusta rutas y datos):
   `claude mcp add --scope user nextcloud -e NEXTCLOUD_HOST=https://mi.nube -e NEXTCLOUD_USERNAME=usuario -e NEXTCLOUD_PASSWORD=<clave de aplicación> -- nextcloud-mcp-server run --transport stdio`
   La persona escribe la clave en su terminal; nunca la pidas en el chat.
4. **Windows:** no uses el lanzador `.exe` de uv ni rutas dentro de `AppData\Roaming` si la instalación se hizo desde la app de escritorio de Claude: esa carpeta está virtualizada y el bot no la ve (ver `references/problemas.md`). Deja el servidor en una carpeta normal, por ejemplo `py -m venv %USERPROFILE%\.nextcloud-mcp` y `%USERPROFILE%\.nextcloud-mcp\Scripts\python.exe -m pip install nextcloud-mcp-server`, y regístralo con comando `%USERPROFILE%\.nextcloud-mcp\Scripts\python.exe` y argumentos `-c "from nextcloud_mcp_server.cli import cli; cli()" run --transport stdio`.
5. Si las entregas van a Nextcloud, `configurar.py` pide URL, usuario y la misma contraseña de aplicación para el `.env` del agente.

## Después de agregar o quitar conectores
1. `python scripts/listar_herramientas.py --agente <carpeta>`
2. `python scripts/clasificar_herramientas.py --agente <carpeta>` y revisar con la persona lo marcado.
3. Actualizar `conectores` en `config.json` (nombre y uso en palabras simples: así el agente sabe para qué sirve cada uno).
4. `python servicio.py reiniciar` y probar con `python agente.py --probar "..."`.
