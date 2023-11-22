from config import CHAT_GPT_API, PROXIES
import g4f
class GPT:
    def __init__(self) -> None:
        self.api_key = CHAT_GPT_API
        self.proxies = PROXIES
        g4f.debug.logging = True  # Enable logging

    def request(self, prompt) -> str:
        response = g4f.ChatCompletion.create(
            model=g4f.models.gpt_35_turbo_0613,
            messages=[{"role": "user", "content": prompt}],
        )  
        
        return response



def main():
    gpt = GPT()
    while True:
        text = input('Введи запрос: ')
        print(gpt.request(prompt=text))

main()