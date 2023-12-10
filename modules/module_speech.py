import json
import os
import wave
import pyaudio
import urllib.request
from pvporcupine import Porcupine
from pvrecorder import PvRecorder
import librosa
import sounddevice as sd
import threading

os.chdir('C:/Users/aralm/YandexDisk/Code_Python/NeuroGPT')

from modules.config import FORMAT, channels, chunk, \
    sample_rate, record_seconds, IAM_TOKEN, FOLDER_ID

class AudioRecord:
    def __init__(self) -> None:
        pass

    def wake_word_check(self, porcupine: Porcupine) -> None:
        """
        porcupine: Porcupine
            Мониторит микрофон, на Wake Word, после 
        """

        recoder = PvRecorder(device_index=-1, frame_length=porcupine.frame_length)
        try:
            audio, sample_rate = librosa.load('model\Sounds\Activate.mp3')
            recoder.start()
            print('\nЖдём wakeword..')
            while True:
                keyword_index = porcupine.process(recoder.read())
                if keyword_index >= 0:
                    print(':', end='')
                    try:
                        return True
                        self.record(audio, recoder, audio, "recorded.wav") # Записываем аудио в wav
                    except KeyboardInterrupt:
                        porcupine.delete()
                        print('Отмена')
                        continue
            
                    self.convert_wav_opus("recorded.wav", "output.opus") # Переводим в opus (Для работы со speechkit)
                    return self.recognise_audio("output.opus")
        finally:
            porcupine.delete()
            recoder.delete()


    def record(self, recoder, audio, filename_wav) -> bool:
        """
            Эта функция служит для записи аудио в формат wav
        """
        if recoder: recoder.stop()
        audio_thread = threading.Thread(target=sd.play, kwargs={"data" : audio, "samplerate": sample_rate, "blocking": True})
        audio_thread.start()
        # sd.play(audio, sample_rate, blocking=True) # воспроизводим звук активации 
        print(f" Я Вас слушаю")
        
        p = pyaudio.PyAudio()
        # открыть объект потока как ввод и вывод
        stream = p.open(format=FORMAT,
                        channels=channels,
                        rate=sample_rate,
                        input=True,
                        output=True,
                        frames_per_buffer=chunk)
        frames = []

        print("Произнесите команду..")
        for i in range(int(sample_rate / chunk * record_seconds)):
            data = stream.read(chunk)
            frames.append(data)
            
        print("[INFO] Запись завершена.")
        stream.stop_stream()
        stream.close()
        p.terminate()
        wf = wave.open(filename_wav, "wb")
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(sample_rate)
        wf.writeframes(b"".join(frames))
        wf.close()

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

        url = urllib.request.Request("https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?%s" % params, data=audiodata)
        # Authentication via the IAM token.
        url.add_header("Authorization", "Bearer %s" % IAM_TOKEN)

        responseData = urllib.request.urlopen(url).read().decode('UTF-8')
        decodedData = json.loads(responseData)

        if decodedData.get("error_code") is None:
            return decodedData.get("result")

    def synthesize_speech(self, text) -> str:
        """
            Принимает на вход текст. Далее возвращает название сохранённого аудиофайла
        """

