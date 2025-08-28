# adware_simulation.py
import webbrowser
import time
import random

ads = [
    "https://example.com/sale",
    "https://example.com/cheap-viagra",
    "https://example.com/win-prize"
]

print("Запуск полезной программы...")

for _ in range(3):
    time.sleep(5)
    url = random.choice(ads)
    print(f"Открываю рекламу: {url}")
    webbrowser.open(url)