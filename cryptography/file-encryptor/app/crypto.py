# app/crypto.py
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
import os
import struct

# Генерация RSA-ключей
def generate_rsa_keys(key_size=2048, private_path="keys/private_key.pem", public_path="keys/public_key.pem"):
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=key_size)
    public_key = private_key.public_key()

    # Сохраняем приватный ключ
    with open(private_path, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))

    # Сохраняем публичный ключ
    with open(public_path, "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

    print(f"RSA-ключи сохранены: {private_path}, {public_path}")

# Загрузка RSA-ключа
def load_public_key(path="keys/public_key.pem"):
    with open(path, "rb") as f:
        key_data = f.read()
    return serialization.load_pem_public_key(key_data)

def load_private_key(path="keys/private_key.pem"):
    with open(path, "rb") as f:
        key_data = f.read()
    return serialization.load_pem_private_key(key_data, password=None)

# Шифрование файла
def encrypt_file(input_path: str, output_path: str, public_key_path: str = "keys/public_key.pem"):
    # Генерируем случайный AES-ключ и nonce
    aes_key = os.urandom(32)  # 256 бит
    aesgcm = AESGCM(aes_key)
    nonce = os.urandom(12)

    # Читаем файл
    with open(input_path, "rb") as f:
        data = f.read()

    # Шифруем данные
    encrypted_data = aesgcm.encrypt(nonce, data, None)

    # Шифруем AES-ключ с помощью RSA
    public_key = load_public_key(public_key_path)
    encrypted_aes_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Формат файла: [длина ключа][зашифрованный ключ][nonce][данные]
    with open(output_path, "wb") as f:
        f.write(struct.pack("<I", len(encrypted_aes_key)))
        f.write(encrypted_aes_key)
        f.write(nonce)
        f.write(encrypted_data)

    print(f"Файл зашифрован: {output_path}")

# Расшифровка файла
def decrypt_file(input_path: str, output_path: str, private_key_path: str = "keys/private_key.pem"):
    private_key = load_private_key(private_key_path)

    with open(input_path, "rb") as f:
        # Читаем длину зашифрованного ключа
        key_len = struct.unpack("<I", f.read(4))[0]
        encrypted_aes_key = f.read(key_len)
        nonce = f.read(12)
        encrypted_data = f.read()

    # Расшифровываем AES-ключ
    aes_key = private_key.decrypt(
        encrypted_aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Расшифровываем данные
    aesgcm = AESGCM(aes_key)
    data = aesgcm.decrypt(nonce, encrypted_data, None)

    with open(output_path, "wb") as f:
        f.write(data)

    print(f"Файл расшифрован: {output_path}")