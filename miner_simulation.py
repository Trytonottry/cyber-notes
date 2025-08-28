# miner_simulation.py
import hashlib
import time

def simulate_mining():
    print("Майнер запущен (симуляция)...")
    counter = 0
    while True:
        # Имитация вычислений
        data = f"block{counter}".encode()
        hashlib.sha256(data).hexdigest()
        counter += 1
        if counter % 10000 == 0:
            print(f"Выполнено итераций: {counter}")

if __name__ == "__main__":
    simulate_mining()