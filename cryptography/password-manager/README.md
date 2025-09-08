# 🛡️ Менеджер паролей с шифрованием

Простой CLI-менеджер паролей с шифрованием данных по мастер-паролю.

## 🔧 Функции
- Генерация надёжных паролей
- Хранение в зашифрованном виде (AES-256-GCM)
- Доступ по мастер-паролю
- Поддержка CLI и базового GUI

## 🚀 Запуск

### Через Docker

```bash
docker-compose build
docker-compose run passman gen gmail user@domain.com --length 12
docker-compose run passman show gmail
```

### Локально
```bash
python -m app.cli gen github mylogin --length 16
python -m app.cli show github
```

### GUI (если установлен tkinter)
```bash
python -m app.gui
```

## 🧪 Тесты
```bash
python -m pytest tests/
```

## 🔐 Безопасность 

    Данные шифруются с помощью PBKDF2 + AES-GCM
    Мастер-пароль не хранится
    Salt и nonce — случайные
     