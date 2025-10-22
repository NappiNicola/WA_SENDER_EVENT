from calendar_api import get_tomorrow_events
from whatsapp_sender import send_whatsapp_message
from logger_module import write_log as log_event

def run_reminder_once():
    try:
        events = get_tomorrow_events()
        if not events:
            log_event("Nessun evento trovato per domani.")
            return

        for ev in events:
            summary = ev.get("title", "Evento senza titolo")
            number = ev.get("number")
            time_str = ev.get("time", "orario sconosciuto")

            if not number:
                log_event(f"Evento '{summary}' ignorato (nessun numero).")
                continue

            msg = f"📅 Promemoria: {summary} alle {time_str}"
            send_whatsapp_message(number, msg)
            log_event(f"Messaggio inviato a {number}: {summary} ({time_str})")

        log_event("✔️ Tutti i promemoria inviati con successo.")

    except Exception as e:
        log_event(f"❌ Errore durante l'esecuzione del reminder: {e}")
