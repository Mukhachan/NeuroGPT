import time
import cv2
from deepface import DeepFace
from collections import Counter

class WebCam:
    def __init__(self) -> None:
        self.face_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def camera_indexes(self):

        index = 0
        arr = []
        i = 10
        while i > 0:
            cap = cv2.VideoCapture(index)
            if cap.read()[0]:
                arr.append(index)
                cap.release()
            index += 1
            i -= 1
        return arr        

    def live_cam(self):
        cap = cv2.VideoCapture(1)
        average_emotion = []
        start_time = time.time()
        while time.time() - start_time < 60:
            ret, frame = cap.read()
            faces = self.face_classifier.detectMultiScale(frame, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40))

            new_frame_available = False  # Дополнительная переменная для проверки обнаружения лиц
            for face in faces:
                # Обработка текущего кадра с лицом
                response = self.face_rec(frame)
                print(response)
                average_emotion.append(response["dominant_emotion"])
                x, y, w, h = face
                cv2.putText(frame, text=response["dominant_emotion"], org=(x, y), fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=1, color=(255, 255, 255))
                new_frame = cv2.rectangle(frame, (x, y), (x + w, y + h), color=(255, 0, 0), thickness=2)
                new_frame_available = True  # Устанавливаем флаг, что новый кадр с лицом доступен

            cv2.imshow("Detecting..", new_frame if new_frame_available else frame)  # Показываем новый кадр с лицом, если он доступен, иначе исходный кадр

            if cv2.waitKey(30) == 27:
                break

        cap.release()
        cv2.destroyAllWindows()

        return Counter(average_emotion).most_common()[0][0]


    def face_rec(self, frame):
        response = DeepFace.analyze(frame, actions=("emotion",), enforce_detection = False)
        return response[0]

WebCam().live_cam()