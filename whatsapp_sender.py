from datetime import datetime
import re
import pywhatkit
import pyautogui
import time

def extract_phone(text: str):
    match = re.search(r'\+?\d{8,15}', text or "")
    return match.group(0) if match else None

def extract_time(iso_string: str):
    dt = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
    return dt.strftime("%H:%M")

def send_whatsapp_message(phone: str, message: str):
    try:
        print(f"📨 Invio messaggio a {phone}...")

        # Apre WhatsApp Web e scrive il messaggio
        pywhatkit.sendwhatmsg_instantly(phone, message, wait_time=15, tab_close=False)

        # Attesa per caricamento completo della chat
        print("⏳ Attesa caricamento WhatsApp Web...")
        time.sleep(8)

        # Mette il focus su WhatsApp e invia il messaggio
        pyautogui.click()  # clicca al centro per assicurarsi che la finestra sia attiva
        pyautogui.press("enter")  # invia il messaggio

        print(f"✅ Messaggio inviato correttamente a {phone}")

        time.sleep(2)
        pyautogui.hotkey("ctrl", "w")  # chiude la scheda (se vuoi)

    except Exception as e:
        print(f"❌ Errore durante l'invio a {phone}: {e}")
