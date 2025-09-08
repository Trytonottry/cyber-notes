# app/storage.py
import json
import os
from app.crypto import encrypt_data, decrypt_data

STORAGE_PATH = "data/passwords.enc"

def save_passwords(passwords: dict, master_password: str):
    plaintext = json.dumps(passwords, ensure_ascii=False, indent=2)
    encrypted = encrypt_data(plaintext, master_password)

    os.makedirs(os.path.dirname(STORAGE_PATH), exist_ok=True)
    with open(STORAGE_PATH, "wb") as f:
        f.write(encrypted)

def load_passwords(master_password: str) -> dict:
    if not os.path.exists(STORAGE_PATH):
        return {}

    with open(STORAGE_PATH, "rb") as f:
        encrypted = f.read()

    try:
        plaintext = decrypt_data(encrypted, master_password)
        return json.loads(plaintext)
    except Exception as e:
        raise ValueError("Неверный мастер-пароль или повреждённые данные") from e