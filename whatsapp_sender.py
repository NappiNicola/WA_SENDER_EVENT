from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import time
import re
import os

driver = None  # sessione globale Chrome


# ==============================================================
# 🔤 Formattazione messaggio
# ==============================================================
def format_message(message: str) -> str:
    if not message:
        return ""
        # Normalizza le nuove righe
    message = message.replace("\r\n", "\n").replace("\r", "\n").replace("\t", " ")

    # Rimuove caratteri non BMP (es. alcune emoji o simboli particolari)
    message = "".join(ch for ch in message if ord(ch) <= 0xFFFF)

    # Divide e rimuove righe completamente vuote
    lines = [line.strip() for line in message.split("\n") if line.strip()]

    # Ricostruisce con un solo \n
    formatted = "\n".join(lines)

    return formatted.strip()


# ==============================================================
# 📞 Estrazione dati da testo
# ==============================================================
def extract_phone(text: str):
    match = re.search(r'\+?\d{8,15}', text or "")
    return match.group(0) if match else None


def extract_time(iso_string: str):
    dt = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
    return dt.strftime("%H:%M")


# ==============================================================
# 🌐 Gestione WhatsApp Web via Selenium
# ==============================================================
def start_whatsapp():
    """Avvia WhatsApp Web (riutilizzando la sessione precedente)."""
    global driver
    if driver:
        print("✅ WhatsApp Web già avviato.")
        return driver

    print("🌐 Avvio WhatsApp Web tramite Selenium...")

    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    # 🔒 Usa una cartella per salvare la sessione (così non rifai il QR code)
    user_data_dir = os.path.join(os.getcwd(), "chrome_profile")
    os.makedirs(user_data_dir, exist_ok=True)
    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")

    # 🚀 Avvio ChromeDriver con gestione automatica della versione
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Vai su WhatsApp Web
    driver.get("https://web.whatsapp.com/")
    driver.fullscreen_window()
    print("🔄 Attendi il caricamento di WhatsApp Web e la scansione del QR code (solo la prima volta)...")

    time.sleep(10)
    return driver


# ==============================================================
# ✉️ Invio messaggio
# ==============================================================
def send_whatsapp_message(phone: str, message: str):
    """Invia un messaggio WhatsApp mantenendo gli a capo e la formattazione."""
    global driver
    if not driver:
        start_whatsapp()

    message_cleaned = format_message(message)

    try:
        print(f"📨 Invio messaggio a {phone}...")

        # 1️⃣ Apri la chat del numero (senza testo precompilato)
        url = f"https://web.whatsapp.com/send?phone={phone}"
        driver.get(url)
        driver.fullscreen_window()

        # 2️⃣ Attendi caricamento chat
        time.sleep(8)

        # 3️⃣ Trova il campo di input messaggio
        input_box = driver.switch_to.active_element

        # 4️⃣ Invia il messaggio riga per riga mantenendo la formattazione
        for line in message_cleaned.split("\n"):
            input_box.send_keys(line)
            input_box.send_keys(Keys.SHIFT, Keys.ENTER)  # vero a capo

        # 5️⃣ Invia il messaggio
        input_box.send_keys(Keys.ENTER)

        print(f"✅ Messaggio inviato correttamente a {phone}")
        time.sleep(2)

    except (NoSuchElementException, TimeoutException) as e:
        print(f"⚠️ Impossibile inviare il messaggio a {phone}: {e}")
    except Exception as e:
        print(f"❌ Errore durante l'invio a {phone}: {e}")


# ==============================================================
# 🔚 Chiusura browser
# ==============================================================
def close_whatsapp():
    """Chiude il browser WhatsApp Web."""
    global driver
    if driver:
        print("🛑 Chiusura WhatsApp Web...")
        try:
            driver.quit()
        except Exception:
            pass
        driver = None
