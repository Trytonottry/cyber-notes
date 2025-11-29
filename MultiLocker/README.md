# MultiLocker — учебный WinLocker (демо)

**Внимание:** это образовательный проект. Не используйте в продакшн, не разворачивайте в рабочей сети без разрешения. Тестировать только в виртуальной машине (snapshot).

## Компоненты
- `MultiLocker.Gui` — WinForms киоск-локер (мульти-монитор, ClipCursor, low-level hook, JSON-лог, named pipe).
- `MultiLocker.Client` — простой named-pipe клиент (UNLOCK <password>).
- `MultiLocker.Watchdog` — опциональный watchdog (перезапускает GUI при падении) — использовать только в тестовых VM.

## Сборка
Требуется .NET 7/8 SDK и Visual Studio (рекомендуется для WinForms).
Пример (CLI):
```bash
dotnet build ./MultiLocker.sln
```

Запуск
Сделайте snapshot VM.
Запустите:
```bash
MultiLocker.Gui.exe --pwd=demo123 --maxAttempts=5 --lockoutSeconds=60 --autoLockSeconds=5 --lang=ru --log=%TEMP%/winlocker_log.json
```

Чтобы разблокировать из другой сессии/терминала:
```
MultiLocker.Client.exe "UNLOCK demo123"
```

Логи

JSON-строки в файле --log (по-умолчанию %TEMP%/winlocker_log.json).

Безопасность

Не использует persistence, реестр, автозапуск, драйверы, модификации Winlogon.
Не пытается перехватить Ctrl+Alt+Del.
Тестировать в VM.