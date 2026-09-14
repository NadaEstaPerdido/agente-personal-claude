"""Arranque automático y mantenimiento semanal del agente, en Windows, macOS o Linux.

  python servicio.py instalar        arranca solo al iniciar sesión y se reinicia si se cae
  python servicio.py mantenimiento   programa el mantenimiento semanal (día y hora de config.json)
  python servicio.py iniciar | detener | reiniciar | estado
  python servicio.py desinstalar     quita el arranque y el mantenimiento
"""
import json
import os
import platform
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
CFG = json.loads((AQUI / "config.json").read_text(encoding="utf-8"))
NOMBRE = CFG["asistente"]["nombre"]
SLUG = re.sub(r"[^a-z0-9]+", "-", unicodedata.normalize("NFKD", NOMBRE).encode("ascii", "ignore").decode().lower()).strip("-") or "agente"
SISTEMA = platform.system()
DIAS = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]
DIAS_EN = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def dia_y_hora():
    m = CFG.get("mantenimiento", {})
    dia = unicodedata.normalize("NFKD", m.get("dia", "martes")).encode("ascii", "ignore").decode().lower()
    hora, minuto = (int(x) for x in m.get("hora", "21:00").split(":"))
    return DIAS.index(dia), hora, minuto


def correr(cmd, **kw):
    p = subprocess.run(cmd, capture_output=True, text=True, **kw)
    salida = (p.stdout + p.stderr).strip()
    if salida:
        print(salida)
    return p.returncode


def python_sin_ventana():
    exe = Path(sys.executable)
    if SISTEMA == "Windows" and exe.with_name("pythonw.exe").exists():
        return str(exe.with_name("pythonw.exe"))
    return str(exe)


# ------------------------------------------------------------------ Windows (Programador de tareas)
def _ps(script):
    return correr(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script])


def _tarea(sufijo):
    return f"Agente {NOMBRE} - {sufijo}"


def win_instalar():
    return _ps(f"""
$a = New-ScheduledTaskAction -Execute '{python_sin_ventana()}' -Argument '"{AQUI / "agente.py"}"' -WorkingDirectory '{AQUI}'
$d = New-ScheduledTaskTrigger -AtLogOn -User "$env:USERDOMAIN\\$env:USERNAME"; $d.Delay = 'PT30S'
$s = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -RestartCount 10 -RestartInterval (New-TimeSpan -Minutes 1) -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew
$p = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\\$env:USERNAME" -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName '{_tarea("bot")}' -Action $a -Trigger $d -Settings $s -Principal $p -Force | Out-Null
Start-ScheduledTask -TaskName '{_tarea("bot")}'
Write-Host 'Arranque automático instalado y bot iniciado.'""")


def win_mantenimiento():
    dia, hora, minuto = dia_y_hora()
    return _ps(f"""
$a = New-ScheduledTaskAction -Execute '{python_sin_ventana()}' -Argument '"{AQUI / "mantenimiento.py"}"' -WorkingDirectory '{AQUI}'
$d = New-ScheduledTaskTrigger -Weekly -DaysOfWeek {DIAS_EN[dia]} -At {hora:02d}:{minuto:02d}
$s = New-ScheduledTaskSettingsSet -StartWhenAvailable -WakeToRun -RunOnlyIfNetworkAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 4) -MultipleInstances IgnoreNew
$p = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\\$env:USERNAME" -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName '{_tarea("mantenimiento")}' -Action $a -Trigger $d -Settings $s -Principal $p -Force | Out-Null
Write-Host ('Mantenimiento programado. Próxima corrida: ' + (Get-ScheduledTaskInfo -TaskName '{_tarea("mantenimiento")}').NextRunTime)""")


def win_detener():
    return _ps(f"""
Stop-ScheduledTask -TaskName '{_tarea("bot")}' -ErrorAction SilentlyContinue
Get-CimInstance Win32_Process -Filter "Name like 'python%'" | Where-Object {{ $_.CommandLine -like '*{AQUI / "agente.py"}*' }} | ForEach-Object {{ Stop-Process -Id $_.ProcessId -Force }}
Write-Host 'Bot detenido.'""")


