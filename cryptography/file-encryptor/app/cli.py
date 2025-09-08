# app/cli.py
import argparse
import os
from app.crypto import generate_rsa_keys, encrypt_file, decrypt_file

def main():
    parser = argparse.ArgumentParser(description="AES+RSA File Encryptor")
    subparsers = parser.add_subparsers(dest="command", help="Доступные команды")

    # Генерация ключей
    parser_gen = subparsers.add_parser("genkeys", help="Сгенерировать RSA-ключи")
    parser_gen.add_argument("--private", default="keys/private_key.pem")
    parser_gen.add_argument("--public", default="keys/public_key.pem")

    # Шифрование
    parser_enc = subparsers.add_parser("encrypt", help="Зашифровать файл")
    parser_enc.add_argument("input", help="Входной файл")
    parser_enc.add_argument("output", help="Выходной файл")
    parser_enc.add_argument("--public", default="keys/public_key.pem")

    # Расшифровка
    parser_dec = subparsers.add_parser("decrypt", help="Расшифровать файл")
    parser_dec.add_argument("input", help="Входной файл")
    parser_dec.add_argument("output", help="Выходной файл")
    parser_dec.add_argument("--private", default="keys/private_key.pem")

    args = parser.parse_args()

    if args.command == "genkeys":
        os.makedirs("keys", exist_ok=True)
        generate_rsa_keys(private_path=args.private, public_path=args.public)

    elif args.command == "encrypt":
        if not os.path.exists(args.input):
            print(f"Ошибка: файл {args.input} не найден.")
            exit(1)
        encrypt_file(args.input, args.output, args.public)

    elif args.command == "decrypt":
        if not os.path.exists(args.input):
            print(f"Ошибка: файл {args.input} не найден.")
            exit(1)
        decrypt_file(args.input, args.output, args.private)

    else:
        parser.print_help()

if __name__ == "__main__":
    main()