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
    def __init__(self, WakeWordRecognizing: WakeWordRecognizing, Audiorec: AudioRecord, sgd: SGD) -> None:
        super(MainWindow, self).__init__()
        self.Audiorec = Audiorec
        self.sgd = sgd
        self.WakeWordRecognizing = WakeWordRecognizing
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

    # @pyqtSlot(str)
    def main_btn_pressed(self):
        """
            Вызывается при нажатии на главную кнопку, а затем запускает основной процесс работы ИИ
        """
        print('Кнопка нажата')
        
        class MyThread(threading.Thread):
            def __init__(self, target, args=()):
                super().__init__(target=target, args=args)
                self._result = None

            def run(self):
                self._result = self._target(*self._args)

            def join(self):
                super().join()
                return self._result
        

        subthread1 = threading.Thread(target=self.inspeechLayout_2.show)
        
        audio, sample_rate = librosa.load('model\Sounds\Activate.mp3')
        audio_thread1 = MyThread(target=self.Audiorec.record, args=[None, audio, "recorded.wav"])
        audio_thread2 = MyThread(target=self.Audiorec.convert_wav_opus, args=["recorded.wav", "output.opus"])
        # audio_thread3 = MyThread(target=self.Audiorec.recognise_audio, args=["output.opus"]) 
        subthread2 = threading.Thread(target=self.inspeechLayout_2.hide)
        
        subthread1.start()
        subthread1.join()

        audio_thread1.start()
        audio_thread1.join()
        
        audio_thread2.start()
        audio_thread2.join()
        
        # audio_thread3.start()
        # text = audio_thread3.join()
        # print(text)

        subthread2.start()
        subthread2.join()


        # sgd_process(camera=None, sgd=self.sgd, gpt=None, text=text)
        



    def cancel_btn_pressed(self):
        """
            Нужна для отмены работы ИИ
        """
        self.inspeechLayout_2.hide()


# def main_process():
#     Audiorec = AudioRecord()
#     sgd = SGD('model/model.txt')
#     print('[INFO] SGD-классификатор обучен')
#     camera = None
#     gpt = None
#     while True:
#         try:
#             porcupine = pvporcupine.create(
#                 access_key=AccesKey_wwd,
#                 keyword_paths=[
#                     'model\Филипп_ru_windows_v2_2_0.ppn', 
#                     'model\WakeWordGarry.ppn', 
#                     'model\Гарри_ru_windows_v2_2_0.ppn'
#                 ],
#                 model_path='model\porcupine_params_ru.pv'
#                 )
#             text = Audiorec.main(porcupine)
#             prediction = sgd.request(text)[1]
#             print(f'Распознано: "{text}"')
#             print(f'Предсказание: "{prediction}"')
#             if prediction == 'вебка':
#                 if camera == None:
#                     camera = WebCam()
#                 mood = camera.live_cam()
#                 print(f'I think you {mood}')
#             elif prediction == 'GPT':
#                 if gpt == None:
#                     gpt = GPT()
#                 print(gpt.request(text))

#         except KeyboardInterrupt:
#             quit()
# main_process()
def application():
    Audiorec = AudioRecord()
    sgd = SGD('model/model.txt') 
    print('[INFO] SGD-классификатор обучен')
    app = QApplication(sys.argv)

    
    wake_word_thread = WakeWordThread(Audiorec=Audiorec, sgd=sgd)

    window = MainWindow(WakeWordRecognizing=wake_word_thread, Audiorec=Audiorec, sgd=sgd)
    window = threading.Thread(target=window.show)
    window.start() # Запускаем UI

    wake_word_thread.start()
    wake_word_thread.wake_word_detected.connect(window.main_btn_pressed)
    

    sys.exit(app.exec())

application()