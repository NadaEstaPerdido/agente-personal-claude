"""Guarda los secretos del agente en .env sin mostrarlos en pantalla.

Córrelo en TU terminal (no se lo pegues a nadie, tampoco a Claude):
  python configurar.py            token del bot, tu cuenta de Telegram y, si aplica, Nextcloud
  python configurar.py --dueno    solo vuelve a registrar tu cuenta de Telegram
"""
import getpass
import json
import os
import re
import sys
import time
from pathlib import Path

import requests

AQUI = Path(__file__).resolve().parent
ENV = AQUI / ".env"
ESTADO = AQUI / "estado.json"
CFG = json.loads((AQUI / "config.json").read_text(encoding="utf-8"))


def leer_env():
    datos = {}
    if ENV.exists():
        for linea in ENV.read_text(encoding="utf-8-sig").splitlines():
            if "=" in linea and not linea.strip().startswith("#"):
                k, v = linea.split("=", 1)
                datos[k.strip()] = v.strip()
    return datos


def guardar_env(datos):
    texto = "# Secretos del agente. No compartas este archivo.\n" + "".join(f"{k}={v}\n" for k, v in datos.items())
    ENV.write_text(texto, encoding="utf-8")
    if os.name != "nt":
        os.chmod(ENV, 0o600)


def telegram(token, metodo, **datos):
    r = requests.post(f"https://api.telegram.org/bot{token}/{metodo}", json=datos, timeout=70)
    j = r.json()
    if not j.get("ok"):
        raise RuntimeError(j.get("description", "error de Telegram"))
    return j["result"]


def pedir_token(env):
    actual = env.get("TELEGRAM_BOT_TOKEN")
    aviso = " (Enter para conservar el actual)" if actual else ""
    while True:
        token = getpass.getpass(f"Pega el token que te dio BotFather; no se verá{aviso}: ").strip() or actual
        if not token:
            print("Necesito el token para continuar.")
            continue
        if not re.fullmatch(r"\d+:[A-Za-z0-9_-]{30,}", token):
            print("Eso no parece un token de BotFather. Intenta de nuevo.")
            continue
        try:
            yo = telegram(token, "getMe")
        except Exception as e:  # noqa: BLE001
            print(f"Telegram rechazó el token ({e}). Revisa que lo copiaste completo.")
            continue
        print(f"✔ Token válido: tu bot es @{yo['username']}")
        return token, yo["username"]


def registrar_dueno(token, usuario_bot):
    print(f"\nAbre Telegram en tu celular, busca @{usuario_bot} y escríbele «hola». Te espero hasta 3 minutos...")
    limite = time.time() + 180
    offset = None
    while time.time() < limite:
        try:
            updates = telegram(token, "getUpdates", offset=offset, timeout=20, allowed_updates=["message"])
        except RuntimeError as e:
            if "Conflict" in str(e):
                print("El bot ya está corriendo y se lleva los mensajes. Detenlo (python servicio.py detener) y repite.")
                sys.exit(1)
            raise
        for u in updates:
            offset = u["update_id"] + 1
            msg = u.get("message") or {}
            if (msg.get("chat") or {}).get("type") != "private":
                continue
            quien = msg.get("from") or {}
            nombre = " ".join(x for x in (quien.get("first_name"), quien.get("last_name")) if x)
            respuesta = input(f"Llegó un mensaje de {nombre} (@{quien.get('username', 'sin usuario')}). ¿Eres tú? [s/n]: ")
            if respuesta.strip().lower().startswith("s"):
                estado = json.loads(ESTADO.read_text(encoding="utf-8")) if ESTADO.exists() else {}
                estado["offset"] = offset
                ESTADO.write_text(json.dumps(estado, indent=2), encoding="utf-8")
                telegram(token, "sendMessage", chat_id=msg["chat"]["id"], text="✔ Listo, desde ahora solo te obedezco a ti.")
                return str(quien["id"])
    print("No llegó ningún mensaje. Corre de nuevo: python configurar.py --dueno")
    sys.exit(1)


def pedir_nextcloud(env):
    nc = CFG.get("entregas", {})
    print("\nNextcloud (para subir tus documentos). Usa una contraseña de aplicación: Nextcloud › Configuración personal › Seguridad.")
    url = input(f"URL de tu Nextcloud [{env.get('NEXTCLOUD_URL') or nc.get('nextcloud_url', '')}]: ").strip()
    usuario = input(f"Usuario [{env.get('NEXTCLOUD_USUARIO', '')}]: ").strip()
    clave = getpass.getpass("Contraseña de aplicación; no se verá (Enter para conservar): ").strip()
    env["NEXTCLOUD_URL"] = url or env.get("NEXTCLOUD_URL") or nc.get("nextcloud_url", "")
    env["NEXTCLOUD_USUARIO"] = usuario or env.get("NEXTCLOUD_USUARIO", "")
    if clave:
        env["NEXTCLOUD_CLAVE"] = clave


def main():
    env = leer_env()
    token, usuario_bot = pedir_token(env)
    env["TELEGRAM_BOT_TOKEN"] = token
    guardar_env(env)
    if "--dueno" in sys.argv or not env.get("TELEGRAM_OWNER_ID"):
        env["TELEGRAM_OWNER_ID"] = registrar_dueno(token, usuario_bot)
        guardar_env(env)
        print("✔ Tu cuenta quedó registrada.")
    if CFG.get("entregas", {}).get("destino") == "nextcloud" and "--dueno" not in sys.argv:
        pedir_nextcloud(env)
        guardar_env(env)
    print(f"\nListo: secretos guardados en {ENV}. Vuelve a la conversación con Claude y dile «ya configuré».")


if __name__ == "__main__":
    main()
