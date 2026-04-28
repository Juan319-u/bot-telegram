import requests
from bs4 import BeautifulSoup
import time
import os
import datetime

# =========================
# CONFIG
# =========================
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

MODELO_URL = "https://www.cbhours.com/user/camilamonroee.html"

estado_anterior = None
ACTIVO = True
LAST_UPDATE_ID = 0


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
        print("Error enviar mensaje:", e)


def enviar_menu():
    teclado = {
        "keyboard": [
            ["🟢 Activar", "🔴 Desactivar"],
            ["📊 Estado"]
        ],
        "resize_keyboard": True
    }

    requests.post(f"{BASE_URL}/sendMessage", json={
        "chat_id": CHAT_ID,
        "text": "Control del bot 👇",
        "reply_markup": teclado
    })


# =========================
# SCRAPER
# =========================
def obtener_estado(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        estado = soup.find("span", class_="room_status_text")

        if estado:
            clases = estado.get("class", [])

            if "online" in clases:
                return "online"
            elif "offline" in clases:
                return "offline"

        return None

    except Exception as e:
        print("Error scraping:", e)
        return None


# =========================
# COMANDOS
# =========================
def procesar_comandos():
    global ACTIVO, LAST_UPDATE_ID

    try:
        url = f"{BASE_URL}/getUpdates?offset={LAST_UPDATE_ID + 1}"
        data = requests.get(url).json()

        for update in data.get("result", []):
            LAST_UPDATE_ID = update["update_id"]

            if "message" not in update:
                continue

            msg = update["message"]
            chat_id = str(msg.get("chat", {}).get("id"))
            text = msg.get("text", "").strip().lower()

            if chat_id != str(CHAT_ID):
                continue

            print("Comando:", text)

            # =========================
            # COMANDOS NUEVOS
            # =========================
            if text == "/on":
                ACTIVO = True
                enviar_mensaje("🟢 Bot ACTIVADO")

            elif text == "/off":
                ACTIVO = False
                enviar_mensaje("🔴 Bot DESACTIVADO")

            elif text == "/status":
                estado = "ACTIVO 🟢" if ACTIVO else "INACTIVO 🔴"
                enviar_mensaje(f"Estado: {estado}")

            enviar_menu()

    except Exception as e:
        print("Error comandos:", e)


# =========================
# INICIO
# =========================
enviar_mensaje("🤖 Bot de prueba iniciado (1 modelo)")
enviar_menu()


# =========================
# LOOP
# =========================
while True:
    try:
        procesar_comandos()

        if not ACTIVO:
            print("Bot apagado...")
            time.sleep(15)
            continue

        estado = obtener_estado(MODELO_URL)
        print("Estado modelo:", estado)

        # 🔥 DETECCIÓN DE CAMBIO REAL
        if estado == "online" and estado_anterior != "online":
            enviar_mensaje("🔥 MODELO ONLINE DETECTADA 🔥")

        estado_anterior = estado

        # =========================
        # frecuencia simple (debug)
        # =========================
        time.sleep(60)

    except Exception as e:
        print("Error general:", e)
        time.sleep(30)
