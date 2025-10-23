import json
from pathlib import Path

CONFIG_FILE = Path("config.json")

DEFAULT_CONFIG = {
    "API_URL": "",
    "POST_ENDPOINT":"",
    "MY_PHONE": []
}

def load_config():
    if not CONFIG_FILE.exists():
        with open(CONFIG_FILE, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        return DEFAULT_CONFIG

    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

config = load_config()

API_URL = config["API_URL"]
MY_PHONE = config["MY_PHONE"]
POST_ENDPOINT = config["POST_ENDPOINT"]
