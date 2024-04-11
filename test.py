import time
x = time.time() # Запускаем секундомер

from pprint import pprint

from modules.module_speech import AudioRecord

print(
AudioRecord().synth_speech(
    block=True, 
    text="Привет. У меня всё хорошо, а как твои дела?")
)
print(time.time() - x)
