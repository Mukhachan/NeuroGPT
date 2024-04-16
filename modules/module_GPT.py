import json
from pprint import pprint
import requests
from modules.config import YANDEX_GPT_API, prompt_template
from PyQt5.QtCore import QThread, pyqtSignal


class GPT(QThread):
    process = pyqtSignal(str)
    def __init__(self) -> None:
        super().__init__()

    def request(self, text) -> str:
        user_name = open("model/user_name.cfg", encoding='utf-8').read()
        with open('model/prompt.json', 'r') as f:
            try:
                prompt = json.load(f)
            except Exception as e:
                print("[Error] Возникла ошибка:", e, "\nНо мы пересоздали json по шаблону")
                with open('model/prompt.json', 'w') as f:
                    json.dump(prompt_template, f)
                with open('model/prompt.json', 'r') as f:   
                    prompt = json.load(f)
        
        prompt['messages'].append({
            "role" : "user",
            "text" : f"{user_name}: {text}"
        })
        
        url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {YANDEX_GPT_API}"
        }
        self.process.emit("Генерирую ответ")
        response = requests.post(url, headers=headers, json=prompt)
        resp_text = response.json()['result']['alternatives'][0]['message']['text']

        self.process.emit("Сохраняю контекст")
        with open('model/prompt.json', 'w', encoding='utf-8') as f:
            prompt['messages'].append({
                "role" : "assistant",
                "text" : resp_text,
            })
            json.dump(prompt, f)

        return resp_text.strip()

