import requests
import json
from datetime import datetime
from config_loader import POST_ENDPOINT
from logger_execution import write_log

def send_event_to_calendar(title, description, start_time, end_time):
    payload = {
        "title": title,
        "description": description,
        "start": start_time.isoformat(),
        "end": end_time.isoformat()
    }
    write_log(f"Payload: {payload}")

    response = requests.post(POST_ENDPOINT, data=json.dumps(payload))
    write_log(f"response: {response}")
    if response.status_code == 200:
        print("✅ Risposta:", response.json())
    else:
        print("❌ Errore:", response.text)


if __name__ == "__main__":
    title = input("Titolo evento: ")
    description = input("Descrizione evento: ")

    start_str = input("Data e ora inizio (formato: YYYY-MM-DD HH:MM): ")
    end_str = input("Data e ora fine (formato: YYYY-MM-DD HH:MM): ")

    try:
        start = datetime.strptime(start_str, "%Y-%m-%d %H:%M")
        end = datetime.strptime(end_str, "%Y-%m-%d %H:%M")

        send_event_to_calendar(title, description, start, end)

    except ValueError:
        print("⚠️ Formato data/ora non valido! Usa il formato: YYYY-MM-DD HH:MM")
