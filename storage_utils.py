import json
import os

CONFIG_FILE = "user_config.json"

class LocalStorage:
    @staticmethod
    def get_user_data():
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        return None

    @staticmethod
    def save_user_data(mobile_number, name):
        data = LocalStorage.get_user_data() or {}
        data.update({"mobile_number": mobile_number, "name": name})
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f)
        return data

    @staticmethod
    def save_relay_url(url):
        data = LocalStorage.get_user_data() or {}
        data["last_relay_url"] = url
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f)

    @staticmethod
    def get_relay_url():
        data = LocalStorage.get_user_data()
        if data:
            return data.get("last_relay_url")
        return None

    @staticmethod
    def is_registered():
        return os.path.exists(CONFIG_FILE)
