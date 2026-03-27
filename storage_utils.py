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
        data = {"mobile_number": mobile_number, "name": name}
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f)
        return data

    @staticmethod
    def is_registered():
        return os.path.exists(CONFIG_FILE)
