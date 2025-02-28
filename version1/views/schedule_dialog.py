import tkinter as tk
from tkinter import ttk, messagebox

class AddScheduleDialog:
    def __init__(self, parent, db, grade, class_name, day_of_week, lesson_number):
        self.top = tk.Toplevel(parent)
        self.db = db
        self.grade = grade
        self.class_name = class_name
        self.day_of_week = day_of_week
        self.lesson_number = lesson_number
        
        self.top.title("Добавить урок")
        self.top.geometry("300x250")
        
        self.subjects = self.db.get_all_subjects()
        
        #Создание и размещение элементов
        ttk.Label(self.top, text="Предмет:").pack(pady=5)
        self.subject_cb = ttk.Combobox(self.top, values=[s[1] for s in self.subjects])
        self.subject_cb.pack(pady=5)
        
        ttk.Label(self.top, text="Кабинет:").pack(pady=5)
        self.room_entry = ttk.Entry(self.top)
        self.room_entry.pack(pady=5)
        
        time_frame = ttk.Frame(self.top)
        time_frame.pack(pady=5, fill='x')
        
        ttk.Label(time_frame, text="Время:").pack(side='left', padx=5)
        self.start_time = ttk.Entry(time_frame, width=8)
        self.start_time.pack(side='left', padx=5)
        ttk.Label(time_frame, text="-").pack(side='left')
        self.end_time = ttk.Entry(time_frame, width=8)
        self.end_time.pack(side='left', padx=5)
        
        time_slots = {
            1: ('09:00', '09:45'),
            2: ('09:55', '10:40'),
            3: ('10:50', '11:35'),
            4: ('11:55', '12:40'),
            5: ('12:50', '13:35'),
            6: ('13:45', '14:30'),
            7: ('14:40', '15:25'),
            8: ('15:35', '16:20')
        }
        if lesson_number in time_slots:
            self.start_time.insert(0, time_slots[lesson_number][0])
            self.end_time.insert(0, time_slots[lesson_number][1])
        
        ttk.Button(self.top, text="Добавить",
                  command=self.add_lesson).pack(pady=20)

    def add_lesson(self):
        subject_idx = self.subject_cb.current()
        room = self.room_entry.get()
        start = self.start_time.get()
        end = self.end_time.get()
        
        if subject_idx >= 0:
            try:
                subject_id = self.subjects[subject_idx][0]
                self.db.add_schedule_entry(
                    self.grade,
                    self.class_name,
                    self.day_of_week,
                    self.lesson_number,
                    subject_id,
                    room
                )
                self.top.destroy()
                messagebox.showinfo("Успех", "Урок добавлен в расписание")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось добавить урок: {str(e)}")
        else:
            messagebox.showerror("Ошибка", "Выберите предмет") 
