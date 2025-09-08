# 🔐 File Encryptor (AES + RSA)

Простой инструмент для шифрования файлов с использованием комбинации AES и RSA.

## 🔧 Функции
- Генерация RSA-ключей (2048 бит)
- Шифрование файлов с AES-256-GCM
- Защита AES-ключа с помощью RSA
- CLI и HTTP API

## 🚀 Запуск

### Через Docker (рекомендуется)

```bash
docker-compose build
docker-compose run encryptor genkeys
echo "Hello" > data/test.txt
docker-compose run encryptor encrypt data/test.txt data/test.enc
docker-compose run encryptor decrypt data/test.enc data/test_dec.txt
cat data/test_dec.txt
```

### Локально
```bash
python -m app.cli genkeys
python -m app.cli encrypt input.txt output.enc
python -m app.cli decrypt output.enc decrypted.txt
```

### 🌐 Запуск API
```bash
python -m app.api
```

### 🧪 Тесты
```bash
python -m pytest tests/
```

