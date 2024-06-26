from collections import deque
import json
import os
from pprint import pprint
import time
import wave
import numpy as np
import pyaudio
import urllib.request
import urllib.parse

from pvporcupine import Porcupine
from pvrecorder import PvRecorder
import librosa
import pygame
import sounddevice as sd
import noisereduce as nr
from pydub import AudioSegment

import io
import multiprocessing
from googletrans import Translator



from modules.module_subprocess import ProgramStart
from modules.module_webcam import WebCam

from PyQt5.QtCore import QThread, pyqtSignal

import requests
import uuid
import ssl

import urllib3
from SGD import SGD
from modules.config import FORMAT, AccesKey_wwd, channels, chunk, \
    sample_rate, record_seconds, FOLDER_ID, \
    SberAuth, synth_format, synth_voice, filename_ogg, oauth
from modules.module_GPT import GPT


try: _create_unverified_https_context = ssl._create_unverified_context
except AttributeError: pass
else: ssl._create_default_https_context = _create_unverified_https_context

translator = Translator()

os.chdir('C:/Users/aralm/YandexDisk/Code_Python/NeuroGPT')



class AudioRecord(QThread):
    finished = pyqtSignal()
    process_audio = pyqtSignal(str)
    def __init__(self, sgd: SGD = SGD, gpt: GPT = None) -> None:
        super().__init__()

        self.sgd = sgd
        self.gpt = gpt
        self.camera = None
        self.programm_start = None
        self.audio, sample_rate = librosa.load('model\Sounds\Activate.mp3')
        self.audio_thread = multiprocessing.Process(target=sd.play, 
                                                    kwargs={
                                                        "data" : self.audio, 
                                                        "samplerate": sample_rate, 
                                                        "blocking": False
                                                        })

    def run(self):
        self.record(None, "recorded.wav")
        self.convert_wav_opus("recorded.wav", "output.opus")

        text = self.recognise_audio("output.opus")
        if len(text) == 0: 
            self.finished.emit()
            print("Текст пуст. Заново")
            print(text)
            return

        prediction: str = self.sgd.request(text)[1]

        print(f'Распознано: "{text}"')
        print(f'Предсказание: "{prediction}"')

        if 'вебка' in prediction:
            if self.camera == None:
                self.camera = WebCam()
            num = int(prediction.split()[1])
            mood, name = self.camera.live_cam(num)
            print(f'Мне кажется ты {mood}')
            print(f'Тебя зовут {name}')
            if name: 
                self.synth_speech(
                    f"Тебя зовут {translator.translate(name, dest = 'ru', src='en').text}",
                    block=True
                    )
            if mood:
                self.synth_speech(
                    f"Мне кажется ты {translator.translate(mood, dest = 'ru', src='en').text}"
                    )

        elif prediction == 'GPT':
            if self.gpt == None:
                self.gpt = GPT()
            gpt_response = self.gpt.request(text)
            self.process_audio.emit("Рассказываю")
            self.synth_speech(gpt_response)
        

        elif prediction == "программа":
            text = text.replace("запусти", "").replace("включи", "").replace("стартани", "")
            if self.programm_start == None:
                self.programm_start = ProgramStart()

            self.synth_speech(self.programm_start.start_programm(text)[1])

        self.finished.emit()

    def wake_word_check(self, porcupine: Porcupine = None) -> str:
        """
        porcupine: Porcupine
            Мониторит микрофон, на Wake Word
        """
        recoder = PvRecorder(frame_length=porcupine.frame_length)
        try:
            recoder.start() 
            print(f"\nRecorder: {recoder.is_recording}")
            print('Ждём wakeword..')
            while True:
                keyword_index = porcupine.process(recoder.read())
                if keyword_index >= 0:
                    print(':', end='')
                    try:
                        self.record(recoder, "recorded.wav") # Записываем аудио в wav
                        
                    except KeyboardInterrupt:
                        recoder.delete()
                        print('Отмена')
                        recoder = PvRecorder(frame_length=porcupine.frame_length)
                        continue
            
                    self.convert_wav_opus("recorded.wav", "output.opus") # Переводим в opus (Для работы со speechkit)
                    return self.recognise_audio("output.opus")  
        finally:
            porcupine.delete()
            recoder.delete()

    def record(self, recoder, filename_wav, window_size: int = 15) -> bool:
        """
            Эта функция служит для записи аудио в формат wav
        """
        audio = pyaudio.PyAudio()

        stream = audio.open(format=FORMAT, channels=channels,
                            rate=sample_rate, input=True,
                            frames_per_buffer=chunk)
        threshold = float(open('model/silence_treshhold.cfg', encoding='utf-8').read().strip())

        self.audio_thread.run() # Воспроизводим звук запуска
        print("Запись началась...")
        frames = []
        volumes = deque(maxlen=window_size)
        
        initial_volume = None
        start_time = time.time()
        while True:
            data = stream.read(chunk)
            np_data = np.frombuffer(data, dtype=np.int16)
            
            # Применение шумоподавления
            if initial_volume == None:
                initial_volume = np.abs(np_data).mean()
            else:
                noise_data = np_data.copy()
                noise_reduced_data = nr.reduce_noise(y=noise_data, sr=sample_rate)
                np_data = np.frombuffer(noise_reduced_data, dtype=np.int16)
            
            volume = np.abs(np_data).mean()
            frames.append(data)

            if volume > threshold:
                volumes.append(1)
            else:
                volumes.append(0)

            # Проверка списка последних значений уровня громкости
            if (sum(volumes) == 0) and (time.time() - start_time > 2):
                print("Тишина обнаружена, запись завершена.")
                break            
        
        print()
        # Сохранить записанные данные в файл
        with wave.open(filename_wav, 'wb') as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(sample_rate)
            wf.writeframes(b''.join(frames))

        stream.stop_stream()
        stream.close()
        audio.terminate()

        return b''.join(frames)
        
        
        if recoder: recoder.stop()

        # p = pyaudio.PyAudio()
        # # открыть объект потока как ввод и вывод
        # stream = p.open(format=FORMAT,
        #                 channels=channels,
        #                 rate=sample_rate,
        #                 input=True,
        #                 output=True,
        #                 frames_per_buffer=chunk)
        # frames = []

        
        # print(f" Я Вас слушаю")
        # self.audio_thread.run() # Воспроизводим звук запуска
        # print("Произнесите команду..")
        # for i in range(int(sample_rate / chunk * record_seconds)):
        #     data = stream.read(chunk)
        #     frames.append(data)
            
        # print("[INFO] Запись завершена.")
        # stream.stop_stream()
        # stream.close()
        # p.terminate()
        # wf = wave.open(filename_wav, "wb")
        # wf.setnchannels(channels)
        # wf.setsampwidth(p.get_sample_size(FORMAT))
        # wf.setframerate(sample_rate)
        # wf.writeframes(b"".join(frames))
        # wf.close()

        audio = pyaudio.PyAudio()

        stream = audio.open(format=FORMAT, channels=channels,
                        rate=sample_rate, input=True,
                        frames_per_buffer=chunk)

        frames = []
        silence_threshold = float(open('model/silence_treshhold.cfg', encoding='utf-8').read().strip())

        print(" Я Вас слушаю")
        self.audio_thread.run() # Воспроизводим звук запуска
        start = time.time()
        # Начать запись
        while True:
            data = stream.read(chunk)
            frames.append(data)
            
            # Преобразовать аудио в массив NumPy
            audio_data = np.frombuffer(data, dtype=np.int16)
            
            end = time.time()
            sil_test = np.max(audio_data) < silence_threshold * np.iinfo(np.int16).max
            print(end - start, sil_test, end='', sep='')

            # Проверить, превышает ли уровень тишины порог
            if  (end - start > 2) and (sil_test):
                break  # Если тишина превышает порог, завершить запись

        print("[INFO] Запись завершена.")

        # Остановить поток
        stream.stop_stream()
        stream.close()
        audio.terminate()

        # Сохранить записанные данные в файл
        with wave.open(filename_wav, 'wb') as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(sample_rate)
            wf.writeframes(b''.join(frames))

        return True

    def convert_wav_opus(self, filename_wav, filename_opus) -> bool:
        """
            Нужна для того что бы преобразовать wav в opus
        """
        command = f'ffmpeg -y -i {filename_wav} -c:a libopus {filename_opus} >{os.devnull} 2>&1' #
        os.system(command)
        os.remove(filename_wav)
        return True

    def recognise_audio(self, filename_opus) -> str:
        """
            Эта функция отправляет аудиозапись формата opus в yandex speechkit и возвращает распознанный текст
        """
        with open(filename_opus, "rb") as f:
            audiodata = f.read()
        os.remove(filename_opus)

        params = "&".join([
            "topic=general",
            "folderId=%s" % FOLDER_ID,
            "lang=ru-RU"
        ])

        url = urllib.request.Request(
            "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?%s" % params, 
            data=audiodata
            )
        url.add_header("Authorization", "Bearer %s" % self.get_iam())

        responseData = urllib.request.urlopen(url).read().decode('UTF-8')
        decodedData = json.loads(responseData)

        if decodedData.get("error_code") is None:
            text = decodedData.get("result")
            return text

    def play_and_del(self):
        # audio, sample_rate = sf.read(
        #     filename_ogg, 
        #     dtype="float32",
        #     stop=-1
        #     )
        
        # sd.play(
        #     audio, 
        #     samplerate=sample_rate, 
        #     blocking=True, 
        #     loop=False
        #     )
        # sd.wait()

        pygame.mixer.init()
        pygame.mixer.music.load(filename_ogg)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():  # if True, the melody is being played
            time.sleep(1)

        pygame.mixer.music.unload()
        os.remove(filename_ogg)

    def synth_speech(self, text: str, block: bool = False) -> bool:
        """
            Принимает на вход текст. Далее возвращает статус выполнения задачи
        """
        print(f"Длина текста {len(text)}")
        print(f"Сообщение:\n{text}")

        # text = text[:4000] if len(text)>4000 else text

        headers = {
            'Authorization' : f"Bearer {self.get_access()['access_token']}",
            'Content-Type' : 'application/text',
        }
        response = urllib3.request('POST', 
            f'https://smartspeech.sber.ru/rest/v1/text:synthesize?format={synth_format}&voice={synth_voice}', 
            headers=headers, body=text)


        # data = urllib.parse.urlencode(text)
        # data = text.encode('utf-8')
        # response = urllib.request.Request(
        #     f'https://smartspeech.sber.ru/rest/v1/text:synthesize?format={synth_format}&voice={synth_voice}',
        #     headers=headers,
        #     data=data,
        #     method='POST'
        # )
        # response = requests.post(
        #     url=f'https://smartspeech.sber.ru/rest/v1/text:synthesize?format={synth_format}&voice={synth_voice}',
        #     data=data,
        #     headers=headers,
        #     # stream=True
        # )

        # print("Status_code: ", response.status_code)
        try:
            if response.status == 200:
                audio_data = io.BytesIO(response.data)
                audio = AudioSegment.from_file(audio_data, format="ogg", start_second=0)
                audio.export(filename_ogg, format="ogg")
                
                # with open(filename_ogg, 'wb') as x:
                #     with io.BytesIO(response.content) as f:
                #         x.write(f)

                # with urllib.request.urlopen(response) as response:
                #     with open(filename_ogg, 'wb') as f:
                #         f.write(bytes(response.read()))

                # with io.BytesIO(response.data) as f:
                #     data, sample_rate = sf.read(f)
                #     sf.write(
                #         filename_ogg, 
                #         data, 
                #         sample_rate
                #     )
            else:
                print(f"Bad response: {response.status}")
        except Exception as e:
            print(f"Возникла ошибка при сохранении аудио {e}")
            return False
        
        if block:
            self.play_and_del()
        else:
            proc = multiprocessing.Process(target=self.play_and_del)
            proc.run()

        return True

    def get_access(self):
        headers = {
            'Authorization': f'Basic {SberAuth}',
            'RqUID': str(uuid.uuid4()),
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        data = {
            'scope': 'SALUTE_SPEECH_PERS'
        }
        response = requests.post('https://ngw.devices.sberbank.ru:9443/api/v2/oauth', headers=headers, data=data)

        return json.loads(response.text.replace('\n', ''))
    
    def get_iam(self):

        headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
        }
        data = '{"yandexPassportOauthToken": "' + oauth + '"}'

        response = requests.post('https://iam.api.cloud.yandex.net/iam/v1/tokens', headers=headers, data=data)

        return json.loads(response.text.replace('\n', ''))['iamToken']

