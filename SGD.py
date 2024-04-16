import os
import re, io
import joblib
import numpy as np
from Stemmer import Stemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
import json

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

class SGD:
    def __init__(self, file = "model/model.txt") -> None:
        self.file = file
        self.open_ai = self.openai()
        self.text_clf = self.open_ai[0]
        self.D = self.open_ai[1]
        
    def openai(self):
        print()
        if not (os.path.exists("model/sgd_dict.json")):
            print("D - не найден. Тренировка")
            data = self.load_data()
            D = self.train_test_split(data)
            with open("model/sgd_dict.json", 'w') as f:
                json.dump(D, f)
        else:
            print("D - обнаружен. Загружаем")
            D = json.load(open("model/sgd_dict.json", encoding='utf-8'))
        
        if not (os.path.exists("model/sgd_pipeline.pkl")):
            print("Pipeline - не найден. Тренировка")
            text_clf = Pipeline([
                            ('tfidf', TfidfVectorizer()),
                            ('clf', SGDClassifier(loss='hinge')),
                            ])
            parameters = {}
            text_clf = GridSearchCV(text_clf, parameters, cv=2, verbose=1)
            text_clf.fit(D['train']['x'], D['train']['y'])
            
            joblib.dump(text_clf.best_estimator_, 'model/sgd_pipeline.pkl', compress = 1)
        else:
            print("Pipeline - обнаружен. Загружаем")
            text_clf = joblib.load("model/sgd_pipeline.pkl")
        print()
        return text_clf, D


    def request(self, text) -> tuple[str, str]:
        # Начало тестирования программы
        zz = []
        zz.append(text)
        predicted = self.text_clf.predict(self.D['train']['x'] )
        predicted = self.text_clf.predict(zz) 
        answer = predicted[0].strip()
        # with io.open('model/model.txt', mode='a', encoding='utf-8') as f:
        #     if input('Правильно? (нет) ') == 'нет':
        #         print('Выберите правильный ответ:\n1. GPT\n2. экран\n3. вебка\n4. личный')
        #         truth = input()
        #         if truth == '1': truth = 'GPT'
        #         elif truth == '2': truth = 'экран'
        #         elif truth == '3': truth = 'вебка'
        #         elif truth == '4': truth = 'личный'
                
        #         f.write(f'\n{text} @ {truth}')
        #         print('Добавил. Спасибо)')
        #     else:
        #         f = open('model/model.txt', mode='r+', encoding='utf-8')
        #         if f'{text} @' not in f.read():
        #             f.write(f'\n{text} @ {answer}')
        #         del f
        #         print('Какой же я молодец)')

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

