# app/gui.py
import tkinter as tk
from tkinter import messagebox, simpledialog
from app.cli import main as run_cli

def run_gui():
    root = tk.Tk()
    root.title("🔐 Менеджер паролей")
    root.geometry("400x300")

    tk.Label(root, text="Менеджер паролей", font=("Arial", 16)).pack(pady=20)

    def add_password():
        service = simpledialog.askstring("Добавить", "Сервис:")
        if not service: return
        login = simpledialog.askstring("Добавить", "Логин:")
        password = simpledialog.askstring("Добавить", "Пароль:", show="*")
        if service and login and password:
            # Эмуляция CLI
            import sys
            from io import StringIO
            old_input = input
            old_getpass = __import__('getpass').getpass

            def mock_input(prompt):
                if "Мастер-пароль" in prompt:
                    return simpledialog.askstring("Мастер", "Мастер-пароль:", show="*")
                return old_input(prompt)

            def mock_getpass(prompt):
                return mock_input(prompt)

            __import__('builtins').input = mock_input
            __import__('getpass').getpass = mock_getpass

            sys.argv = ['cli.py', 'add', service, login]
            try:
                main()
                messagebox.showinfo("Успех", f"Пароль для {service} добавлен!")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
            finally:
                __import__('builtins').input = old_input
                __import__('getpass').getpass = old_getpass

    tk.Button(root, text="Добавить пароль", command=add_password).pack(pady=10)
    tk.Button(root, text="Сгенерировать", command=lambda: messagebox.showinfo("Info", "Используй CLI: gen")).pack(pady=10)
    tk.Button(root, text="Показать пароль", command=lambda: messagebox.showinfo("Info", "Используй CLI: show")).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    run_gui()