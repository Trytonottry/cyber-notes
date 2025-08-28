# worm_simulation.py
import os
import shutil

# Упрощённый червь, копирующий себя в другие папки
import sys

def worm_action():
    current_file = sys.argv[0]
    for i in range(3):  # Создаём 3 копии
        copy_name = f"fake_update_{i}.py"
        if not os.path.exists(copy_name):
            shutil.copy(current_file, copy_name)
            print(f"Создана копия: {copy_name}")

if __name__ == "__main__":
    worm_action()