import sys
from time import sleep
import librosa
from modules.config import AccesKey_wwd
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
                ],
                model_path='model\porcupine_params_ru.pv'
                )
            text = Audiorec.wake_word_check(porcupine)
            if len(text) == 0: continue

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
                        f"Мне кажется ты {translator.translate(mood, dest = 'ru').text}"
                    )

            elif prediction == 'GPT':
                if gpt == None:
                    gpt = GPT()
                gpt_response = gpt.request(text)
                print(gpt_response)
                Audiorec.synth_speech(gpt_response)


        except KeyboardInterrupt:
            quit()


def main_process():

    sgd = SGD("model/model.txt")
    window = multiprocessing.Process(target=create_window, args=[sgd])
    # console_side = multiprocessing.Process(target=console_side_voice, args=[sgd])

    window.start()
    # console_side.start()

    
if __name__ == '__main__':
    main_process()
