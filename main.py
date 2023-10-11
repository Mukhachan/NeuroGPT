import os
from modules.config import AccesKey_wwd
# from modules.module_GPT import GPT
# from modules.module_screen import Screen
from modules.module_webcam import WebCam
from modules.module_speech import AudioRecord
from SGD import SGD
import pvporcupine
import keyboard
import threading
os.system('cls')

def my_function():
    print("Моё сочетание клавиш выполнено!")

def clear_term():
    os.system('cls')

def hotkey_thread():
    keyboard.add_hotkey('Ctrl+Alt+A', my_function)
    keyboard.add_hotkey('Ctrl+Alt+C', clear_term)
    keyboard.add_hotkey('Ctrl+C', quit)
    keyboard.wait('Esc')



audio = AudioRecord()
main = SGD('model/model.txt')
print('[INFO] SGD-классификатор обучен')


def main_process(AudioRecord: AudioRecord, SGD: SGD):
    camera = []
    while True:
        try:
            porcupine = pvporcupine.create(
                access_key=AccesKey_wwd,
                keyword_paths=['model\Филипп_ru_windows_v2_2_0.ppn', 'model\WakeWordGarry.ppn', 'model\Гарри_ru_windows_v2_2_0.ppn'],
                model_path='model\porcupine_params_ru.pv'
                )
            
            text = AudioRecord.main(porcupine)
            prediction = SGD.request(text)[1]
            print(f'Распознано: "{text}"')
            print(f'Предсказание: "{prediction}"')
            if prediction == 'вебка':
                if camera == []:
                    camera = [WebCam()]

                mood = camera[0].live_cam()
                print(f'I think you {mood}')
                
        except KeyboardInterrupt:
            quit()

# main_process(audio, main)

#-- Создаём потоки --#
hotkey_thrd = threading.Thread(target=hotkey_thread)
hotkey_thrd.daemon = True
hotkey_thrd.start()


main_thrd = threading.Thread(target=main_process, args=(audio, main))
main_thrd.start()