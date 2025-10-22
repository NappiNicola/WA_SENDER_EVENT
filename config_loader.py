import json
import os
import sys


def load_config():
    """Carica il file di configurazione JSON"""
    base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))  # compatibile anche con PyInstaller
    config_path = os.path.join(base_dir, "config.json")

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"File di configurazione non trovato: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

# Carichiamo i valori
config = load_config()
API_URL = config["API_URL"]
MY_PHONE = config["MY_PHONE"]
