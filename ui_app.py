
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow
import sys
from main import AiLogic

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.AiLogic = AiLogic()
        self.AiLogic.start() # Запускаем ИИ

        uic.loadUi('design.ui', self)
        self.btn_handlers()
        self.setFixedSize(400, 600)
        self.inspeechLayout_2.hide()


    def btn_handlers(self): 
        print('Хендлеры запущены')
        self.voiceButton.clicked.connect(self.main_btn_pressed)
        self.Cancel.clicked.connect(self.cancel_btn_pressed)

    def main_btn_pressed(self):
        """
            Вызывается при нажатии на главную кнопку, а затем запускает основной процесс работы ИИ
        """
        print('Кнопка нажата')
        self.inspeechLayout_2.show()
        
    def cancel_btn_pressed(self):
        """
            Нужна для отмены работы ИИ
        """
        self.inspeechLayout_2.hide()

# def application():
#     app = QApplication(sys.argv)
#     window = MainWindow()
#     window.show()

#     sys.exit(app.exec_())


# if __name__ == '__main__':
#     application()