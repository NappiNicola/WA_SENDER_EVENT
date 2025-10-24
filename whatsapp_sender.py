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
    """Invia un messaggio WhatsApp mantenendo gli a capo (compatibile con il layout aggiornato)."""
    global driver
    if not driver:
        start_whatsapp()

    try:
        message_cleaned = format_message(message)
        if not message_cleaned:
            print(f"⚠️ Messaggio vuoto o non valido per {phone}.")
            return

        print(f"📨 Apertura chat di {phone}...")
        driver.get(f"https://web.whatsapp.com/send?phone={phone}")
        driver.fullscreen_window()
        time.sleep(10)  # attesa caricamento chat

        # 🔍 Trova il campo di input messaggio (nuovo layout WhatsApp Web)
        print("🔎 Ricerca campo messaggio...")
        input_box = None
        for _ in range(10):
            try:
                input_box = driver.find_element(
                    By.XPATH,
                    '//div[@contenteditable="true" and @data-tab="10"]'
                )
                if input_box:
                    break
            except:
                time.sleep(1)

        if not input_box:
            print("❌ Campo messaggio non trovato. Controlla che la chat sia aperta correttamente.")
            return

        print("✍️ Scrittura messaggio...")

        # Invio riga per riga con a capo reale
        lines = message_cleaned.split("\n")
        for i, line in enumerate(lines):
            input_box.send_keys(line)
            if i < len(lines) - 1:
                input_box.send_keys(Keys.SHIFT, Keys.ENTER)
                time.sleep(0.1)

        # 🚀 Invio
        input_box.send_keys(Keys.ENTER)
        print(f"✅ Messaggio inviato correttamente a {phone}")
        time.sleep(3)

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
