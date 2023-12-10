import threading

def func1():
    print("Функция 1")

def func2():
    print("Функция 2")

def func3():
    print("Функция 3")
    return 42

# Создаем класс-наследник от Thread и добавляем метод для возврата значения
class MyThread(threading.Thread):
    def __init__(self, target, args=()):
        super().__init__(target=target, args=args)
        self._result = None

    def run(self):
        self._result = self._target(*self._args)

    def join(self):
        super().join()
        return self._result

# Создаем потоки для трех функций
thread1 = MyThread(target=func1)
thread2 = MyThread(target=func2)
thread3 = MyThread(target=func3)

# Запускаем потоки
thread1.start()
thread2.start()
thread3.start()

# Ожидаем завершения потоков
thread1.join()
thread2.join()
result = thread3.join()

print(f"Результат функции 3: {result}")  # Вывод: Результат функции 3: 42