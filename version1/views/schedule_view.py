import tkinter as tk
from tkinter import ttk, messagebox
from database.db_manager import DatabaseManager
from datetime import datetime, timedelta

class ScheduleView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.db = DatabaseManager()
        self.current_week_start = self.get_current_week_start()
        self.setup_ui()
        
    def get_current_week_start(self):
        today = datetime.now()
        return today - timedelta(days=today.weekday())
    
    #Панель
    def setup_ui(self):
        control_frame = ttk.Frame(self)
        control_frame.pack(fill='x', padx=5, pady=5)
        
        class_frame = ttk.Frame(control_frame)
        class_frame.pack(side='left', fill='x', padx=5)
        
        ttk.Label(class_frame, text="Класс:").pack(side='left', padx=5)
        
        classes = self.get_unique_classes()
        self.class_var = tk.StringVar()
        self.class_cb = ttk.Combobox(class_frame, textvariable=self.class_var, values=classes)
        self.class_cb.pack(side='left', padx=5)
        self.class_cb.bind('<<ComboboxSelected>>', self.on_class_selected)
        
        ttk.Button(class_frame, text="Добавить урок",
                  command=self.show_add_dialog).pack(side='left', padx=5)
        
        refresh_btn = ttk.Button(class_frame, text="Обновить",
                               command=self.on_class_selected)
        refresh_btn.pack(side='left', padx=5)
        
        week_frame = ttk.Frame(control_frame)
        week_frame.pack(side='right', fill='x', padx=5)
        
        self.prev_week_btn = ttk.Button(week_frame, text="◀",
                                      command=self.prev_week)
        self.prev_week_btn.pack(side='left', padx=5)
        
        self.week_label = ttk.Label(week_frame, text="")
        self.week_label.pack(side='left', padx=5)
        
        self.next_week_btn = ttk.Button(week_frame, text="▶",
                                      command=self.next_week)
        self.next_week_btn.pack(side='left', padx=5)
        
        self.update_week_label()
        
        main_container = ttk.Frame(self)
        main_container.pack(fill='both', expand=True, padx=5, pady=5)
        
        columns = ('time', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday')
        self.schedule_tree = ttk.Treeview(main_container, columns=columns, show='headings')
        
        days = {
            'time': 'Время',
            'monday': 'Понедельник',
            'tuesday': 'Вторник',
            'wednesday': 'Среда',
            'thursday': 'Четверг',
            'friday': 'Пятница'
        }
        
        style = ttk.Style()
        style.configure("Treeview", rowheight=60, font=('Segoe UI', 10))
        style.configure("Treeview.Heading", font=('Segoe UI', 10, 'bold'))
        
        for col in columns:
            self.schedule_tree.heading(col, text=days[col])
            if col == 'time':
                self.schedule_tree.column(col, width=100, anchor='center', stretch=False)
            else:
                self.schedule_tree.column(col, width=180, anchor='center', stretch=True)
        
        y_scrollbar = ttk.Scrollbar(main_container, orient='vertical', command=self.schedule_tree.yview)
        x_scrollbar = ttk.Scrollbar(main_container, orient='horizontal', command=self.schedule_tree.xview)
        
        self.schedule_tree.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        
        self.schedule_tree.grid(row=0, column=0, sticky='nsew')
        y_scrollbar.grid(row=0, column=1, sticky='ns')
        x_scrollbar.grid(row=1, column=0, sticky='ew')
        
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
        
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Редактировать", command=self.edit_lesson)
        self.context_menu.add_command(label="Удалить", command=self.delete_lesson)
        
        self.schedule_tree.bind('<Button-3>', self.show_context_menu)
        
        self.add_time_slots()
        
    def get_unique_classes(self):
        students = self.db.get_all_students()
        classes = set()
        for student in students:
            if student[2] and student[3]:
                classes.add(f"{student[2]}{student[3]}")
        return sorted(list(classes))
        
    def add_time_slots(self):
        for item in self.schedule_tree.get_children():
            self.schedule_tree.delete(item)
        
        time_slots = [
            ('1', '09:00-09:45'),
            ('2', '09:55-10:40'),
            ('3', '10:50-11:35'),
            ('4', '11:55-12:40'),
            ('5', '12:50-13:35'),
            ('6', '13:45-14:30'),
            ('7', '14:40-15:25'),
            ('8', '15:35-16:20')
        ]
        
        for slot in time_slots:
            values = [f"{slot[0]} урок\n{slot[1]}"] + [''] * 5
            self.schedule_tree.insert('', 'end', values=values)
    
    def on_class_selected(self, event=None):
        if not self.class_var.get():
            return
            
        self.add_time_slots()
        
        class_str = self.class_var.get()
        grade = int(''.join(filter(str.isdigit, class_str)))
        class_name = ''.join(filter(str.isalpha, class_str))
        
        schedule = self.db.get_schedule_for_class_by_week(grade, class_name, self.current_week_start)
        
        for day_of_week, lesson_number, subject_name, room, start_time, end_time, schedule_id, subject_id in schedule:
            try:
                item_id = self.schedule_tree.get_children()[lesson_number - 1]
                values = list(self.schedule_tree.item(item_id)['values'])
                values[day_of_week + 1] = f"{subject_name}\n{room if room else ''}"  
                self.schedule_tree.item(item_id, values=values)
            except IndexError as e:
                print(f"Ошибка при добавлении урока: {e}")
                continue
    
    def show_context_menu(self, event):
        item = self.schedule_tree.identify_row(event.y)
        if item:
            self.schedule_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def show_add_dialog(self):
        if not self.class_var.get():
            messagebox.showwarning("Предупреждение", "Выберите класс")
            return
            
        AddLessonDialog(self, self.db, self.class_var.get())
        self.on_class_selected()
    
    def edit_lesson(self):
        selected = self.schedule_tree.selection()
        if not selected:
            return
            
        item = self.schedule_tree.item(selected[0])
        # TODO: Implement edit dialog
        
    def delete_lesson(self):
        selected = self.schedule_tree.selection()
        if not selected:
            return
            
        if messagebox.askyesno("Подтверждение", "Удалить выбранный урок?"):
            # TODO: Implement deletion
            self.on_class_selected()
    
    def update_week_label(self):
        week_end = self.current_week_start + timedelta(days=6)
        self.week_label.config(
            text=f"{self.current_week_start.strftime('%d.%m.%Y')} - {week_end.strftime('%d.%m.%Y')}"
        )
    
    def prev_week(self):
        self.current_week_start -= timedelta(days=7)
        self.update_week_label()
        self.on_class_selected()
    
    def next_week(self):
        self.current_week_start += timedelta(days=7)
        self.update_week_label()
        self.on_class_selected()

class AddLessonDialog:
    def __init__(self, parent, db, class_str):
        self.top = tk.Toplevel(parent)
        self.db = db
        self.parent = parent
        
        self.grade = int(''.join(filter(str.isdigit, class_str)))
        self.class_name = ''.join(filter(str.isalpha, class_str))
        
        ttk.Label(self.top, text="День недели:").pack(pady=5)
        self.day_cb = ttk.Combobox(self.top, values=[
            'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница'
        ])
        self.day_cb.pack(pady=5)
        
        ttk.Label(self.top, text="Номер урока:").pack(pady=5)
        self.lesson_cb = ttk.Combobox(self.top, values=[str(i) for i in range(1, 9)])
        self.lesson_cb.pack(pady=5)
        
        ttk.Label(self.top, text="Предмет:").pack(pady=5)
        subjects = self.db.get_all_subjects()
        self.subjects = subjects
        self.subject_cb = ttk.Combobox(self.top, values=[s[1] for s in subjects])
        self.subject_cb.pack(pady=5)
        
        ttk.Label(self.top, text="Кабинет:").pack(pady=5)
        self.room_entry = ttk.Entry(self.top)
        self.room_entry.pack(pady=5)
        
        ttk.Button(self.top, text="Добавить",
                  command=self.add_lesson).pack(pady=10)
    
    def add_lesson(self):
        try:
            day = self.day_cb.current()
            lesson = int(self.lesson_cb.get())
            subject_idx = self.subject_cb.current()
            room = self.room_entry.get()
            
            if day >= 0 and lesson and subject_idx >= 0 and room:
                subject_id = self.subjects[subject_idx][0]
                time_slots = [
                    ('8:30', '9:15'),
                    ('9:25', '10:10'),
                    ('10:30', '11:15'),
                    ('11:35', '12:20'),
                    ('12:30', '13:15'),
                    ('13:25', '14:10'),
                    ('14:20', '15:05'),
                    ('15:15', '16:00')
                ]
                start_time, end_time = time_slots[lesson - 1]
                
                self.db.add_schedule_item(
                    self.grade, self.class_name, day, lesson,
                    subject_id, room, start_time, end_time
                )
                self.top.destroy()
                messagebox.showinfo("Успех", "Урок добавлен в расписание")
            else:
                messagebox.showerror("Ошибка", "Заполните все поля")
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректные данные") 
