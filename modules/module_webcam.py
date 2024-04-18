import time
from cv2 import CascadeClassifier, VideoCapture, imshow, putText, rectangle, \
	destroyAllWindows, waitKey, data, FONT_HERSHEY_COMPLEX
from deepface.DeepFace import find, analyze 
from collections import Counter
from modules.config import CAMERA_INDEX
import pandas as pd

class WebCam:
	def __init__(self) -> None:
		self.face_classifier = CascadeClassifier(
			data.haarcascades + 'haarcascade_frontalface_default.xml')

	def live_cam(self, detect_pers: int):
		"""
			`detect_pers` == 0, то определяем только личность человека,
			`detect_pers` == 1, то определяем эмоции,
			`detect_pers` == 2, определяем и то и то.
			`detect_pers` == 3, просто посмотреть на себя
		"""
		cap = VideoCapture(CAMERA_INDEX)
		start_time = time.time()

		if detect_pers == 0:  # Определяем личность
			person = []
			while time.time() - start_time <= 15:
				ret, frame = cap.read()
				faces = self.face_classifier.detectMultiScale(
					frame, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40))
				new_frame_available = False  # Дополнительная переменная для проверки обнаружения лиц
				for face in faces:
					# Обработка текущего кадра с лицом
					response, dfs = self.face_rec(frame, detect_pers)
					try:
						dfs = dfs['identity'][0].replace("\\", "/").split("/")[2] if dfs['identity']!={} else "Unknown"
					except Exception as e:
						print("ОШИБКА", e)
						print(dfs)

					person.append(dfs)

					x, y, w, h = face
					putText(frame, text=dfs, org=(
						x, y), fontFace=FONT_HERSHEY_COMPLEX, fontScale=1, color=(0, 255, 0))
					
					new_frame = rectangle(
						frame, (x, y), (x + w, y + h), color=(255, 0, 0), thickness=2)
					
					new_frame_available = True  # Устанавливаем флаг, что новый кадр с лицом доступен

				imshow("Detecting..", new_frame if new_frame_available else frame)

				if waitKey(1) & 0xFF == ord('q'): break

			cap.release()
			destroyAllWindows()
			person = Counter(person).most_common()[0][0] if person else "Unknown"

			open(r"model\user_name.cfg", "w", encoding='utf-8').write(person)
			return None, person

		elif detect_pers == 1: # Оцениваем эмоции
			average_emotion = []
			
			while time.time() - start_time <= 15:
				ret, frame = cap.read()
				faces = self.face_classifier.detectMultiScale(
					frame, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40))

				new_frame_available = False  # Дополнительная переменная для проверки обнаружения лиц
				for face in faces:
					# Обработка текущего кадра с лицом
					response, dfs = self.face_rec(frame, detect_pers)
					average_emotion.append(response["dominant_emotion"])
					x, y, w, h = face
					putText(frame, text=response["dominant_emotion"], org=(x, y), 
						fontFace=FONT_HERSHEY_COMPLEX, fontScale=1, color=(255, 255, 255))
					new_frame = rectangle(
						frame, (x, y), (x + w, y + h), color=(255, 0, 0), thickness=2)
					new_frame_available = True  # Устанавливаем флаг, что новый кадр с лицом доступен

				imshow("Detecting..",
						   new_frame if new_frame_available else frame)

				if waitKey(1) & 0xFF == ord('q'): break
			
			cap.release()
			destroyAllWindows()

			return (
				(Counter(average_emotion).most_common()[0][0] if average_emotion else "Unknown"),
				None
				)
		
		elif detect_pers == 2: # Определяем и то и то.
			average_emotion = [] 
			person = []
			while time.time() - start_time <= 30:
				ret, frame = cap.read()
				faces = self.face_classifier.detectMultiScale(
					frame, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40))

				new_frame_available = False  # Дополнительная переменная для проверки обнаружения лиц
				for face in faces:
					# Обработка текущего кадра с лицом
					response, dfs = self.face_rec(frame, detect_pers)
					average_emotion.append(response["dominant_emotion"])

					try:
						dfs = dfs['identity'][0].replace("\\", "/").split("/")[2] if dfs['identity']!={} else "Unknown"

					except Exception as e:
						print("ОШИБКА", e)
						print(dfs)
					person.append(dfs)
					x, y, w, h = face
					putText(frame, text=dfs, org=(x, y), 
						fontFace=FONT_HERSHEY_COMPLEX, fontScale=1, color=(0, 255, 0))
					putText(frame, text=response["dominant_emotion"], org=(x, y-40), 
						fontFace=FONT_HERSHEY_COMPLEX, fontScale=1, color=(255, 255, 255))
					
					new_frame = rectangle(
					frame, (x, y), (x + w, y + h), color=(255, 0, 0), thickness=2)

					
					new_frame_available = True  # Устанавливаем флаг, что новый кадр с лицом доступен

				imshow("Detecting..", new_frame if new_frame_available else frame)

				if waitKey(1) & 0xFF == ord('q'): break

			cap.release()
			destroyAllWindows()

			person = Counter(person).most_common()[0][0] if person else "Unknown"

			open(r"model\user_name.cfg", "w", encoding='utf-8').write(person)
			return (
				(Counter(average_emotion).most_common()[0][0] if average_emotion else "Unknown"), 
		   		person
				) 

		elif detect_pers == 3: # Просто посмотреть на себя
			while True:
				ret, frame = cap.read()
				putText(frame, text="`Q` for close", org=(
						20, 30), fontFace=FONT_HERSHEY_COMPLEX, fontScale=0.7, color=(0, 255, 0))
				
				imshow("Detecting..", frame)
				if waitKey(1) & 0xFF == ord('q'): 
					break
    
			cap.release()
			destroyAllWindows()

			return "Фсё", "Фсё"


	def face_rec(self, frame, detect_pers: int) -> tuple[list, list]:
		dfs = None
		response = [None]

		if detect_pers in [0, 2]:
			# print(f'detect_pers: {detect_pers}')
			try:
				dfs = find(img_path= frame,
					db_path = 'model\Faces',
					enforce_detection = False,
					silent=True,
					detector_backend='fastmtcnn'
					)
				dfs = dict(pd.concat(dfs).to_dict())
			except ValueError as e:
				print(f'ValueError: {e}')

		if detect_pers in [1, 2]:
			response = analyze(
				frame, actions=("emotion",), enforce_detection=False, detector_backend='fastmtcnn')

		return (response[0] if len(response)>0 else [None]), dfs
