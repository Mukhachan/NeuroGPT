import sys

import librosa
from modules.config import AccesKey_wwd
from modules.module_GPT import GPT
# from modules.module_screen import Screen
from modules.module_webcam import WebCam
from modules.module_speech import AudioRecord
from SGD import SGD
import pvporcupine

from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import pyqtSignal, QObject, QThread
import threading
import multiprocessing
import os



class WakeWordRecognizing(QObject):
    wake_word_detected = pyqtSignal(str)
    def __init__(self, Audiorec: AudioRecord, sgd: SGD) -> None:
        super(WakeWordRecognizing, self).__init__()
        self.Audiorec = Audiorec
        self.sgd = sgd

    def run(self):
        self.camera = None
        self.gpt = None
        while True:
            try:
                porcupine = pvporcupine.create(
                    access_key=AccesKey_wwd,
                    keyword_paths=[
                        'model\Филипп_ru_windows_v2_2_0.ppn', 
                        'model\WakeWordGarry.ppn', 
                        'model\Гарри_ru_windows_v2_2_0.ppn'
                    ],
                    model_path='model\porcupine_params_ru.pv'
                    )
                if self.Audiorec.wake_word_check(porcupine):
                    self.wake_word_detected.emit("WakeWord обнаружен")
                    # audio, sample_rate = librosa.load('model\Sounds\Activate.mp3')
                    # self.Audiorec.record(recoder=None, audio=audio, filename_wav="recorded.wav")
                    # self.Audiorec.convert_wav_opus("recorded.wav", "output.opus")
                    # text = self.Audiorec.recognise_audio("output.opus")

                    # sgd_process(camera=self.camera, sgd=self.sgd, gpt=self.gpt, text=text)

            except KeyboardInterrupt:
                quit()

def sgd_process(camera: WebCam | None, sgd: SGD | None, gpt: GPT | None, text: str) -> None:
    prediction = sgd.request(text)[1]
    print(f'Распознано: "{text}"')
    print(f'Предсказание: "{prediction}"')
    if prediction == 'вебка': # - Запускает оценку эмоция
        if camera == None:
            camera = WebCam()
        mood = camera.live_cam()
        print(f'I think you {mood}')
    elif prediction == 'GPT': # - Отправляет текст в GPT и ждёт ответ
        if gpt == None:
            gpt = GPT()
        print(gpt.request(text))        

class WakeWordThread(QThread):
    wake_word_detected = pyqtSignal(str)
    def __init__(self, Audiorec: AudioRecord, sgd: SGD) -> None:
        super().__init__()
        self.Audiorec = Audiorec
        self.sgd = sgd

    def run(self):
        wake_word_detector = WakeWordRecognizing(self.Audiorec, self.sgd)
        wake_word_detector.wake_word_detected.connect(self.wake_word_detected.emit)
        wake_word_detector.run()
    


class MainWindow(QMainWindow):
    def __init__(self, Audiorec: AudioRecord, sgd: SGD) -> None:
        super(MainWindow, self).__init__()
        self.Audiorec = Audiorec
        self.sgd = sgd
        uic.loadUi('APP/design.ui', self)

        self.btn_handlers()
        self.setFixedSize(400, 600)
        self.inspeechLayout_2.hide()

    def run(self):
        app = QtWidgets.QApplication(sys.argv)

    def btn_handlers(self): 
        self.voiceButton.clicked.connect(self.main_btn_pressed)
        self.Cancel.clicked.connect(self.cancel_btn_pressed)
        print('Хендлеры UI успешно запущены')

    def main_btn_pressed(self):
        """
            Вызывается при нажатии на главную кнопку, а затем запускает основной процесс работы ИИ
        """
        print('Кнопка нажата')

        self.inspeechLayout_2.show()
        
        audio, sample_rate = librosa.load('model\Sounds\Activate.mp3')
        audio_thread1 = multiprocessing.Process(target=self.Audiorec.record, args=[None, audio, "recorded.wav"])
        audio_thread2 = multiprocessing.Process(target=self.Audiorec.convert_wav_opus, args=["recorded.wav", "output.opus"])
        
        try:
            audio_thread1.start()
            audio_thread1.join()
            
            audio_thread2.run()
            audio_thread2.join()
        except Exception as e:
            print(e)
            quit('Да ебись оно всё конём')
        # self.inspeechLayout_2.hide()
        

    def cancel_btn_pressed(self):
        """
            Нужна для отмены работы ИИ
        """
        self.inspeechLayout_2.hide()


def create_window( Audiorec, sgd):
    app = QApplication(sys.argv)
    window = MainWindow(Audiorec=Audiorec, sgd=sgd) 
    window.show()
    
    sys.exit(app.exec())

def console_side_voice(Audiorec: AudioRecord, sgd: SGD):
    camera = None
    gpt = None

    while True:
        try:
            porcupine = pvporcupine.create(
                access_key=AccesKey_wwd,
                keyword_paths=[
                    # 'model\Филипп_ru_windows_v2_2_0.ppn', 
                    'model\WakeWordGarry.ppn', 
                    'model\Гарри_ru_windows_v2_2_0.ppn'
                ],
                model_path='model\porcupine_params_ru.pv'
                )
            text = Audiorec.wake_word_check(porcupine)

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
                gpt_response = gpt.request(text)
                Audiorec.synth_speech(gpt_response)
                print(gpt_response)

        except KeyboardInterrupt:
            quit()


def main_process():
    Audiorec = AudioRecord()
    sgd = SGD('model/model.txt')
    print('[INFO] SGD-классификатор обучен')

    window = multiprocessing.Process(target=create_window, args=[Audiorec, sgd])
    console_side = multiprocessing.Process(target=console_side_voice, args=[Audiorec, sgd])

    window.start()
    console_side.start()

 
if __name__ == '__main__':
    main_process()
