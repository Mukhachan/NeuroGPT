import os
from modules.config import AccesKey_wwd
from modules.module_GPT import GPT
# from modules.module_screen import Screen
from modules.module_webcam import WebCam
from modules.module_speech import AudioRecord
from SGD import SGD
import pvporcupine
os.system('cls')


def main_process():
    Audiorec = AudioRecord()
    sgd = SGD('model/model.txt')
    print('[INFO] SGD-классификатор обучен')
    camera = None
    gpt = None
    while True:
        try:
            porcupine = pvporcupine.create(
                access_key=AccesKey_wwd,
                keyword_paths=['model\Филипп_ru_windows_v2_2_0.ppn', 'model\WakeWordGarry.ppn', 'model\Гарри_ru_windows_v2_2_0.ppn'],
                model_path='model\porcupine_params_ru.pv'
                )
            text = Audiorec.main(porcupine)
            prediction = sgd.request(text)[1]
            print(f'Распознано: "{text}"')
            print(f'Предсказание: "{prediction}"')
            if prediction == 'вебка':
                if camera == None:
                    camera = WebCam()
                mood = camera.live_cam()
                print(f'I think you {mood}')
            elif prediction == 'GPT':
                if gpt == None:
                    gpt = GPT()
                print(gpt.request(text))

                
        except KeyboardInterrupt:
            quit()

main_process()


