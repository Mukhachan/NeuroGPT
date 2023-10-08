import os

from modules.config import AccesKey_wwd
# from modules.module_GPT import GPT
# from modules.module_screen import Screen
# from modules.module_webcam import WebCam
from modules.module_speech import AudioRecord
from SGD import SGD
import pvporcupine

os.system('cls')

audio = AudioRecord()
main = SGD('model/model.txt')
print('[INFO] SGD-классификатор обучен')


def main_process(AudioRecord: AudioRecord, SGD: SGD):
    while True:
        try:
            porcupine = pvporcupine.create(
                access_key=AccesKey_wwd,
                keyword_paths=['model\Филипп_ru_windows_v2_2_0.ppn', 'model\WakeWordGarry.ppn', 'model\Гарри_ru_windows_v2_2_0.ppn'],
                model_path='model\porcupine_params_ru.pv'
                )
            text = AudioRecord.main(porcupine)
            print(f'Распознано: "{text}"')
            print(f'Предсказание: "{SGD.request(text)[1]}"')
            
        except KeyboardInterrupt:
            quit()

main_process(audio, main)