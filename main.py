from calendar_api import get_tomorrow_events
from whatsapp_sender import (
    extract_phone,
    extract_time,
    start_whatsapp,
    send_whatsapp_message,
    close_whatsapp
)
from config_loader import API_URL, MY_PHONE
from logger_module import write_log, read_log
from logger_execution import write_log as write_ex, read_log as red_ex


def send_daily_reminder(phone_list):
    """Invia il promemoria giornaliero ai numeri di servizio (MY_PHONE)."""
    log_content = read_log()
    message = f"📅 Promemoria giornaliero:\n\n{log_content}"

    for number in phone_list:
        send_whatsapp_message(number, message)
        write_log(f"Promemoria inviato a {number}")
        write_ex(f"Promemoria inviato a {number}")


def function_1():
    """Recupera gli eventi di domani e invia un messaggio WhatsApp ai partecipanti."""
    print("📅 Recupero eventi di domani...")
    events = get_tomorrow_events(API_URL)

    if not events:
        print("⚠️ Nessun evento trovato per domani.")
        write_log("Nessun evento trovato per domani.")
        write_ex("Nessun evento trovato per domani.")
        return

    for e in events:
        title = e.get('title', 'Senza titolo')
        description = e.get('description', '')
        phone = extract_phone(description)
        start = extract_time(e.get('start', ''))
        end = extract_time(e.get('end', ''))

        if phone:
            message = (
                f"Ciao! Ti scrivo riguardo all'evento di domani:\n"
                f"📌 *{title}*\n🕒 Dalle ore {start} alle {end}"
            )

            print(f"➡️ Invio messaggio a {phone}: {message}")
            send_whatsapp_message(phone, message)

            write_log(f"Messaggio inviato a {phone} per evento '{title}' alle {start}")
            write_ex(f"Messaggio inviato a {phone} per evento '{title}' alle {start}")
        else:
            print(f"ℹ️ Nessun numero trovato per evento '{title}'")
            write_log(f"Nessun numero trovato per evento '{title}'")
            write_ex(f"Nessun numero trovato per evento '{title}'")

    print("✅ Operazione completata.")
    write_log("Invio completato.")
    write_ex("Invio completato.")


def main():
    """Flusso principale del programma."""
    try:
        start_whatsapp()  # ✅ Avvia WhatsApp una sola volta
        function_1()
        send_daily_reminder(MY_PHONE)
    finally:
        close_whatsapp()  # ✅ Chiude la sessione alla fine


if __name__ == "__main__":
    main()
