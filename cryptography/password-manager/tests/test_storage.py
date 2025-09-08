# tests/test_storage.py
import os
import json
from app.storage import save_passwords, load_passwords

TEST_PASSWORDS = {"test.com": {"login": "user", "password": "secret123"}}
MASTER_PASS = "mypass123"
STORAGE = "test_data/test.enc"

def setup_module():
    os.makedirs("test_data", exist_ok=True)

def teardown_module():
    if os.path.exists(STORAGE):
        os.remove(STORAGE)

def test_encrypt_decrypt():
    save_passwords(TEST_PASSWORDS, MASTER_PASS)

    assert os.path.exists(STORAGE)

    loaded = load_passwords(MASTER_PASS)
    assert loaded == TEST_PASSWORDS

    # Проверка на неверный пароль
    try:
        load_passwords("wrongpass")
        assert False, "Должна быть ошибка"
    except ValueError:
        pass