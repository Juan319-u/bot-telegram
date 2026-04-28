import requests
from bs4 import BeautifulSoup
import time
import os

# Variables desde Railway
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URL = "https://www.cbhours.com/user/victoria_and_michael.html"

estado_anterior = None


def enviar_mensaje(texto):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        r = requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": texto
        })
        print("Mensaje enviado:", r.status_code)
    except Exception as e:
        print("Error enviando mensaje:", e)


def obtener_estado():
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(URL, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        texto = soup.text.lower()

        if "online" in texto:
            return "online"
        return "offline"

    except Exception as e:
        print("Error obteniendo estado:", e)
        return None


# 🔥 Mensaje al iniciar (para probar que funciona)
enviar_mensaje("✅ BOT INICIADO Y FUNCIONANDO")


while True:
    try:
        estado = obtener_estado()

        print("Estado actual:", estado)

        # Solo notifica cuando pasan de OFFLINE → ONLINE
        if estado == "online" and estado_anterior != "online":
            enviar_mensaje("🔥 ESTÁN ONLINE 🔥")

        estado_anterior = estado

        time.sleep(180)  # cada 3 minutos

    except Exception as e:
        print("Error general:", e)
        time.sleep(60)
