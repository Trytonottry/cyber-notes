# ransomware_simulation.py
import os

# ⚠️ НИКОГДА НЕ ЗАПУСКАЙТЕ НА ВАЖНЫХ ДАННЫХ

files_to_encrypt = []
for file in os.listdir('.'):
    if file.endswith('.txt') or file.endswith('.doc'):
        files_to_encrypt.append(file)

if not files_to_encrypt:
    print("Нет файлов для шифрования.")
else:
    key = "SIMULATED_KEY_123"  # Условный "ключ"
    for file in files_to_encrypt:
        # Переименовываем файл, как будто зашифровали
        os.rename(file, file + ".encrypted")
        print(f"Файл зашифрован: {file} → {file}.encrypted")

    print(f"""
    Ваши файлы зашифрованы!
    Для расшифровки отправьте 1 BTC на кошелёк...
    (Это симуляция. Восстановите файлы, переименовав обратно.)
    """)