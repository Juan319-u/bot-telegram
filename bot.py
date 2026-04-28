import cloudscraper
import requests
import time
import os

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

URL = "https://www.cbhours.com/user/camilamonroee.html"

LAST_UPDATE_ID = 0
ACTIVO = True

scraper = cloudscraper.create_scraper()


# =========================
# TELEGRAM
# =========================
def send(msg):
    requests.post(f"{BASE_URL}/sendMessage", data={
        "chat_id": CHAT_ID,
        "text": msg
    })


# =========================
# COMANDOS
# =========================
def commands():
    global LAST_UPDATE_ID, ACTIVO

    try:
        r = requests.get(f"{BASE_URL}/getUpdates?offset={LAST_UPDATE_ID+1}").json()

        for u in r.get("result", []):
            LAST_UPDATE_ID = u["update_id"]

            if "message" not in u:
                continue

            msg = u["message"]
            chat_id = str(msg["chat"]["id"])
            text = msg.get("text", "").lower()

            if chat_id != str(CHAT_ID):
                continue

            if text == "/on":
                ACTIVO = True
                send("🟢 ON")

            elif text == "/off":
                ACTIVO = False
                send("🔴 OFF")

            elif text == "/status":
                send(f"Estado: {'ACTIVO' if ACTIVO else 'INACTIVO'}")


    except Exception as e:
        print("cmd error:", e)


# =========================
# SCRAPER SIMPLE (SIN SELCTORES)
# =========================
def check():
    try:
        r = scraper.get(URL, timeout=15)

        html = r.text.lower()

        print("SIZE:", len(html))

        # 🔥 búsqueda directa de texto
        if "online" in html:
            return "online"
        elif "offline" in html:
            return "offline"

        return None

    except Exception as e:
        print("scraper error:", e)
        return None


# =========================
# INIT
# =========================
send("🤖 BOT SIMPLE INICIADO")
print("bot iniciado")


# =========================
# LOOP
# =========================
last_state = None

while True:
    try:
        commands()

        if not ACTIVO:
            time.sleep(10)
            continue

        state = check()

        print("STATE:", state)

        # 🔥 solo avisa cambios reales
        if state == "online" and last_state != "online":
            send("🔥 MODELO ONLINE")

        last_state = state

        time.sleep(60)

    except Exception as e:
        print("loop error:", e)
        time.sleep(10)