def win_iniciar():
    return _ps(f"Start-ScheduledTask -TaskName '{_tarea('bot')}'; Write-Host 'Bot iniciado.'")


def win_estado():
    return _ps(f"""
foreach ($n in '{_tarea("bot")}','{_tarea("mantenimiento")}') {{
  $t = Get-ScheduledTask -TaskName $n -ErrorAction SilentlyContinue
  if ($t) {{ Write-Host ($n + ': ' + $t.State + ' | próxima: ' + (Get-ScheduledTaskInfo -TaskName $n).NextRunTime) }} else {{ Write-Host ($n + ': no instalada') }}
}}""")


def win_desinstalar():
    win_detener()
    return _ps(f"""
foreach ($n in '{_tarea("bot")}','{_tarea("mantenimiento")}') {{ Unregister-ScheduledTask -TaskName $n -Confirm:$false -ErrorAction SilentlyContinue }}
Write-Host 'Tareas quitadas.'""")


# ------------------------------------------------------------------ macOS (launchd)
LAUNCH = Path.home() / "Library" / "LaunchAgents"


def _plist(nombre, script, extra):
    ruta = LAUNCH / f"com.agente.{SLUG}.{nombre}.plist"
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.agente.{SLUG}.{nombre}</string>
  <key>ProgramArguments</key><array><string>{sys.executable}</string><string>{AQUI / script}</string></array>
  <key>WorkingDirectory</key><string>{AQUI}</string>
  <key>EnvironmentVariables</key><dict><key>PATH</key><string>{os.environ.get("PATH", "")}</string></dict>
  <key>StandardOutPath</key><string>{AQUI / "logs" / (nombre + ".out.log")}</string>
  <key>StandardErrorPath</key><string>{AQUI / "logs" / (nombre + ".err.log")}</string>
{extra}
</dict></plist>
""", encoding="utf-8")
    return ruta


def _launchctl(accion, ruta):
    dominio = f"gui/{os.getuid()}"
    if accion == "cargar":
        subprocess.run(["launchctl", "bootout", dominio, str(ruta)], capture_output=True)
        return correr(["launchctl", "bootstrap", dominio, str(ruta)])
    return correr(["launchctl", "bootout", dominio, str(ruta)])


def mac_instalar():
    (AQUI / "logs").mkdir(exist_ok=True)
    ruta = _plist("bot", "agente.py", "  <key>RunAtLoad</key><true/>\n  <key>KeepAlive</key><true/>")
    _launchctl("cargar", ruta)
    print("Arranque automático instalado y bot iniciado.")


def mac_mantenimiento():
    (AQUI / "logs").mkdir(exist_ok=True)
    dia, hora, minuto = dia_y_hora()
    semana_mac = (dia + 1) % 7  # launchd: 0 = domingo
    extra = (f"  <key>StartCalendarInterval</key><dict><key>Weekday</key><integer>{semana_mac}</integer>"
             f"<key>Hour</key><integer>{hora}</integer><key>Minute</key><integer>{minuto}</integer></dict>")
    _launchctl("cargar", _plist("mantenimiento", "mantenimiento.py", extra))
    print(f"Mantenimiento programado: {DIAS[dia]} {hora:02d}:{minuto:02d}.")


def mac_detener():
    correr(["launchctl", "bootout", f"gui/{os.getuid()}/com.agente.{SLUG}.bot"])


def mac_iniciar():
    _launchctl("cargar", LAUNCH / f"com.agente.{SLUG}.bot.plist")


def mac_estado():
    for n in ("bot", "mantenimiento"):
        codigo = subprocess.run(["launchctl", "print", f"gui/{os.getuid()}/com.agente.{SLUG}.{n}"], capture_output=True).returncode
        print(f"{n}: {'instalado' if codigo == 0 else 'no instalado'}")


def mac_desinstalar():
    for n in ("bot", "mantenimiento"):
        ruta = LAUNCH / f"com.agente.{SLUG}.{n}.plist"
        if ruta.exists():
            _launchctl("quitar", ruta)
            ruta.unlink()
    print("Arranque y mantenimiento quitados.")


# ------------------------------------------------------------------ Linux (systemd de usuario)
SYSTEMD = Path.home() / ".config" / "systemd" / "user"


def _unidad(nombre, contenido):
    SYSTEMD.mkdir(parents=True, exist_ok=True)
    (SYSTEMD / nombre).write_text(contenido, encoding="utf-8")


def _systemctl(*args):
    return correr(["systemctl", "--user", *args])


def linux_instalar():
    _unidad(f"agente-{SLUG}.service", f"""[Unit]
