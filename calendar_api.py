import requests

def get_tomorrow_events(api_url: str):
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        events = response.json()
        return events
    except Exception as e:
        print(f"❌ Errore nella richiesta API: {e}")
        return []
