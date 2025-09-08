# app/cli.py
import argparse
import getpass
from app.storage import load_passwords, save_passwords
from app.generator import generate_password

def main():
    parser = argparse.ArgumentParser(description="Менеджер паролей с шифрованием")
    subparsers = parser.add_subparsers(dest="command", help="Команды")

    # Добавить пароль
    p_add = subparsers.add_parser("add", help="Добавить пароль")
    p_add.add_argument("service", help="Название сервиса (например, gmail)")
    p_add.add_argument("login", help="Логин")

    # Сгенерировать пароль
    p_gen = subparsers.add_parser("gen", help="Сгенерировать пароль")
    p_gen.add_argument("service", help="Название сервиса")
    p_gen.add_argument("login", help="Логин")
    p_gen.add_argument("--length", type=int, default=16, help="Длина пароля")
    p_gen.add_argument("--no-symbols", action="store_true", help="Без символов")

    # Показать пароль
    p_show = subparsers.add_parser("show", help="Показать пароль")
    p_show.add_argument("service", help="Название сервиса")

    # Список всех сервисов
    p_list = subparsers.add_parser("list", help="Показать все сервисы")

    args = parser.parse_args()

    # Запрашиваем мастер-пароль
    master_password = getpass.getpass("Мастер-пароль: ")

    passwords = {}
    try:
        passwords = load_passwords(master_password)
    except ValueError as e:
        if "Неверный мастер-пароль" in str(e) and args.command != "add":
            print("Ошибка: неверный мастер-пароль.")
            exit(1)
        # Если файла нет — создаём пустой
        elif "повреждённые данные" not in str(e):
            passwords = {}

    if args.command == "add":
        password = getpass.getpass("Пароль: ")
        passwords[args.service] = {"login": args.login, "password": password}
        save_passwords(passwords, master_password)
        print(f"✅ Пароль для {args.service} добавлен.")

    elif args.command == "gen":
        password = generate_password(
            length=args.length,
            use_symbols=not args.no_symbols
        )
        passwords[args.service] = {"login": args.login, "password": password}
        save_passwords(passwords, master_password)
        print(f"✅ Сгенерирован пароль для {args.service}: {password}")

    elif args.command == "show":
        if args.service in passwords:
            entry = passwords[args.service]
            print(f"Логин: {entry['login']}")
            print(f"Пароль: {entry['password']}")
        else:
            print(f"❌ Сервис '{args.service}' не найден.")

    elif args.command == "list":
        if passwords:
            print("Сохранённые сервисы:")
            for svc in passwords:
                print(f"  - {svc}")
        else:
            print("Хранилище пусто.")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()