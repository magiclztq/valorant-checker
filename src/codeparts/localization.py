import json
import os

class LocalizationBase:
    localizer = None

    @staticmethod
    def initialize(lang:str):
        LocalizationBase.localizer = Localization(lang)

class Localization:
    def __init__(self, lang: str) -> None:
        self.lang = lang
        self.data = self.load_localization()

    def find_localization_files(self):
        localization_dir = os.path.join(os.getcwd(), 'local')
        files = os.listdir(localization_dir)
        localization_files = [file for file in files if file.endswith('.json')]
        return localization_files

    def load_localization(self):
        filename = f"{self.lang.lower()}.json"
        localization_dir = os.path.join(os.getcwd(), 'local', filename)

        if os.path.exists(localization_dir):
            with open(localization_dir, 'r', encoding='utf-8') as f:
                phrases = json.load(f)
                return phrases
        else:
            raise FileNotFoundError(f"Localization file {filename} not found.")
