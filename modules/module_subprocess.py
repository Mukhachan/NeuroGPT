import subprocess
import json
import difflib
from PyQt5.QtCore import QThread, pyqtSignal 
from time import sleep
from modules.config import cutoff

class ProgramStart(QThread):
    started = pyqtSignal(str)
    def __init__(self) -> None:
        super().__init__()
        self.json_raw = json.load(open("model/programs.json", encoding="utf-8"))
        if not self.json_raw: return
        self.programms = [x["Program"] for x in self.json_raw]
        self.paths = [x["Path"] for x in self.json_raw]

    def start_programm(self, text: str) -> tuple[bool, str]:
        """
            Передаём текст. Запускается программа
        """
        self.json_raw = json.load(open("model/programs.json", encoding="utf-8"))
        if not self.json_raw: return
        self.programms = [x["Program"] for x in self.json_raw]
        self.paths = [x["Path"] for x in self.json_raw]

        text = text.lower().strip()
        programm = "".join(difflib.get_close_matches(text, self.programms, cutoff=cutoff))
        if programm:
            # Нашлась программа, запускаем
            self.started.emit('Программа найдена')
            prog_path = self.paths[self.programms.index(programm)]
            print(prog_path)
            subprocess.Popen(prog_path)
            return (True, f"Программа {programm} найдена, запускаю")
        
        else:
            # Не нашла программа, не запускаем
            self.started.emit('Программа не найдена')
            return (False, f"Программа {text} не найден")
