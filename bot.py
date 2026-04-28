import requests
import time
import os
from playwright.sync_api import sync_playwright

# =========================
# CONFIGURACIÓN
# =========================
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

MODELOS = {
    "Victoria & Michael": "https://www.cbhours.com/user/victoria_and_michael.html",
    #"Kelly Fernandes": "https://www.cbhours.com/user/kellyfernandes.html",
    "Cristal Bunny": "https://www.cbhours.com/user/cristal_bunny.html",
    #"Jimmy Mia Couple": "https://www.cbhours.com/user/jimmymiacouple.html",
    #"Ashley Ospino": "https://www.cbhours.com/user/ashley_ospino.html",
    #"Susie Thomsonn": "https://www.cbhours.com/user/susie_thomsonn.html"
}

estados_anteriores = {m: None for m in MODELOS}
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
        }, timeout=10)
    except Exception as e:
        print("Error Telegram:", e)


# =========================
# COMANDOS
# =========================
def procesar_comandos():
    global ACTIVO, LAST_UPDATE_ID

    try:
        url = f"{BASE_URL}/getUpdates?offset={LAST_UPDATE_ID + 1}"
        response = requests.get(url, timeout=10).json()

        for update in response.get("result", []):
            LAST_UPDATE_ID = update["update_id"]

            if "message" not in update:
                continue

            msg = update["message"]
            chat_id = str(msg.get("chat", {}).get("id"))
            text = msg.get("text", "").strip().lower()

            if chat_id != str(CHAT_ID):
                continue

            print("Comando:", text)

            if text == "/on":
                ACTIVO = True
                enviar_mensaje("🟢 Bot ACTIVADO")

            elif text == "/off":
                ACTIVO = False
                enviar_mensaje("🔴 Bot DESACTIVADO")

            elif text == "/status":
                enviar_mensaje(f"Estado: {'ACTIVO 🟢' if ACTIVO else 'INACTIVO 🔴'}")


    except Exception as e:
        print("Error comandos:", e)


# =========================
# PLAYWRIGHT INIT (IMPORTANTE)
# =========================
print("Iniciando navegador...")

play = sync_playwright().start()
browser = play.chromium.launch(headless=True, args=["--no-sandbox"])
page = browser.new_page()

# =========================
# SCRAPER REAL (REUTILIZA PÁGINA)
# =========================
def obtener_estado(url):
    try:
        page.goto(url, timeout=60000)
        page.wait_for_timeout(3000)

        html = page.content().lower()

        if "online" in html:
            return "online"
        elif "offline" in html:
            return "offline"

        return None

    except Exception as e:
        print("Playwright error:", e)
        return None


# =========================
# INICIO
# =========================
enviar_mensaje("🤖 Bot Playwright estable iniciado")
print("Bot iniciado")


# =========================
# LOOP PRINCIPAL
# =========================
while True:
    try:
        procesar_comandos()

        if not ACTIVO:
            time.sleep(10)
            continue

        modelos_online = []

        for nombre, url in MODELOS.items():
            estado = obtener_estado(url)
            print(f"{nombre}: {estado}")

            if estado == "online" and estados_anteriores[nombre] != "online":
                enviar_mensaje(f"🔥 {nombre} está ONLINE 🔥")

            if estado == "online":
                modelos_online.append(nombre)

            estados_anteriores[nombre] = estado

        if len(modelos_online) > 1:
            lista = "\n".join(modelos_online)
            enviar_mensaje(f"🔥 {len(modelos_online)} modelos online:\n{lista}")

        time.sleep(60)

    except Exception as e:
        print("Error general:", e)
        time.sleep(10)
