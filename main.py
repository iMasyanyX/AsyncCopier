import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import os
import shutil
import datetime
import asyncio


class CopyDirectoryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AsyncCopier")

        # Исходная папка
        self.source_frame = tk.Frame(self)
        self.source_frame.pack()
        self.source_label = tk.Label(self.source_frame, text="Исходная папка:")
        self.source_label.pack(side="left")
        self.source_entry = tk.Entry(self.source_frame, width=40)
        self.source_entry.pack(side="left")
        self.source_browse_button = tk.Button(self.source_frame, text="Обзор", command=self.browse_source_folder)
        self.source_browse_button.pack(side="left")

        # Папка назначения
        self.destination_frame = tk.Frame(self)
        self.destination_frame.pack()
        self.destination_label = tk.Label(self.destination_frame, text="Папка назначения:")
        self.destination_label.pack(side="left")
        self.destination_entry = tk.Entry(self.destination_frame, width=40)
        self.destination_entry.pack(side="left")
        self.destination_browse_button = tk.Button(self.destination_frame, text="Обзор", command=self.browse_destination_folder)
        self.destination_browse_button.pack(side="left")

        # Время начала копирования
        self.start_time_frame = tk.Frame(self)
        self.start_time_frame.pack()
        self.start_time_label = tk.Label(self.start_time_frame, text="Время начала копирования:")
        self.start_time_label.pack(side="left")
        self.start_time_entry = tk.Entry(self.start_time_frame, width=10)
        self.start_time_entry.pack(side="left")
        self.start_time_up_button = tk.Button(self.start_time_frame, text="▲", command=self.increment_start_time)
        self.start_time_up_button.pack(side="left")
        self.start_time_down_button = tk.Button(self.start_time_frame, text="▼", command=self.decrement_start_time)
        self.start_time_down_button.pack(side="left")

        # Время окончания копирования
        self.end_time_frame = tk.Frame(self)
        self.end_time_frame.pack()
        self.end_time_label = tk.Label(self.end_time_frame, text="Время окончания копирования:")
        self.end_time_label.pack(side="left")
        self.end_time_entry = tk.Entry(self.end_time_frame, width=10)
        self.end_time_entry.pack(side="left")
        self.end_time_up_button = tk.Button(self.end_time_frame, text="▲", command=self.increment_end_time)
        self.end_time_up_button.pack(side="left")
        self.end_time_down_button = tk.Button(self.end_time_frame, text="▼", command=self.decrement_end_time)
        self.end_time_down_button.pack(side="left")

        # Кнопки старт и стоп
        self.progress_frame = tk.Frame(self)
        self.progress_frame.pack(pady=10)
        self.button_frame = tk.Frame(self)
        self.button_frame.pack()
        self.start_button = tk.Button(self.button_frame, text="Старт", command=self.start_copying)
        self.start_button.pack(side="left")
        self.stop_button = tk.Button(self.button_frame, text="Стоп", command=self.stop_copying, state=tk.DISABLED)
        self.stop_button.pack(side="left")

        # Прогрессбар
        self.progress_frame = tk.Frame(self)
        self.progress_frame.pack(pady=10)
        self.progress_frame = tk.Frame(self)
        self.progress_frame.pack()
        self.progress_label = tk.Label(self.progress_frame, text="Текущий статус выполнения:")
        self.progress_label.pack(side="left")
        self.status_progressbar = ttk.Progressbar(self.progress_frame, length=200, mode="determinate")
        self.status_progressbar.pack(side="left")

        # Информация о задаче
        self.info_text = tk.Text(self, height=10, width=50)
        self.info_text.pack()

        self.copying_active = False
        self.total_files = 0
        self.copied_files = 0
        self.status = 0

    def browse_source_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.source_entry.delete(0, tk.END)
            self.source_entry.insert(tk.END, folder)

    def browse_destination_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.destination_entry.delete(0, tk.END)
            self.destination_entry.insert(tk.END, folder)

    def increment_start_time(self):
        current_time = self.start_time_entry.get()
        try:
            time_obj = datetime.datetime.strptime(current_time, "%H:%M")
            new_time = (time_obj + datetime.timedelta(minutes=1)).strftime("%H:%M")
            self.start_time_entry.delete(0, tk.END)
            self.start_time_entry.insert(tk.END, new_time)
        except ValueError:
            pass

    def decrement_start_time(self):
        current_time = self.start_time_entry.get()
        try:
            time_obj = datetime.datetime.strptime(current_time, "%H:%M")
            new_time = (time_obj - datetime.timedelta(minutes=1)).strftime("%H:%M")
            self.start_time_entry.delete(0, tk.END)
            self.start_time_entry.insert(tk.END, new_time)
        except ValueError:
            pass

    def increment_end_time(self):
        current_time = self.end_time_entry.get()
        try:
            time_obj = datetime.datetime.strptime(current_time, "%H:%M")
            new_time = (time_obj + datetime.timedelta(minutes=1)).strftime("%H:%M")
            self.end_time_entry.delete(0, tk.END)
            self.end_time_entry.insert(tk.END, new_time)
        except ValueError:
            pass

    def decrement_end_time(self):
        current_time = self.end_time_entry.get()
        try:
            time_obj = datetime.datetime.strptime(current_time, "%H:%M")
            new_time = (time_obj - datetime.timedelta(minutes=1)).strftime("%H:%M")
            self.end_time_entry.delete(0, tk.END)
            self.end_time_entry.insert(tk.END, new_time)
        except ValueError:
            pass

    async def start_copying(self):
        self.source_folder = self.source_entry.get()
        self.destination_folder = self.destination_entry.get()

        if not os.path.isdir(self.source_folder) or not os.path.isdir(self.destination_folder):
            messagebox.showerror("Ошибка", "Некорректные пути папок")
            return

        try:
            self.start_time = datetime.datetime.strptime(self.start_time_entry.get(), "%H:%M").time()
            self.end_time = datetime.datetime.strptime(self.end_time_entry.get(), "%H:%M").time()
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректный формат времени")
            return

        if self.start_time >= self.end_time:
            messagebox.showerror("Ошибка", "Некорректный период времени")
            return

        self.total_files = sum(len(files) for _, _, files in os.walk(self.source_folder))
        self.copied_files = 0
        self.status = 0

        self.start_button.configure(state=tk.DISABLED)
        self.stop_button.configure(state=tk.NORMAL)
        self.start_time_entry.configure(state=tk.DISABLED)
        self.start_time_up_button.configure(state=tk.DISABLED)
        self.start_time_down_button.configure(state=tk.DISABLED)
        self.end_time_entry.configure(state=tk.DISABLED)
        self.end_time_up_button.configure(state=tk.DISABLED)
        self.end_time_down_button.configure(state=tk.DISABLED)
        self.copying_active = True

        await self.copy_directory()

    def stop_copying(self):
        self.start_button.configure(state=tk.NORMAL)
        self.stop_button.configure(state=tk.DISABLED)
        self.start_time_entry.configure(state=tk.NORMAL)
        self.start_time_up_button.configure(state=tk.NORMAL)
        self.start_time_down_button.configure(state=tk.NORMAL)
        self.end_time_entry.configure(state=tk.NORMAL)
        self.end_time_up_button.configure(state=tk.NORMAL)
        self.end_time_down_button.configure(state=tk.NORMAL)
        self.copying_active = False

    async def copy_directory(self):
        while self.copying_active:
            current_time = datetime.datetime.now().time()

            if self.start_time <= current_time < self.end_time:
                source_files = []
                for root, _, files in os.walk(self.source_folder):
                    for file in files:
                        source_files.append(os.path.join(root, file))

                for file in source_files:
                    destination_file = file.replace(self.source_folder, self.destination_folder)
                    destination_directory = os.path.dirname(destination_file)
                    os.makedirs(destination_directory, exist_ok=True)
                    shutil.copy2(file, destination_file)
                    self.copied_files += 1
                    self.status = int((self.copied_files / self.total_files) * 100)

                    self.status_progressbar['value'] = self.status
                    self.info_text.delete(1.0, tk.END)
                    self.info_text.insert(tk.END, "Исходная папка: {}\n".format(self.source_folder))
                    self.info_text.insert(tk.END, "Папка назначения: {}\n".format(self.destination_folder))
                    self.info_text.insert(tk.END, "Дата создания задачи: {}\n".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    self.info_text.insert(tk.END, "Указанный период копирования: {} - {}\n".format(self.start_time, self.end_time))
                    self.info_text.insert(tk.END, "Текущий статус выполнения: {}%\n".format(self.status))

                    if self.copied_files == self.total_files:
                        self.info_text.insert(tk.END, "Копирование завершено!\n")
                        self.start_button.configure(state=tk.NORMAL)
                        self.stop_button.configure(state=tk.DISABLED)
                        self.start_time_entry.configure(state=tk.NORMAL)
                        self.start_time_up_button.configure(state=tk.NORMAL)
                        self.start_time_down_button.configure(state=tk.NORMAL)
                        self.end_time_entry.configure(state=tk.NORMAL)
                        self.end_time_up_button.configure(state=tk.NORMAL)
                        self.end_time_down_button.configure(state=tk.NORMAL)
                        self.copying_active = False
                        return

            else:
                self.info_text.delete(1.0, tk.END)
                self.info_text.insert(tk.END, "Исходная папка: {}\n".format(self.source_folder))
                self.info_text.insert(tk.END, "Папка назначения: {}\n".format(self.destination_folder))
                self.info_text.insert(tk.END, "Дата создания задачи: {}\n".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                self.info_text.insert(tk.END, "Указанный период копирования: {} - {}\n".format(self.start_time, self.end_time))
                self.info_text.insert(tk.END, "Текущий статус выполнения: Задача на паузе...\n")

            await asyncio.sleep(1)  # Пауза в 1 секунду

if __name__ == "__main__":
    app = CopyDirectoryApp()
    app.mainloop()