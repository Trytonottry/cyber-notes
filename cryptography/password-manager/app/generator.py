# app/generator.py
import secrets
import string

def generate_password(length=16, use_upper=True, use_lower=True, use_digits=True, use_symbols=True):
    if length < 1:
        raise ValueError("Длина должна быть >= 1")

    chars = ""
    if use_lower:
        chars += string.ascii_lowercase
    if use_upper:
        chars += string.ascii_uppercase
    if use_digits:
        chars += string.digits
    if use_symbols:
        chars += "!@#$%^&*"

    if not chars:
        raise ValueError("Нужно выбрать хотя бы один набор символов")

    return ''.join(secrets.choice(chars) for _ in range(length))