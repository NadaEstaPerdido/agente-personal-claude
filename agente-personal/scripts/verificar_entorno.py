"""Revisa si el computador está listo para el agente y devuelve un informe en JSON.

  python verificar_entorno.py                  revisión rápida
  python verificar_entorno.py --probar-claude  además comprueba que Claude Code tiene sesión iniciada
"""
import ctypes
import importlib.util
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def ram_gb():
    try:
        if os.name == "nt":
            class Mem(ctypes.Structure):
                _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                            ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                            ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                            ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                            ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
            m = Mem()
            m.dwLength = ctypes.sizeof(Mem)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
            return round(m.ullTotalPhys / 2**30, 1)
        if platform.system() == "Darwin":
            return round(int(subprocess.check_output(["sysctl", "-n", "hw.memsize"])) / 2**30, 1)
        for linea in Path("/proc/meminfo").read_text().splitlines():
            if linea.startswith("MemTotal"):
                return round(int(linea.split()[1]) / 2**20, 1)
    except Exception:  # noqa: BLE001
        return None


def buscar_claude():
    for c in [x for x in (shutil.which("claude.exe"), shutil.which("claude")) if x]:
        ruta = Path(c)
        if ruta.suffix.lower() in (".cmd", ".ps1", ".bat") or (os.name == "nt" and not ruta.suffix):
            paquete = ruta.parent / "node_modules" / "@anthropic-ai" / "claude-code"
            if (paquete / "bin" / "claude.exe").exists():
                return [str(paquete / "bin" / "claude.exe")]
            if (paquete / "cli.js").exists():
                node = ruta.parent / "node.exe"
                return [str(node) if node.exists() else (shutil.which("node") or "node"), str(paquete / "cli.js")]
            continue
        return [str(ruta)]
    for extra in (Path.home() / ".local" / "bin" / "claude.exe", Path.home() / ".local" / "bin" / "claude",
                  Path("/opt/homebrew/bin/claude"), Path("/usr/local/bin/claude")):
        if extra.exists():
            return [str(extra)]
    return None


def hay_word():
    if os.name != "nt":
        return Path("/Applications/Microsoft Word.app").exists()
    return subprocess.run(["reg", "query", r"HKCR\Word.Application"], capture_output=True).returncode == 0


def hay_libreoffice():
    return bool(shutil.which("soffice") or shutil.which("libreoffice")
                or Path(r"C:\Program Files\LibreOffice\program\soffice.exe").exists()
                or Path("/Applications/LibreOffice.app").exists())


def main():
    sin_ventana = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    informe = {
        "sistema": f"{platform.system()} {platform.release()} ({platform.machine()})",
        "python": {"version": platform.python_version(), "ejecutable": sys.executable,
                   "ok": sys.version_info >= (3, 10)},
        "paquetes": {p: importlib.util.find_spec(m) is not None
                     for p, m in (("requests", "requests"), ("python-docx", "docx"), ("faster-whisper", "faster_whisper"))},
        "ram_gb": ram_gb(),
        "pdf": {"word": hay_word(), "libreoffice": hay_libreoffice()},
    }
    ram = informe["ram_gb"] or 8
    informe["modelo_voz_recomendado"] = "base" if ram < 6 else "small"

    claude = buscar_claude()
    informe["claude"] = {"comando": claude, "encontrado": bool(claude)}
    if claude:
        try:
            v = subprocess.run(claude + ["--version"], capture_output=True, text=True, timeout=60, creationflags=sin_ventana)
            informe["claude"]["version"] = (v.stdout or v.stderr).strip()
        except Exception as e:  # noqa: BLE001
            informe["claude"]["version"] = f"error: {e}"
        if "--probar-claude" in sys.argv:
            try:
                p = subprocess.run(claude + ["-p", "--output-format", "json"], input="Responde solo: OK",
                                   capture_output=True, text=True, encoding="utf-8", timeout=180, creationflags=sin_ventana)
                j = json.loads(p.stdout)
                informe["claude"]["sesion_iniciada"] = not j.get("is_error")
                informe["claude"]["respuesta"] = (j.get("result") or "")[:120]
            except Exception:  # noqa: BLE001
                informe["claude"]["sesion_iniciada"] = False
                informe["claude"]["respuesta"] = (locals().get("p") and (p.stderr or p.stdout) or "")[-300:]

    faltantes = [p for p, ok in informe["paquetes"].items() if not ok]
    informe["pendientes"] = (
        ([] if informe["python"]["ok"] else ["Instalar Python 3.10 o más reciente"])
        + ([f"Instalar paquetes: {' '.join(faltantes)}"] if faltantes else [])
        + ([] if claude else ["Instalar Claude Code"])
        + (["Iniciar sesión en Claude Code"] if informe["claude"].get("sesion_iniciada") is False else [])
        + ([] if informe["pdf"]["word"] or informe["pdf"]["libreoffice"] else ["Para PDF: instalar LibreOffice (o Word)"])
    )
    print(json.dumps(informe, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
