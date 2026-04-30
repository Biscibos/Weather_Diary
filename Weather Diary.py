import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

# --- Настройки ---
DATA_FILE = "data/weather_data.json"

# --- Функции работы с данными ---
def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- Функции GUI ---
def add_record():
    # Получаем значения из полей
    day = spinbox_day.get()
    month = spinbox_month.get()
    year = spinbox_year.get()
    temp = entry_temp.get()
    desc = entry_desc.get()
    precip = var_precip.get()

    # Проверка обязательных полей
    if not temp or not desc:
        messagebox.showerror("Ошибка", "Температура и Описание должны быть заполнены!")
        return

    # Проверка температуры
    try:
        temp = float(temp)
    except ValueError:
        messagebox.showerror("Ошибка", "Температура должна быть числом!")
        return

    # Формирование даты в нужном формате для хранения (ГГГГ.ММ.ДД)
    date_str = f"{year}.{month}.{day}"

    record = {
        "date": date_str,
        "temperature": temp,
        "description": desc,
        "precipitation": precip == 1
    }

    data.append(record)
    save_data(data)
    update_listbox()
    clear_entries()

def clear_entries():
    entry_temp.delete(0, tk.END)
    entry_desc.delete(0, tk.END)
    var_precip.set(0)

def update_listbox(filter_func=None):
    """Обновляет список записей в Listbox"""
    listbox.delete(0, tk.END)
    
    # Сортируем данные по дате (сначала год, потом месяц, потом день)
    sorted_data = sorted(data, key=lambda x: x['date'])
    
    records = sorted_data if filter_func is None else list(filter(filter_func, sorted_data))
    
    for i, rec in enumerate(records):
        precip_str = "Да" if rec["precipitation"] else "Нет"
        listbox.insert(tk.END, f"{i+1}. {rec['date']} | {rec['temperature']}°C | {rec['description']} | Осадки: {precip_str}")

def filter_by_date():
    target_date = entry_filter_date.get()
    
    # Проверка формата даты для фильтра (ГГГГ.ММ.ДД)
    if not target_date:
        update_listbox()
        return

    parts = target_date.split('.')
    if len(parts) != 3:
        messagebox.showerror("Ошибка", "Дата должна быть в формате ГГГГ.ММ.ДД!")
        return

    try:
        year, month, day = map(int, parts)
        # Проверка диапазонов (базовая валидация)
        if not (1 <= month <= 12) or not (1 <= day <= 31):
            raise ValueError
    except ValueError:
        messagebox.showerror("Ошибка", "Неверный формат даты или значения!")
        return

    update_listbox(lambda x: x["date"] == target_date)

def filter_by_temp():
    try:
        threshold = float(entry_filter_temp.get())
    except ValueError:
        messagebox.showerror("Ошибка", "Порог температуры должен быть числом!")
        return
    
    # Фильтруем записи с температурой выше порога
    update_listbox(lambda x: x["temperature"] > threshold)

# --- Инициализация данных и окна ---
data = load_data()
root = tk.Tk()
root.title("Дневник погоды")
root.geometry("850x650")

# --- Вкладки (Notebook) ---
notebook = ttk.Notebook(root)
frame_main = ttk.Frame(notebook)
frame_filter = ttk.Frame(notebook)
notebook.add(frame_main, text="Добавить запись")
notebook.add(frame_filter, text="Фильтр")
notebook.pack(expand=1, fill="both")

# --- Вкладка "Добавить запись" ---
# Блок для даты (День. Месяц. Год)
frame_date = tk.LabelFrame(frame_main, text="Дата (ДД.ММ.ГГГГ)", padx=10, pady=10)
frame_date.grid(row=0, column=0, columnspan=2, pady=10, padx=10, sticky="we")

spinbox_day = tk.Spinbox(frame_date, from_=1, to=31, width=5)
spinbox_day.grid(row=0, column=0, padx=5)
tk.Label(frame_date, text=".").grid(row=0, column=1)
spinbox_month = tk.Spinbox(frame_date, from_=1, to=12, width=5)
spinbox_month.grid(row=0, column=2, padx=5)
tk.Label(frame_date, text=".").grid(row=0, column=3)
spinbox_year = tk.Spinbox(frame_date, from_=2020, to=2035, width=8)
spinbox_year.grid(row=0, column=4)

# Остальные поля ввода
tk.Label(frame_main, text="Температура (°C):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
entry_temp = tk.Entry(frame_main)
entry_temp.grid(row=1, column=1, padx=10, pady=5)

tk.Label(frame_main, text="Описание:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
entry_desc = tk.Entry(frame_main)
entry_desc.grid(row=2, column=1, padx=10, pady=5)

tk.Label(frame_main, text="Осадки:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
var_precip = tk.IntVar()
tk.Radiobutton(frame_main, text="Да", variable=var_precip, value=1).grid(row=3, column=1, sticky="w")
tk.Radiobutton(frame_main, text="Нет", variable=var_precip, value=0).grid(row=3, column=1)

btn_add = tk.Button(frame_main, text="Добавить запись", command=add_record)
btn_add.grid(row=4, column=0, columnspan=2, pady=20)

# --- Вкладка "Фильтр" ---
tk.Label(frame_filter, text="Фильтр по дате (ГГГГ.ММ.ДД):").grid(row=0, column=0, padx=10, pady=5)
entry_filter_date = tk.Entry(frame_filter)
entry_filter_date.grid(row=0, column=1, padx=10)
btn_filter_date = tk.Button(frame_filter, text="Найти", command=filter_by_date)
btn_filter_date.grid(row=0, column=2)

tk.Label(frame_filter, text="Фильтр по температуре (>):").grid(row=1, column=0)
entry_filter_temp = tk.Entry(frame_filter)
entry_filter_temp.grid(row=1, column=1)
btn_filter_temp = tk.Button(frame_filter, text="Найти", command=filter_by_temp)
btn_filter_temp.grid(row=1, column=2)

# Список записей (общий для обеих вкладок)
listbox = tk.Listbox(root)
listbox.pack(expand=True, fill="both", padx=20, pady=(0, 20))
update_listbox() # Загружаем данные при старте

root.mainloop()
