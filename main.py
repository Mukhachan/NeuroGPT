import io
import os
import re

import numpy as np
from Stemmer import Stemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

import pyaudio
import speech_recognition
from config import BOT_NAME

from module_GPT import GPT
from module_screen import Screen
from module_webcam import WebCam

os.system('cls')

class SGD:
    def __init__(self, file) -> None:
        self.file = file
        self.text_clf = self.openai()[0]
        self.D = self.openai()[1]
        
    def openai(self):
        data = self.load_data()
        D = self.train_test_split(data)
        text_clf = Pipeline([
                        ('tfidf', TfidfVectorizer()),
                        ('clf', SGDClassifier(loss='hinge')),
                        ])
        text_clf.fit(D['train']['x'], D['train']['y'])
        return text_clf, D

    def request(self, text):
        # Начало тестирования программы
        zz = []
        zz.append(text)
        predicted = self.text_clf.predict( self.D['train']['x'] )
        predicted = self.text_clf.predict(zz) 
        answer = predicted[0].strip()
        print(answer)
        with io.open('model/model.txt', mode='a', encoding='utf-8') as f:
            if input('Правильно? (нет) ') == 'нет':
                print('Выберите правильный ответ:\n1. GPT\n2. экран\n3. вебка\n4. личный')
                truth = input()
                if truth == '1': truth = 'GPT'
                elif truth == '2': truth = 'экран'
                elif truth == '3': truth = 'вебка'
                elif truth == '4': truth = 'личный'
                
                f.write(f'\n{text} @ {truth}')
                print('Добавил. Спасибо)')
            else:
                if f'{text} @' not in f.read():
                    f.write(f'\n{text} @ {answer}')
                print('Какой же я молодец)')

        return text, answer

    # очистка текста с помощью regexp приведение слов в инфинитив и нижний регистр, замена цифр
    def text_cleaner(self, text):
        text = text.lower() # приведение в lowercase 
        stemmer = Stemmer('russian')
        text = ' '.join( stemmer.stemWords( text.split() ) ) 
        text = re.sub( r'\b\d+\b', ' digit ', text ) # замена цифр 
        return  text 
    # загрузка данных из файла
    def load_data(self):   
        data = {'text':[],'tag':[]}
        for line in io.open(self.file, encoding='utf-8'):
            if not('#' in line):
                row = line.split("@") 
                data['text'] += [row[0]]
                data['tag'] += [row[1]]
        return data
    # Обучение 
    def train_test_split(self, data, validation_split = 0.1):
        sz = len(data['text'])
        indices = np.arange(sz)
        np.random.shuffle(indices)

        X = [data['text'][i] for i in indices]
        Y = [data['tag'][i] for i in indices]
        nb_validation_samples = int( validation_split * sz )

        return { 
            'train': {'x': X[:-nb_validation_samples], 'y': Y[:-nb_validation_samples]},
            'test': {'x': X[-nb_validation_samples:], 'y': Y[-nb_validation_samples:]}
        }

sr = speech_recognition.Recognizer()
with speech_recognition.Microphone() as mic:
    sr.adjust_for_ambient_noise(source=mic)
    print('Шумодав отработал')
main = SGD('model/model.txt')
print('Модель sgd обучена')

def listen() -> str:
    try:    
        with speech_recognition.Microphone() as mic:
            print(':')
            audio = sr.listen(source=mic)
            query = sr.recognize_google(audio, language='ru-RU')
            return query.lower()
        
    except KeyboardInterrupt:
        print('Прощай)')
    except:
        return ''

while True: 
    text = listen()
    print(text)
    ratio = process.extractOne(BOT_NAME, text.split())
    # 'бобби' in text 
    print(ratio)
    if ratio == None: continue

    if ratio[1] > 65: 
        text = text.replace(ratio[0], '', 1).strip()
        print(main.request(text))