Description=Agente {NOMBRE} (Telegram + Claude Code)
After=network-online.target

[Service]
WorkingDirectory={AQUI}
ExecStart={sys.executable} {AQUI / "agente.py"}
Environment=PATH={os.environ.get("PATH", "")}
Restart=always
RestartSec=60

[Install]
WantedBy=default.target
""")
    _systemctl("daemon-reload")
    _systemctl("enable", "--now", f"agente-{SLUG}.service")
    print("Arranque automático instalado. Para que corra aunque no inicies sesión: loginctl enable-linger $USER")


def linux_mantenimiento():
    dia, hora, minuto = dia_y_hora()
    _unidad(f"agente-{SLUG}-mantenimiento.service", f"""[Unit]
Description=Mantenimiento semanal del agente {NOMBRE}

[Service]
Type=oneshot
WorkingDirectory={AQUI}
ExecStart={sys.executable} {AQUI / "mantenimiento.py"}
Environment=PATH={os.environ.get("PATH", "")}
""")
    _unidad(f"agente-{SLUG}-mantenimiento.timer", f"""[Unit]
Description=Mantenimiento semanal del agente {NOMBRE}

[Timer]
OnCalendar={DIAS_EN[dia][:3]} *-*-* {hora:02d}:{minuto:02d}:00
Persistent=true

[Install]
WantedBy=timers.target
""")
    _systemctl("daemon-reload")
    _systemctl("enable", "--now", f"agente-{SLUG}-mantenimiento.timer")
    print(f"Mantenimiento programado: {DIAS[dia]} {hora:02d}:{minuto:02d}.")


def linux_desinstalar():
    _systemctl("disable", "--now", f"agente-{SLUG}.service", f"agente-{SLUG}-mantenimiento.timer")
    for n in (f"agente-{SLUG}.service", f"agente-{SLUG}-mantenimiento.service", f"agente-{SLUG}-mantenimiento.timer"):
        (SYSTEMD / n).unlink(missing_ok=True)
    _systemctl("daemon-reload")
    print("Arranque y mantenimiento quitados.")


ACCIONES = {
    "Windows": {"instalar": win_instalar, "mantenimiento": win_mantenimiento, "iniciar": win_iniciar,
                "detener": win_detener, "estado": win_estado, "desinstalar": win_desinstalar},
    "Darwin": {"instalar": mac_instalar, "mantenimiento": mac_mantenimiento, "iniciar": mac_iniciar,
               "detener": mac_detener, "estado": mac_estado, "desinstalar": mac_desinstalar},
    "Linux": {"instalar": linux_instalar, "mantenimiento": linux_mantenimiento,
              "iniciar": lambda: _systemctl("start", f"agente-{SLUG}.service"),
              "detener": lambda: _systemctl("stop", f"agente-{SLUG}.service"),
              "estado": lambda: _systemctl("--no-pager", "status", f"agente-{SLUG}.service", f"agente-{SLUG}-mantenimiento.timer"),
              "desinstalar": linux_desinstalar},
}


def main():
    accion = sys.argv[1] if len(sys.argv) > 1 else ""
    acciones = ACCIONES.get(SISTEMA)
    if not acciones:
        raise SystemExit(f"Sistema no soportado: {SISTEMA}")
    if accion == "reiniciar":
        acciones["detener"]()
        acciones["iniciar"]()
    elif accion in acciones:
        acciones[accion]()
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
