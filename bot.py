import requests
from bs4 import BeautifulSoup
import time
import os
import datetime

# =========================
# CONFIGURACIÓN
# =========================
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

MODELOS = {
    "Victoria & Michael": "https://www.cbhours.com/user/victoria_and_michael.html",
    "Kelly Fernandes": "https://www.cbhours.com/user/kellyfernandes.html",
    "Cristal Bunny": "https://www.cbhours.com/user/cristal_bunny.html",
    "Jimmy Mia Couple": "https://www.cbhours.com/user/jimmymiacouple.html",
    "Ashley Ospino": "https://www.cbhours.com/user/ashley_ospino.html",
    "Susie Thomsonn": "https://www.cbhours.com/user/susie_thomsonn.html"
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
        })
    except Exception as e:
        print("Error enviando mensaje:", e)


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
# SCRAPER ESTADO
# =========================
def obtener_estado(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        estado_div = soup.find("span", class_="room_status_text")

        if estado_div:
            clases = estado_div.get("class", [])
            if "online" in clases:
                return "online"
            elif "offline" in clases:
                return "offline"

        return None

    except:
        return None


# =========================
# COMANDOS TELEGRAM
# =========================
def procesar_comandos():
    global ACTIVO, LAST_UPDATE_ID

    try:
        url = f"{BASE_URL}/getUpdates?offset={LAST_UPDATE_ID + 1}"
        response = requests.get(url).json()

        for update in response.get("result", []):
            LAST_UPDATE_ID = update["update_id"]

            if "message" not in update:
                continue

            mensaje = update["message"]
            chat_id = str(mensaje.get("chat", {}).get("id"))
            texto = mensaje.get("text", "").strip().lower()

            if chat_id != str(CHAT_ID):
                continue

            print("Comando recibido:", texto)

            # =========================
            # COMANDOS
            # =========================
            if texto in ["/on", "on", "🟢 activar"]:
                ACTIVO = True
                enviar_mensaje("🟢 Bot ACTIVADO")

            elif texto in ["/off", "off", "🔴 desactivar"]:
                ACTIVO = False
                enviar_mensaje("🔴 Bot DESACTIVADO")

            elif texto == "📊 estado":
                estado = "ACTIVO 🟢" if ACTIVO else "INACTIVO 🔴"
                enviar_mensaje(f"Estado actual: {estado}")

            enviar_menu()

    except Exception as e:
        print("Error comandos:", e)


# =========================
# INICIO
# =========================
enviar_mensaje("Bot iniciado correctamente")
enviar_menu()


# =========================
# LOOP PRINCIPAL
# =========================
while True:
    try:
        procesar_comandos()

        if not ACTIVO:
            print("Bot pausado...")
            time.sleep(20)
            continue

        modelos_online = []

        for nombre, url in MODELOS.items():
            estado = obtener_estado(url)
            print(f"{nombre}: {estado}")

            # alerta cambio offline → online
            if estado == "online" and estados_anteriores[nombre] != "online":
                enviar_mensaje(f"🔥 {nombre} está ONLINE 🔥")

            if estado == "online":
                modelos_online.append(nombre)

            estados_anteriores[nombre] = estado

        # resumen
        if len(modelos_online) > 1:
            lista = "\n".join(modelos_online)
            enviar_mensaje(f"🔥 {len(modelos_online)} modelos online:\n{lista}")

        # =========================
        # TIEMPO INTELIGENTE
        # =========================
        hora = datetime.datetime.now().hour

        if 18 <= hora <= 23:
            tiempo_espera = 180
        elif 0 <= hora <= 6:
            tiempo_espera = 1200
        else:
            tiempo_espera = 600

        time.sleep(tiempo_espera)

    except Exception as e:
        print("Error general:", e)
        time.sleep(60)
