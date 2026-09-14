# Por sistema operativo

## Instalar lo básico
| | Windows | macOS | Linux |
|---|---|---|---|
| Python 3.10+ | python.org (marcar «Add to PATH») o `winget install Python.Python.3.12`; usar `py` | `brew install python` o python.org; usar `python3` | `sudo apt install python3 python3-pip python3-venv` |
| Claude Code | `irm https://claude.ai/install.ps1 \| iex` en PowerShell, o `npm install -g @anthropic-ai/claude-code` | `curl -fsSL https://claude.ai/install.sh \| bash` | igual que macOS |
| Iniciar sesión | abrir una terminal, `claude`, luego `/login` | igual | igual |
| PDF | Word (si lo tiene) o LibreOffice | LibreOffice | `sudo apt install libreoffice-writer` |

Si un comando de instalación falla, revisa la documentación oficial de Claude Code antes de improvisar.
Las notas de voz no necesitan ffmpeg: faster-whisper decodifica el audio por su cuenta.

## Arranque automático (lo hace `servicio.py instalar`)
- **Windows:** tarea del Programador de tareas al iniciar sesión, con `pythonw.exe` (sin ventana), reinicio cada minuto si falla y sin límite de tiempo.
- **macOS:** LaunchAgent en `~/Library/LaunchAgents` con `RunAtLoad` y `KeepAlive`. Guarda el PATH del momento de instalar para que encuentre `claude`.
- **Linux:** servicio de systemd de usuario con `Restart=always`. Para que corra sin iniciar sesión gráfica: `loginctl enable-linger $USER`.

## Mantenimiento semanal (lo hace `servicio.py mantenimiento`)
- **Windows:** tarea semanal con «Activar el equipo para ejecutar» y «ejecutar lo antes posible si se perdió».
- **macOS:** `StartCalendarInterval`. launchd no despierta el equipo; si debe correr con la tapa cerrada: `sudo pmset repeat wake <día> <hora>` (explícale y que lo corra la persona).
- **Linux:** timer de systemd con `Persistent=true` (corre al encender si se perdió).

## Mantener el computador despierto
El agente solo responde con el computador encendido. Explícale a la persona cómo hacerlo; es un ajuste de su sistema, así que lo hace ella:
- **Windows:** Configuración › Sistema › Energía y batería › suspensión en «Nunca» con corriente.
- **macOS:** Ajustes › Batería/Energía › «Evitar el reposo automático cuando la pantalla esté apagada».
- **Linux:** Configuración › Energía › suspensión automática desactivada.
Alternativa si no quiere dejarlo siempre encendido: usar el agente solo en horario de oficina y saberlo.

## Particularidades de Windows
- **«claude.ps1 no se puede cargar porque la ejecución de scripts está deshabilitada»:** usa `claude.cmd` o abre «Símbolo del sistema» (cmd) en lugar de PowerShell. No cambies la política de ejecución sin que la persona lo pida y entienda qué implica.
- **Rutas con espacios y tildes:** funcionan; siempre entre comillas en los comandos.
- **WDAC o antivirus corporativo** pueden bloquear ejecutables descargados (uv, servidores MCP). Si algo "no arranca" sin error claro, revisa eso primero.
- El bot usa el ejecutable real de Claude Code (no el `.cmd`) para evitar problemas de comillas; `crear_agente.py` lo encuentra y lo guarda en `config.json`.
