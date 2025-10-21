import schedule
import time
import subprocess
from logger_execution import write_log

def run_main():
    """Esegue lo script principale e registra il log."""
    try:
        write_log("Esecuzione automatica avviata alle 07:00.")
        subprocess.run(["python", "main.py"], check=True)
        write_log("Esecuzione completata con successo.")
    except subprocess.CalledProcessError as e:
        write_log(f"Errore durante l'esecuzione automatica: {e}")
    except Exception as ex:
        write_log(f"Errore sconosciuto: {ex}")

# Pianifica l’esecuzione ogni giorno alle 07:00
schedule.every().day.at("07:00").do(run_main)

write_log("⏰ Scheduler avviato e in attesa delle 07:00.")

while True:
    schedule.run_pending()
    time.sleep(60)
