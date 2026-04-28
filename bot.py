import requests
from bs4 import BeautifulSoup
import time
import os
import datetime

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URL = "https://www.cbhours.com/user/victoria_and_michael.html"

estado_anterior = None


def enviar_mensaje(texto):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": texto
        })
    except Exception as e:
        print("Error enviando mensaje:", e)


def obtener_estado():
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(URL, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        estado_div = soup.find("span", class_="room_status_text")

        if estado_div:
            clases = estado_div.get("class", [])
            print("Clases detectadas:", clases)

            if "online" in clases:
                return "online"
            elif "offline" in clases:
                return "offline"

        return None

    except Exception as e:
        print("Error obteniendo estado:", e)
        return None


# 🔥 Mensaje único al iniciar
enviar_mensaje("✅ Bot activo y monitoreando")


while True:
    try:
        estado = obtener_estado()
        print("Estado actual:", estado)

        # Notifica solo cuando pasan a ONLINE
        if estado == "online" and estado_anterior != "online":
            enviar_mensaje("🔥 ESTÁN ONLINE 🔥")

        estado_anterior = estado

        # ⏱️ Frecuencia inteligente
        hora = datetime.datetime.now().hour

        if 18 <= hora <= 23:
            tiempo_espera = 540   # más frecuente
        else:
            tiempo_espera = 900   # más lento

        print(f"Esperando {tiempo_espera} segundos...")
        time.sleep(tiempo_espera)

    except Exception as e:
        print("Error general:", e)
        time.sleep(60)
