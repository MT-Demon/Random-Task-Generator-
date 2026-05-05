import json
import tkinter as tk
from tkinter import ttk, messagebox
import random
from datetime import datetime

# --- Списки по умолчанию ---
DEFAULT_TASKS = [
    {"name": "Прочитать статью", "type": "учёба"},
    {"name": "Сделать зарядку", "type": "спорт"},
    {"name": "Написать отчёт", "type": "работа"},
    {"name": "Выучить 5 новых слов", "type": "учёба"},
    {"name": "Пробежать 2 км", "type": "спорт"},
    {"name": "Позвонить клиенту", "type": "работа"}
]

TASKS_FILE = "tasks_list.json"
HIST_FILE = "tasks_history.json"

# --- Работа с файлами ---
def load_tasks():
    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return DEFAULT_TASKS.copy()
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка загрузки задач: {e}")
        return DEFAULT_TASKS.copy()

def save_tasks(tasks):
    try:
        with open(TASKS_FILE, "w", encoding="utf-8") as f:
            json.dump(tasks, f, ensure_ascii=False, indent=4)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка сохранения задач: {e}")

def load_history():
    try:
        with open(HIST_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка загрузки истории: {e}")
        return []

def save_history(history):
    try:
        with open(HIST_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=4)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка сохранения истории: {e}")

# --- Логика данных ---
def filter_history(history, typ):
    if typ == "Все":
        return history
    return [z for z in history if z["type"] == typ]

# --- GUI ---
class TaskApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор случайных задач")
        self.root.geometry("950x600")
        self.tasks = load_tasks()
        self.history = load_history()

        # --- Левая колонка (список задач) ---
        self.frame_left = tk.LabelFrame(root, text="Список задач", padx=10, pady=10)
        self.frame_left.pack(side="left", fill="y", padx=10, pady=10)
        self.tasks_listbox = tk.Listbox(self.frame_left, width=40, height=20)
        self.tasks_listbox.pack(pady=5)
        self.update_tasks_listbox()

        self.btn_del = tk.Button(self.frame_left, text="Удалить задачу", command=self.delete_task, bg="salmon")
        self.btn_del.pack(pady=4)

        tk.Label(self.frame_left, text="Добавить новую задачу:").pack(pady=(10,2))
        add_frame = tk.Frame(self.frame_left)
        add_frame.pack()
        self.new_task_name = tk.Entry(add_frame, width=22)
        self.new_task_name.pack(side="left")
        self.new_task_type = ttk.Combobox(add_frame, values=["учёба", "спорт", "работа"], state="readonly", width=8)
        self.new_task_type.set("учёба")
        self.new_task_type.pack(side="left", padx=5)
        tk.Button(self.frame_left, text="Добавить", command=self.add_task, bg="lightblue").pack(pady=4)

        # --- Средняя колонка (генератор) ---
        self.frame_generator = tk.LabelFrame(root, text="Генератор задач", padx=10, pady=10)
        self.frame_generator.pack(side="left", fill="y", expand=True, padx=10, pady=10)
        tk.Button(self.frame_generator, text="Сгенерировать задачу", command=self.generate_task, bg="lightgreen", font=("Arial", 13)).pack(pady=10)
        self.result_label = tk.Label(self.frame_generator, text="Нажмите кнопку, чтобы получить задачу", fg="blue", font=("Arial", 12))
        self.result_label.pack(pady=5)

        # --- Правая колонка (история + фильтр) ---
        self.frame_hist = tk.LabelFrame(root, text="История сгенерированных задач", padx=10, pady=10)
        self.frame_hist.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        # Фильтр
        filter_frame = tk.Frame(self.frame_hist)
        filter_frame.pack(fill="x", pady=2)
        tk.Label(filter_frame, text="Фильтр: ").pack(side="left")
        self.filter_var = tk.StringVar()
        self.filter_type = ttk.Combobox(filter_frame, textvariable=self.filter_var,
                                        values=["Все", "учёба", "спорт", "работа"], state="readonly", width=8)
        self.filter_type.set("Все")
        self.filter_type.pack(side="left")
        tk.Button(filter_frame, text="Применить", command=self.apply_filter).pack(side="left", padx=3)
        tk.Button(filter_frame, text="Сброс", command=self.reset_filter).pack(side="left", padx=3)

        # Таблица истории
        columns = ("task", "type", "date")
        self.tree = ttk.Treeview(self.frame_hist, columns=columns, show="headings", height=18)
        self.tree.heading("task", text="Задача")
        self.tree.heading("type", text="Тип")
        self.tree.heading("date", text="Когда")
        self.tree.column("task", width=230)
        self.tree.column("type", width=70)
        self.tree.column("date", width=150)
        self.tree.pack(fill="both", expand=True, pady=4)
        self.update_history_table(self.history)

        tk.Button(self.frame_hist, text="Очистить историю", command=self.clear_history, bg="lightgray").pack(pady=4)

    # --- Функции действий ---
    def update_tasks_listbox(self):
        self.tasks_listbox.delete(0, tk.END)
        for z in self.tasks:
            self.tasks_listbox.insert(tk.END, f"{z['name']} ({z['type']})")

    def add_task(self):
        name = self.new_task_name.get().strip()
        typ = self.new_task_type.get()
        if not name:
            messagebox.showerror("Ошибка", "Название задачи не может быть пустым!")
            return
        self.tasks.append({"name": name, "type": typ})
        save_tasks(self.tasks)
        self.update_tasks_listbox()
        self.new_task_name.delete(0, tk.END)
        messagebox.showinfo("Добавлено", f"Задача '{name}' добавлена!")

    def delete_task(self):
        idx = self.tasks_listbox.curselection()
        if not idx:
            messagebox.showerror("Ошибка", "Выберите задачу для удаления")
            return
        if messagebox.askyesno("Подтвердите", "Удалить выбранную задачу?"):
            removed = self.tasks.pop(idx[0])
            save_tasks(self.tasks)
            self.update_tasks_listbox()
            messagebox.showinfo("Удалено", f"Задача '{removed['name']}' удалена")

    def generate_task(self):
        if not self.tasks:
            messagebox.showerror("Ошибка", "Нет доступных задач для генерации!")
            return
        task = random.choice(self.tasks)
        rec = {
            "task": task["name"],
            "type": task["type"],
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.history.append(rec)
        save_history(self.history)
        self.update_history_table(self.history)
        self.result_label.config(text=f"Текущая задача: {task['name']}")
        messagebox.showinfo("Задача!", f"Ваша задача:\n\n{task['name']}")

    def update_history_table(self, data):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for z in data:
            self.tree.insert("", "end", values=(z["task"], z["type"], z["date"]))

    def apply_filter(self):
        typ = self.filter_type.get()
        filtered = filter_history(self.history, typ)
        self.update_history_table(filtered)
        if not filtered:
            messagebox.showinfo("Результат", "По фильтру ничего не найдено.")

    def reset_filter(self):
        self.filter_type.set("Все")
        self.update_history_table(self.history)

    def clear_history(self):
        if not self.history:
            messagebox.showinfo("Инфо", "История уже пуста.")
            return
        if messagebox.askyesno("Подтвердите", "Очистить всю историю?"):
            self.history = []
            save_history(self.history)
            self.update_history_table(self.history)
            messagebox.showinfo("Готово", "История очищена.")

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskApp(root)
    root.mainloop()
