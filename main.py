import json
import sys
from time import sleep
import time
import librosa
import numpy as np
import pyaudio
from modules.config import AccesKey_wwd, prompt_template, threshold_ratio
from modules.module_GPT import GPT
# from modules.module_screen import Screen
from googletrans import Translator
from modules.module_webcam import WebCam
from modules.module_speech import AudioRecord
from SGD import SGD
import pvporcupine

from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QApplication,  QMainWindow
import multiprocessing
import sys
import argparse

parser = argparse.ArgumentParser(add_help=False)

parser.add_argument(
    '-t', '--threshhold', 
    choices=[0, 1],
    type=int, 
    help='Запустить сканирование шума (Рекомендуется при каждом запуске)',
    default=1
)
parser.add_argument(
    '-c', '--console',
    choices=[0, 1],
    type=int, 
    help="Запустить WakeWord",
    default=1
)
args = parser.parse_args()



translator = Translator()

class MainWindow(QMainWindow):
    def __init__(self, sgd: SGD) -> None:
        super().__init__()
        
        self.sgd = sgd
        self.gpt = GPT()
        self.Audiorec = AudioRecord(self.sgd, self.gpt)

        uic.loadUi('APP/design.ui', self)

        audio, sample_rate = librosa.load('model\Sounds\Activate.mp3')
        self.voiceButton.clicked.connect(self.main_btn_pressed)
        self.Cancel.clicked.connect(self.cancel_btn_pressed)
        print('Хендлеры UI успешно запущены')

        self.setFixedSize(400, 600)
        self.inspeechLayout_2.hide()

    def run(self):
        app = QtWidgets.QApplication(sys.argv)

    def main_btn_pressed(self):
        """
            Вызывается при нажатии на главную кнопку, а затем запускает основной процесс работы ИИ
        """
        print('Кнопка нажата')
        self.inspeechLayout_2.show()

        try:
            self.Audiorec.finished.connect(self.on_finished)
            self.Audiorec.process_audio.connect(self.on_change_gpt)
            self.gpt.process.connect(self.on_change_gpt)
            self.Audiorec.start()

        except Exception as e:
            print(e)
            quit('Всем спасибо. Всем пока')

    def on_change_gpt(self, state):
        self.listening.setText(state)

    def on_finished(self):
        print("Процедура завершена")
        self.inspeechLayout_2.hide()
        self.listening.setText("Слушаю")

    def cancel_btn_pressed(self):
        """
            Нужна для отмены работы ИИ
        """
        self.Audiorec.terminate()
        self.inspeechLayout_2.hide()
        print("Процедура прервана")


def create_window(sgd):
    app = QApplication(sys.argv)
    window = MainWindow(sgd) 
    window.show()
    
    sys.exit(app.exec())

def console_side_voice(sgd: SGD):
    Audiorec = AudioRecord(sgd)
    print('[INFO] SGD-классификатор обучен')

    camera = None
    gpt = None

    while True:
        try:
            porcupine = pvporcupine.create(
                access_key=AccesKey_wwd,
                keyword_paths=[
                    'model\Гарри_ru_windows_v3_0_0.ppn', 
                    'model\Гарри_ru_windows_v3_0_0_1.ppn'
                ],
                model_path='model\porcupine_params_ru.pv'
                )
            text = Audiorec.wake_word_check(porcupine)
            if len(text) == 0: 
                print("Текст пуст. Заново")
                print(text)
                continue

            prediction = sgd.request(text)[1]
            print(f'Распознано: "{text}"')
            print(f'Предсказание: "{prediction}"')

            if 'вебка' in prediction:
                if camera == None:
                    camera = WebCam()
                num = int(prediction.split()[1])
                mood, name = camera.live_cam(num)
                print(f'Мне кажется ты {mood}')
                print(f'Тебя зовут {name}')                
                if name: 
                    print(f'Тебя зовут {name}')
                    Audiorec.synth_speech(
                        f"Тебя зовут {translator.translate(name, dest = 'ru').text}",
                        block=True
                    )
                if mood:
                    print(f'Мне кажется ты {mood}')
                    Audiorec.synth_speech(
                        f"Мне кажется ты {translator.translate(mood, dest = 'ru').text}",
                        block=True
                    )

            elif prediction == 'GPT':
                if gpt == None:
                    gpt = GPT()
                gpt_response = gpt.request(text)
                Audiorec.synth_speech(gpt_response)

        except KeyboardInterrupt:
            quit()

def noise_treshhold(sample_seconds=3):
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 1024
    
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    print(f"Запись образца тишины началась.\nПомолчите пожалуйста в течение {sample_seconds} секунд...\n")

    frames = []
    for _ in range(int(RATE / CHUNK * sample_seconds)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Запись образца тишины завершена.")

    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Преобразование данных в numpy массив и вычисление среднего значения громкости
    np_frames = np.frombuffer(b''.join(frames), dtype=np.int16)
    volume = np.abs(np_frames).mean() * threshold_ratio

    with open('model/silence_treshhold.cfg', 'w') as f:
        f.write(str(volume))

    return volume

    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)

    frames = []
    print('Берём образец тишины, помолчите')
    start = time.time()
    while time.time() - start <=3:
        data = stream.read(CHUNK)
        frames.append(data)

        # Преобразовать аудио в массив NumPy
        audio_data = np.frombuffer(data, dtype=np.int16)

    average = sum(audio_data)/len(audio_data)
    silence_threshold = 0.0001 * average
    with open('model/silence_treshhold.cfg', 'w') as f:
        f.write(str(silence_threshold))

    print('Образец тишины благополучно взят:', silence_threshold)

    stream.stop_stream()
    stream.close()
    audio.terminate()

    


def main_process():
    with open('model/prompt.json', 'w', encoding='utf-8') as f:
        json.dump(prompt_template, f)

    sgd = SGD("model/model.txt")
    window = multiprocessing.Process(target=create_window, args=[sgd])
    console_side = multiprocessing.Process(target=console_side_voice, args=[sgd])
    silence_test = multiprocessing.Process(target=noise_treshhold)

    window.start()
    if args.threshhold:
        silence_test.start()
        silence_test.join()
    if args.console:
        console_side.start()

    
if __name__ == '__main__':
    main_process()
