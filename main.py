from calendar_api import get_tomorrow_events
from whatsapp_sender import extract_phone, send_whatsapp_message, extract_time
# from config import API_URL, MY_PHONE
from config_loader import API_URL, MY_PHONE
from logger_module import write_log, read_log
from logger_execution import write_log as write_ex, read_log as red_ex

def send_daily_reminder(phone):
    log_content = read_log()
    message = f"📅 Promemoria giornaliero:\n\n{log_content}"
    send_whatsapp_message(phone, message)

def main():
    print("📅 Recupero eventi di domani...")
    events = get_tomorrow_events(API_URL)

    if not events:
        print("⚠️ Nessun evento trovato per domani.")
        write_log("Nessun evento trovato per domani.")
        write_ex("Nessun evento trovato per domani")
        return


    for e in events:
        title = e.get('title', '')
        description = e.get('description', '')
        phone = extract_phone(description)
        start = e.get('start', '')
        start = extract_time(start)
        end = e.get('end', '')
        end = extract_time(end)

        if phone:
            message = f"Ciao! Ti scrivo riguardo all'evento di domani: {title}.\nDalle ore: {start} alle ore: {end}"
            print(f"➡️ Invio messaggio a {phone}: {message}")
            write_log(f"Messaggio inviato a {phone} per evento '{title}' alle {start}")
            write_ex(f"Messaggio inviato a {phone} per evento '{title}' alle {start}")
            send_whatsapp_message(phone, message)
        else:
            print(f"ℹ️ Nessun numero trovato per evento '{title}'")
            write_log(f"Nessun numero trovato per evento '{title}'")
            write_ex(f"Nessun numero trovato per evento '{title}'")

        print("✅ Operazione completata.")
        write_log("Invio completato.")
        write_ex("Invio completato.")

if __name__ == "__main__":
    main()
    send_daily_reminder(MY_PHONE)
