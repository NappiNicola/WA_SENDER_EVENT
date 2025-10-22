import os
from datetime import datetime

LOG_DIR = "execution_logs"

def _ensure_log_dir():
    """Crea la cartella dei log se non esiste."""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

def get_log_filename():
    """Restituisce il nome del file log per il giorno corrente."""
    date_str = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(LOG_DIR, f"log_{date_str}_execution.txt")

def write_log(message: str):
    """Scrive un messaggio nel file di log con timestamp."""
    _ensure_log_dir()
    timestamp = datetime.now().strftime("%H:%M:%S")
    with open(get_log_filename(), "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

def read_log():
    """Legge e restituisce il contenuto del log odierno."""
    filename = get_log_filename()
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()
    return "Nessun log disponibile per oggi."

def read_log_by_filename(filename):
    file_path = os.path.join(LOG_DIR, filename)
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        return "❌ File non trovato o eliminato."

def return_all_log_files():
    _ensure_log_dir()
    solo_file = [f for f in os.listdir(LOG_DIR) if os.path.isfile(os.path.join(LOG_DIR, f))]
    return solo_file  # Restituisce sempre una LISTA, anche vuota

