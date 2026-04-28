import os
import time
import requests
from playwright.sync_api import sync_playwright

# =========================
# CONFIG
# =========================
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

MODELO_URL = "https://www.cbhours.com/user/camilamonroee.html"

LAST_UPDATE_ID = 0
ACTIVO = True


# =========================
# TELEGRAM
# =========================
def enviar_mensaje(texto):
    try:
        requests.post(f"{BASE_URL}/sendMessage", data={
            "chat_id": CHAT_ID,
            "text": texto
        })
    except Exception as e:
        print("Telegram error:", e)


# =========================
# COMANDOS
# =========================
def procesar_comandos():
    global LAST_UPDATE_ID, ACTIVO

    try:
        url = f"{BASE_URL}/getUpdates?offset={LAST_UPDATE_ID + 1}"
        data = requests.get(url).json()

        for u in data.get("result", []):
            LAST_UPDATE_ID = u["update_id"]

            if "message" not in u:
                continue

            msg = u["message"]
            chat_id = str(msg.get("chat", {}).get("id"))
            text = msg.get("text", "").strip().lower()

            if chat_id != str(CHAT_ID):
                continue

            print("Comando:", text)

            if text == "/on":
                ACTIVO = True
                enviar_mensaje("🟢 BOT ACTIVADO")

            elif text == "/off":
                ACTIVO = False
                enviar_mensaje("🔴 BOT DESACTIVADO")

            elif text == "/status":
                enviar_mensaje(f"Estado bot: {'ACTIVO' if ACTIVO else 'INACTIVO'}")

    except Exception as e:
        print("Error comandos:", e)


# =========================
# SCRAPER DEFINITIVO (PLAYWRIGHT)
# =========================
def obtener_estado():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(MODELO_URL, timeout=60000)
            page.wait_for_timeout(5000)  # espera JS

            html = page.content()

            browser.close()

            print("\n===================")
            print("HTML SIZE:", len(html))
            print("===================\n")

            # 🔥 DETECCIÓN FLEXIBLE (NO depende de clase exacta)
            lower = html.lower()

            if "online" in lower:
                return "online"
            elif "offline" in lower:
                return "offline"

            return None

    except Exception as e:
        print("Playwright error:", e)
        return None


# =========================
# INICIO
# =========================
enviar_mensaje("🤖 BOT DEFINITIVO (PLAYWRIGHT) INICIADO")

print("Bot iniciado...")


# =========================
# LOOP PRINCIPAL
# =========================
while True:
    try:
        procesar_comandos()

        if not ACTIVO:
            time.sleep(10)
            continue

        estado = obtener_estado()

        print("👉 ESTADO DETECTADO:", estado)

        if estado == "online":
            enviar_mensaje("🔥 MODELO ONLINE DETECTADA 🔥")

        time.sleep(60)

    except Exception as e:
        print("ERROR GENERAL:", e)
        time.sleep(10)
