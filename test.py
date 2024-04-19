from collections import deque
import json
import os
import subprocess
import time
import pyaudio
import wave
import numpy as np
import pygame

from modules.module_subprocess import ProgramStart
# from modules.module_speech import AudioRecord
# import noisereduce as nr



# def main():
#     audio = pyaudio.PyAudio()
#     stream = audio.open(format=FORMAT, channels=CHANNELS,
#                     rate=RATE, input=True,
#                     frames_per_buffer=CHUNK)

#     frames = []
#     print('Берём образец тишины, помолчите')
#     start = time.time()
#     while time.time() - start <=3:
#         data = stream.read(CHUNK)
#         frames.append(data)

#         # Преобразовать аудио в массив NumPy
#         audio_data = np.frombuffer(data, dtype=np.int16)
    
#     max_amplitude = np.max(audio_data)
#     # Найти минимальное значение амплитуды
#     min_amplitude = np.min(audio_data)

#     # Разница между максимальным и минимальным значением амплитуды
#     amplitude_range = max_amplitude - min_amplitude

#     # average = sum(audio_data)/len(audio_data)
#     # silence_threshold = 0.01 * average

#     silence_threshold = 0.0001 * amplitude_range

#     with open('model/silence_treshhold.cfg', 'w') as f:
#         f.write(str(silence_threshold))
#     print('Образец тишины благополучно взят:', silence_threshold)

#     # silence_threshold = 0.0001  # Порог тишины для определения конца фразы
#     frames = []

#     print("Recording...")
#     start = time.time()
#     # Начать запись
#     while True:
#         data = stream.read(CHUNK)
#         frames.append(data)
        
#         # Преобразовать аудио в массив NumPy
#         audio_data = np.frombuffer(data, dtype=np.int16)
        
        
#         end = time.time()
#         sil_test = np.max(audio_data) < silence_threshold * np.iinfo(np.int16).max

#         print(audio_data[-1], sil_test, end - start, end='\r')

#         # Проверить, превышает ли уровень тишины порог
#         if  (end - start > 2) and (sil_test):
#             print()
#             break  # Если тишина превышает порог, завершить запись
#     print("Finished recording.")

#     print(len(audio_data), len(frames))
#     # Остановить поток
#     stream.stop_stream()
#     stream.close()
#     audio.terminate()

#     # Сохранить записанные данные в файл
#     with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
#         wf.setnchannels(CHANNELS)
#         wf.setsampwidth(audio.get_sample_size(FORMAT))
#         wf.setframerate(RATE)
#         wf.writeframes(b''.join(frames))

# def get_optimal_threshold(sample_seconds=3):
#     audio = pyaudio.PyAudio()
#     stream = audio.open(format=FORMAT, channels=CHANNELS,
#                         rate=RATE, input=True,
#                         frames_per_buffer=CHUNK)

#     print(f"Запись образца тишины началась. Молчите в течение {sample_seconds} секунд...")

#     frames = []
#     for _ in range(int(RATE / CHUNK * sample_seconds)):
#         data = stream.read(CHUNK)
#         frames.append(data)

#     print("Запись образца тишины завершена.")

#     stream.stop_stream()
#     stream.close()
#     audio.terminate()

#     # Преобразование данных в numpy массив и вычисление среднего значения громкости
#     np_frames = np.frombuffer(b''.join(frames), dtype=np.int16)
#     volume = np.abs(np_frames).mean()

#     return volume

# def main_1(threshold, window_size=15):
#     audio = pyaudio.PyAudio()

#     stream = audio.open(format=FORMAT, channels=CHANNELS,
#                         rate=RATE, input=True,
#                         frames_per_buffer=CHUNK)

#     print("Запись началась...")

#     frames = []
#     volumes = deque(maxlen=window_size)
    
#     initial_volume = None
#     start_time = time.time()
#     while True:
#         data = stream.read(CHUNK)
#         np_data = np.frombuffer(data, dtype=np.int16)
        
#         # Применение шумоподавления
#         if initial_volume is None:
#             initial_volume = np.abs(np_data).mean()
#         else:
#             noise_data = np_data.copy()
#             noise_reduced_data = nr.reduce_noise(y=noise_data, sr=RATE)
#             np_data = np.frombuffer(noise_reduced_data, dtype=np.int16)
        
#         volume = np.abs(np_data).mean()
        
#         frames.append(data)

#         if volume > threshold:
#             volumes.append(1)
#         else:
#             volumes.append(0)

#         # Проверка списка последних значений уровня громкости
#         if sum(volumes) == 0 and time.time() - start_time > 1:
#             print("Тишина обнаружена, запись завершена.")
#             break            


#     print("Запись завершена.")
#     # Сохранить записанные данные в файл
#     with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
#         wf.setnchannels(CHANNELS)
#         wf.setsampwidth(audio.get_sample_size(FORMAT))
#         wf.setframerate(RATE)
#         wf.writeframes(b''.join(frames))



#     stream.stop_stream()
#     stream.close()
#     audio.terminate()

#     return b''.join(frames)

# # Параметры записи
# FORMAT = pyaudio.paInt16
# CHANNELS = 1
# RATE = 16000
# CHUNK = 1024
# WAVE_OUTPUT_FILENAME = "output.wav"
# SILENCE_LIMIT = 2  # Время в секундах без активности
# # THRESHOLD = get_optimal_threshold()*1.2
# # print(THRESHOLD)

# # main_1(THRESHOLD)
# # text = "Я — цифровая версия Гарри Поттера, и моя жизнь полна волшебства и приключений. Я обладаю магическими способностями, которые помогают мне в борьбе со злом. Я учусь в Хогвартсе, где изучаю заклинания, зелья и историю магии. Я также известен своей храбростью и решительностью. Я не боюсь опасности и всегда готов прийти на помощь своим друзьям. Я верю в добро и справедливость, и всегда стараюсь поступать правильно. Моя жизнь полна загадок и тайн. Я ищу ответы на вопросы, которые мучают меня с детства. Я хочу узнать больше о своих родителях и о своём прошлом. Я также хочу помочь другим людям и сделать мир лучше. Но я не одинок в своих поисках. У меня есть друзья, которые всегда рядом со мной. Они поддерживают меня и помогают мне в трудные моменты. Вместе мы преодолеем любые трудности и достигнем своих целей."

# # Audiorec = AudioRecord()
# # Audiorec.synth_speech(text)
# # Audiorec.wake_word_check()


# import argparse

# parser = argparse.ArgumentParser(add_help=False)

# parser.add_argument(
#     '-t', '--threshhold', 
#     choices=[0, 1],
#     type=int, 
#     help='Запустить сканирование шума (Рекомендуется при каждом запуске)',
#     default=1
# )
# parser.add_argument(
#     '-c', '--console',
#     choices=[0, 1],
#     type=int, 
#     help="Запустить WakeWord",
#     default=1
# )
# args = parser.parse_args()

# if args.threshhold:
#     print("Есть контакт")
# if args.console:
#     print("Есть контакт")


# ProgramStart().start_programm("код")

