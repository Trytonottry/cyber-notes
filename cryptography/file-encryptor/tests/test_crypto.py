# tests/test_crypto.py
import os
import pytest
from app.crypto import encrypt_file, decrypt_file, generate_rsa_keys

TEST_FILE = "test_input.txt"
ENCRYPTED_FILE = "test_encrypted.enc"
DECRYPTED_FILE = "test_decrypted.txt"

def setup_module():
    with open(TEST_FILE, "w") as f:
        f.write("Секретные данные для теста!")

    if not os.path.exists("keys/private_key.pem"):
        generate_rsa_keys()

def teardown_module():
    for f in [TEST_FILE, ENCRYPTED_FILE, DECRYPTED_FILE]:
        if os.path.exists(f):
            os.remove(f)

def test_encrypt_decrypt():
    encrypt_file(TEST_FILE, ENCRYPTED_FILE)
    assert os.path.exists(ENCRYPTED_FILE)

    decrypt_file(ENCRYPTED_FILE, DECRYPTED_FILE)
    assert os.path.exists(DECRYPTED_FILE)

    with open(TEST_FILE, "r") as f1, open(DECRYPTED_FILE, "r") as f2:
        assert f1.read() == f2.read()