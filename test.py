import cv2
from deepface import DeepFace
from multiprocessing import Pool
from functools import partial

class WebCam:
    def __init__(self) -> None:
        pass

    def process_frame(self, frame, face):
        x, y, w, h = face
        response = self.face_rec(frame[y:y+h, x:x+w])
        return (face, response)
    
    def live_cam(self):
        face_classifier = cv2.CascadeClassifier(cv2.samples.findFile(r"C:\Users\aralm\YandexDisk\Code_Python\NeuroGPT\modules\cascade\haarcascade_frontalface_default.xml"))

        cap = cv2.VideoCapture(1)
        # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        pool = Pool()
        new_frame = None  # объявляем переменную перед циклом while

        while True:
            ret, frame = cap.read()
            faces = face_classifier.detectMultiScale(frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            process_frame_partial = partial(self.process_frame, frame)
            results = pool.map(process_frame_partial, faces)

            for (face, response) in results:
                x, y, w, h = face
                cv2.putText(frame, text=response[0]["dominant_emotion"], org=(x, y), fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=1, color=(255, 255, 255))
                new_frame = cv2.rectangle(frame, (x,y), (x+w, y+h), color=(255, 0, 0), thickness=2)

            cv2.imshow("Detecting..", new_frame)

            if cv2.waitKey(30) == 27:
                break

        cap.release()
        cv2.destroyAllWindows()

    def face_rec(self, frame):
        response = DeepFace.analyze(frame, actions=("emotion",), enforce_detection=False)
        return response

cam = WebCam()
cam.live_cam()