import cloudscraper
import requests
import time
import os

# =========================
# CONFIG
# =========================
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

MODELOS = {
    "Victoria & Michael": "https://www.cbhours.com/user/victoria_and_michael.html",
    #"Kelly Fernandes": "https://www.cbhours.com/user/kellyfernandes.html",
    "Cristal Bunny": "https://www.cbhours.com/user/cristal_bunny.html",
    "Camila Monroee": "https://www.cbhours.com/user/camilamonroee.html",
    #"Jimmy Mia Couple": "https://www.cbhours.com/user/jimmymiacouple.html",
    #"Ashley Ospino": "https://www.cbhours.com/user/ashley_ospino.html",
    #"Susie Thomsonn": "https://www.cbhours.com/user/susie_thomsonn.html"
}

estados_anteriores = {m: None for m in MODELOS}
ACTIVO = True
LAST_UPDATE_ID = 0

# scraper anti-cloudflare ligero
scraper = cloudscraper.create_scraper()


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
        data = requests.get(url, timeout=10).json()

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
                enviar_mensaje(f"Estado: {'ACTIVO 🟢' if ACTIVO else 'INACTIVO 🔴'}")

    except Exception as e:
        print("Error comandos:", e)


# =========================
# SCRAPER ESTABLE
# =========================
def obtener_estado(url):
    try:
        r = scraper.get(url, timeout=15)

        html = r.text.lower()

        print("HTML SIZE:", len(html))

        # detección simple y robusta
        if "online" in html:
            return "online"
        elif "offline" in html:
            return "offline"

        return None

    except Exception as e:
        print("Scraper error:", e)
        return None


# =========================
# INICIO
# =========================
enviar_mensaje("🤖 Bot estable iniciado (cloudscraper)")
print("Bot iniciado...")


# =========================
# LOOP PRINCIPAL
# =========================
while True:
    try:
        procesar_comandos()

        if not ACTIVO:
            time.sleep(15)
            continue

        modelos_online = []

        for nombre, url in MODELOS.items():
            estado = obtener_estado(url)
            print(f"{nombre}: {estado}")

            # alerta solo en cambio
            if estado == "online" and estados_anteriores[nombre] != "online":
                enviar_mensaje(f"🔥 {nombre} está ONLINE 🔥")

            if estado == "online":
                modelos_online.append(nombre)

            estados_anteriores[nombre] = estado

        # resumen
        if len(modelos_online) > 1:
            lista = "\n".join(modelos_online)
            enviar_mensaje(f"🔥 {len(modelos_online)} modelos online:\n{lista}")

        time.sleep(60)

    except Exception as e:
        print("Error general:", e)
        time.sleep(20)
