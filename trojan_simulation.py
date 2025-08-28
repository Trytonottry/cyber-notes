# trojan_simulation.py
# Выглядит как калькулятор, но делает что-то ещё

def calculator():
    a = float(input("Введите первое число: "))
    b = float(input("Введите второе число: "))
    print(f"Сумма: {a + b}")

# "Троянская" часть — запись в лог
def log_input():
    with open("trojan_log.txt", "a") as f:
        f.write("Пользователь запустил калькулятор\n")

if __name__ == "__main__":
    log_input()  # Скрытая активность
    calculator()