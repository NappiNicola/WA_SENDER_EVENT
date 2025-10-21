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
