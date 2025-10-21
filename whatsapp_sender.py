from datetime import datetime
import re
import pywhatkit
import pyautogui
import time

def extract_phone(text: str):
    """
    Estrae un numero di telefono da una stringa (es. +39...).
    """
    match = re.search(r'\+?\d{8,15}', text or "")
    return match.group(0) if match else None

def extract_time(iso_string: str):
    # Converte la stringa ISO in oggetto datetime
    dt = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
    # Ritorna l'orario nel formato HH:MM
    return dt.strftime("%H:%M")


def send_whatsapp_message(phone: str, message: str):
    try:
        # Apre WhatsApp Web e prepara il messaggio
        pywhatkit.sendwhatmsg_instantly(phone, message, wait_time=10, tab_close=True)
        time.sleep(5)  # aspetta che la pagina sia pronta
        pyautogui.press("enter")  # simula il click su INVIO

        print(f"✅ Messaggio inviato a {phone}")
    except Exception as e:
        print(f"❌ Errore durante l'invio a {phone}: {e}")
