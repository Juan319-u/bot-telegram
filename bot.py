import requests
from bs4 import BeautifulSoup
import time
import os
import datetime

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

MODELOS = {
    "Victoria & Michael": "https://www.cbhours.com/user/victoria_and_michael.html",
    "Kelly Fernandes": "https://www.cbhours.com/user/kellyfernandes.html",
    "Cristal Bunny": "https://www.cbhours.com/user/cristal_bunny.html",
    "Jimmy Mia Couple": "https://www.cbhours.com/user/jimmymiacouple.html",
    "Ashley Ospino": "https://www.cbhours.com/user/ashley_ospino.html",
    "Susie Thomsonn": "https://www.cbhours.com/user/susie_thomsonn.html"
}

estados_anteriores = {modelo: None for modelo in MODELOS}

ACTIVO = True
LAST_UPDATE_ID = None


def enviar_mensaje(texto):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": texto})
    except Exception as e:
        print("Error enviando mensaje:", e)


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
    except Exception as e:
        print("Error obteniendo estado:", e)
        return None


# 🔥 Leer comandos de Telegram
def revisar_comandos():
    global ACTIVO, LAST_UPDATE_ID

    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"

    try:
        response = requests.get(url).json()

        for update in response.get("result", []):
            update_id = update["update_id"]

            if LAST_UPDATE_ID is not None and update_id <= LAST_UPDATE_ID:
                continue

            LAST_UPDATE_ID = update_id

            if "message" not in update:
                continue

            mensaje = update["message"]
            chat_id = str(mensaje.get("chat", {}).get("id"))
            texto = mensaje.get("text", "")

            print("Comando recibido:", texto)

            if chat_id != CHAT_ID:
                continue

            if texto == "/on":
                ACTIVO = True
                enviar_mensaje("🟢 Bot ACTIVADO")

            elif texto == "/off":
                ACTIVO = False
                enviar_mensaje("🔴 Bot DESACTIVADO")

            elif texto == "/estado":
                estado = "ACTIVO 🟢" if ACTIVO else "INACTIVO 🔴"
                enviar_mensaje(f"Estado actual: {estado}")

    except Exception as e:
        print("Error leyendo comandos:", e)
# 🔥 Mensaje inicial
enviar_mensaje("✅ Bot con control remoto activo (/on /off /estado)")


while True:
    try:
        revisar_comandos()

        if not ACTIVO:
            print("Bot desactivado...")
            time.sleep(30)
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

        # ⏱️ Frecuencia inteligente
        hora = datetime.datetime.now().hour

        if 18 <= hora <= 23:
            tiempo_espera = 180
        elif 0 <= hora <= 6:
            tiempo_espera = 1200
        else:
            tiempo_espera = 600

        print(f"Esperando {tiempo_espera} segundos...")
        time.sleep(tiempo_espera)

    except Exception as e:
        print("Error general:", e)
        time.sleep(60)
