import requests
from modules.config import FOLDER_ID, YANDEX_GPT_IDENTIFY, YANDEX_GPT_API, \
                            maxTokens
from PyQt5.QtCore import QThread, pyqtSignal


class GPT(QThread):
    process = pyqtSignal(str)
    def __init__(self) -> None:
        super().__init__()

    def request(self, prompt) -> str:
        user_name = open(r"model\user_name.cfg", encoding='utf-8').read()
        prompt = {
            "modelUri": f"gpt://{FOLDER_ID}/yandexgpt-lite/latest",
            "completionOptions": {
                "stream": False,
                "temperature": 0.3,
                "maxTokens": maxTokens
            },
            "messages": [
                {
                    "role": "system",
                    "text": "Представь что ты Гарри Поттер." + \
                    "Ты обитаешь в компьютере и являешься цифровой версией "  +\
                    "Гарри Поттера из книги про Гарри Поттера автора Джоан Роулинг. " +\
                    f"С тобой общаюсь я, твой пользователь - {user_name}, но это не диалог. " +\
                    "Во время ответа необязательно упоминать моё имя, но " +\
                    "это можно сделать, чтобы он был более очеловеченным." +\
                    "Также ты обязан давать свои ответы на языке SSML"
                },
                {
                    "role": "user",
                    "text": prompt
                }
            ]
        }

        url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {YANDEX_GPT_API}"
        }
        self.process.emit("Генерирую ответ")
        response = requests.post(url, headers=headers, json=prompt)
        
        return response.json()['result']['alternatives'][0]['message']['text']

