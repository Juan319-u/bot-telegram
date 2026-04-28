import requests
from bs4 import BeautifulSoup
import time
import os

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
        print("Error Telegram:", e)


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

            print("📩 Comando recibido:", text)

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
# SCRAPER DEBUG
# =========================
def obtener_estado(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        r = requests.get(url, headers=headers, timeout=15)

        print("\n====================")
        print("STATUS CODE:", r.status_code)
        print("HTML SIZE:", len(r.text))
        print("HTML SAMPLE:\n", r.text[:800])
        print("====================\n")

        soup = BeautifulSoup(r.text, "html.parser")

        estado = soup.find("span", class_="room_status_text")

        if estado:
            clases = estado.get("class", [])
            print("CLASES DETECTADAS:", clases)

            if "online" in clases:
                return "online"
            elif "offline" in clases:
                return "offline"

        print("⚠ NO SE ENCONTRÓ EL SELECTOR")
        return None

    except Exception as e:
        print("ERROR SCRAPER:", e)
        return None


# =========================
# INICIO
# =========================
enviar_mensaje("🤖 BOT DEBUG INICIADO")

print("Bot iniciado...")

# =========================
# LOOP
# =========================
while True:
    try:
        procesar_comandos()

        if not ACTIVO:
            print("⛔ Bot pausado")
            time.sleep(10)
            continue

        estado = obtener_estado(MODELO_URL)

        print("👉 ESTADO FINAL DETECTADO:", estado)

        if estado == "online":
            enviar_mensaje("🔥 MODELO ONLINE DETECTADA 🔥")

        time.sleep(60)

    except Exception as e:
        print("ERROR GENERAL:", e)
        time.sleep(10)
