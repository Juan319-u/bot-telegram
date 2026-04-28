import cloudscraper
from bs4 import BeautifulSoup
import requests
import time
import os

# =========================
# CONFIG
# =========================
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

MODELO_URL = "https://www.cbhours.com/user/camilamonroee.html"

LAST_UPDATE_ID = 0
ACTIVO = True

# Scraper con bypass Cloudflare
scraper = cloudscraper.create_scraper()


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

            print("📩 comando:", text)

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
# SCRAPER (CLOUDFLARE BYPASS)
# =========================
def obtener_estado(url):
    try:
        r = scraper.get(url, timeout=15)

        print("\n===================")
        print("STATUS:", r.status_code)
        print("HTML SIZE:", len(r.text))
        print("===================\n")

        soup = BeautifulSoup(r.text, "html.parser")

        # 🔥 buscar cualquier elemento con esa clase
        estado = soup.select(".room_status_text")

        print("ELEMENTOS ENCONTRADOS:", len(estado))

        if estado:
            el = estado[0]
            clases = el.get("class", [])
            print("CLASES REALES:", clases)

            if "online" in clases:
                return "online"
            elif "offline" in clases:
                return "offline"

        print("⚠ NO SE ENCONTRÓ ESTADO REAL")
        return None

    except Exception as e:
        print("ERROR SCRAPER:", e)
        return None

# =========================
# INICIO
# =========================
enviar_mensaje("🤖 Bot con Cloudscraper iniciado")

print("Bot iniciado...")


# =========================
# LOOP
# =========================
while True:
    try:
        procesar_comandos()

        if not ACTIVO:
            print("⛔ bot apagado")
            time.sleep(10)
            continue

        estado = obtener_estado(MODELO_URL)

        print("👉 ESTADO FINAL:", estado)

        if estado == "online":
            enviar_mensaje("🔥 MODELO ONLINE DETECTADA 🔥")

        time.sleep(60)

    except Exception as e:
        print("ERROR GENERAL:", e)
        time.sleep(10)
