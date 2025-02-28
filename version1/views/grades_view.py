import tkinter as tk
from tkinter import ttk, messagebox
from database.db_manager import DatabaseManager
from datetime import datetime, timedelta
from .schedule_dialog import AddScheduleDialog

class AddGradeDialog:
    def __init__(self, parent, db, student_id, subject_id, date):
        self.top = tk.Toplevel(parent)
        self.db = db
        self.student_id = student_id
        self.subject_id = subject_id
        self.date = date
        
        self.top.title("Добавить оценку")
        
        # Создание и размещение элементов
        ttk.Label(self.top, text="Оценка:").pack(pady=5)
        self.grade_cb = ttk.Combobox(self.top, values=['2', '3', '4', '5'])
        self.grade_cb.pack(pady=5)
        
        ttk.Button(self.top, text="Добавить",
                  command=self.add_grade).pack(pady=10)

    def add_grade(self):
        grade = self.grade_cb.get()
        if grade:
            try:
                self.db.add_grade(self.student_id, self.subject_id, int(grade), self.date)
                self.top.destroy()
                messagebox.showinfo("Успех", "Оценка добавлена")
            except ValueError:
                messagebox.showerror("Ошибка", "Некорректные данные")
        else:
            messagebox.showerror("Ошибка", "Выберите оценку")

class EditGradeDialog:
    def __init__(self, parent, db, values):
        self.top = tk.Toplevel(parent)
        self.db = db
        self.grade_id = values[0]
        
        ttk.Label(self.top, text="Ученик:").pack(pady=5)
        self.student_cb = ttk.Combobox(self.top, values=[s[1] for s in self.db.get_all_students()])
        self.student_cb.pack(pady=5)
        
        ttk.Label(self.top, text="Предмет:").pack(pady=5)
        self.subject_cb = ttk.Combobox(self.top, values=[s[1] for s in self.db.get_all_subjects()])
        self.subject_cb.pack(pady=5)
        
        ttk.Label(self.top, text="Оценка:").pack(pady=5)
        self.grade_cb = ttk.Combobox(self.top, values=['2', '3', '4', '5'])
        self.grade_cb.pack(pady=5)
        
        self.student_cb.set(values[1])
        self.subject_cb.set(values[2])
        self.grade_cb.set(values[3])
        
        ttk.Button(self.top, text="Сохранить",
                  command=self.save_grade).pack(pady=10)

    def save_grade(self):
        try:
            student_idx = self.student_cb.current()
            subject_idx = self.subject_cb.current()
            grade = self.grade_cb.get()
            
            if student_idx >= 0 and subject_idx >= 0 and grade:
                student_id = self.db.get_all_students()[student_idx][0]
                subject_id = self.db.get_all_subjects()[subject_idx][0]
                
                self.db.update_grade(self.grade_id, student_id, subject_id, int(grade))
                self.top.destroy()
                messagebox.showinfo("Успех", "Оценка обновлена")
            else:
                messagebox.showerror("Ошибка", "Заполните все поля")
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректные данные")

class GradesView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.db = DatabaseManager()
        self.selected_student_id = None
        self.selected_grade = None
        self.selected_class = None
        self.current_week_start = self.get_current_week_start()
        self.setup_ui()
        
    def get_current_week_start(self):
        today = datetime.now()
        return today - timedelta(days=today.weekday())
     
    #Панель
    def setup_ui(self):
        main_container = ttk.Frame(self)
        main_container.pack(fill='both', expand=True, padx=5, pady=5)

        top_panel = ttk.Frame(main_container)
        top_panel.pack(fill='x', padx=5, pady=5)
        
        class_frame = ttk.LabelFrame(top_panel, text="Класс")
        class_frame.pack(side='left', padx=5)
        
        self.grade_combo = ttk.Combobox(class_frame, values=['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11'])
        self.grade_combo.pack(side='left', padx=5, pady=5)
        self.grade_combo.bind('<<ComboboxSelected>>', lambda e: self.on_grade_selected())
        
        self.class_combo = ttk.Combobox(class_frame, values=['А', 'Б', 'В', 'Г'])
        self.class_combo.pack(side='left', padx=5, pady=5)
        self.class_combo.bind('<<ComboboxSelected>>', lambda e: self.on_class_selected())
        
        student_frame = ttk.LabelFrame(top_panel, text="Ученик")
        student_frame.pack(side='left', padx=5, fill='x', expand=True)
        
        self.student_combo = ttk.Combobox(student_frame)
        self.student_combo.pack(side='left', padx=5, pady=5, fill='x', expand=True)
        self.student_combo.bind('<<ComboboxSelected>>', lambda e: self.on_student_selected())
        
        week_frame = ttk.Frame(top_panel)
        week_frame.pack(side='right', padx=5)
        
        ttk.Button(week_frame, text="←",
                  command=self.prev_week).pack(side='left', padx=2)
                  
        self.week_label = ttk.Label(week_frame, text=self.get_week_label())
        self.week_label.pack(side='left', padx=5)
        
        ttk.Button(week_frame, text="→",
                  command=self.next_week).pack(side='left', padx=2)
        
        ttk.Button(week_frame, text="Обновить",
                  command=self.refresh_schedule).pack(side='left', padx=5)
        
        schedule_frame = ttk.LabelFrame(main_container, text="Расписание и оценки")
        schedule_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        columns = ('time', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday')
        self.schedule_tree = ttk.Treeview(schedule_frame, columns=columns, show='headings', height=8)
        
        days = {
            'time': 'Время',
            'monday': 'Понедельник',
            'tuesday': 'Вторник',
            'wednesday': 'Среда',
            'thursday': 'Четверг',
            'friday': 'Пятница'
        }
        
        for col in columns:
            self.schedule_tree.heading(col, text=days[col])
            if col == 'time':
                self.schedule_tree.column(col, width=100, anchor='center')
            else:
                self.schedule_tree.column(col, width=150, anchor='center')

        scrollbar = ttk.Scrollbar(schedule_frame, orient='vertical', command=self.schedule_tree.yview)
        self.schedule_tree.configure(yscrollcommand=scrollbar.set)
        
        self.schedule_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.schedule_tree.bind('<Double-1>', self.on_schedule_double_click)

        self.add_time_slots()
    
    def get_week_label(self):
        week_end = self.current_week_start + timedelta(days=4)
        return f"{self.current_week_start.strftime('%d.%m')} - {week_end.strftime('%d.%m.%Y')}"
    
    def prev_week(self):
        self.current_week_start -= timedelta(days=7)
        self.week_label.config(text=self.get_week_label())
        self.refresh_schedule()
    
    def next_week(self):
        self.current_week_start += timedelta(days=7)
        self.week_label.config(text=self.get_week_label())
        self.refresh_schedule()
    
    def current_week(self):
        self.current_week_start = self.get_current_week_start()
        self.week_label.config(text=self.get_week_label())
        self.refresh_schedule()
    
    def on_grade_selected(self):
        self.selected_grade = self.grade_combo.get()
        if self.selected_grade:
            self.on_class_selected()
    
    def on_class_selected(self):
        if not self.selected_grade:
            return
            
        self.selected_class = self.class_combo.get()
        if not self.selected_class:
            return
            
        self.student_combo.set('')
        self.student_combo['values'] = []

        students = self.db.get_students_by_class(int(self.selected_grade), self.selected_class)

        student_list = []
        student_ids = []
        for student in students:
            student_list.append(student[1])
            student_ids.append(student[0])  
            
        self.student_combo['values'] = student_list
        self.student_combo.student_ids = student_ids

        self.load_schedule()
    
    def on_student_selected(self):
        if hasattr(self.student_combo, 'student_ids'):
            idx = self.student_combo.current()
            if idx >= 0:
                self.selected_student_id = self.student_combo.student_ids[idx]
                self.load_student_grades()
    
    def show_add_lesson_dialog(self):
        if not self.selected_grade or not self.selected_class:
            messagebox.showwarning("Предупреждение", "Выберите класс")
            return

        selection = self.schedule_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите ячейку в расписании")
            return
            
        item = selection[0]
        column = self.schedule_tree.identify_column(self.schedule_tree.winfo_pointerx() - self.schedule_tree.winfo_rootx())

        try:
            lesson_number = int(self.schedule_tree.item(item)['values'][0].split()[0])
            day_of_week = int(column[1]) - 2
            
            if 0 <= day_of_week <= 4:
                dialog = AddScheduleDialog(
                    self,
                    self.db,
                    int(self.selected_grade),
                    self.selected_class,
                    day_of_week,
                    lesson_number
                )
                self.wait_window(dialog.top)
                self.refresh_schedule()
        except (ValueError, IndexError):
            messagebox.showerror("Ошибка", "Некорректная ячейка расписания")
    
    def refresh_schedule(self):
        """Обновляет отображение расписания"""
        self.load_schedule()
        if self.selected_student_id:
            self.load_student_grades()
    
    def load_schedule(self):
        """Загружает расписание для выбранного класса"""
        if not self.selected_grade or not self.selected_class:
            return

        for item in self.schedule_tree.get_children():
            self.schedule_tree.delete(item)

        schedule = self.db.get_schedule_for_class_by_week(
            int(self.selected_grade), 
            self.selected_class,
            self.current_week_start
        )

        schedule_dict = {}
        for lesson in schedule:
            day = lesson[0]  # day_of_week
            num = lesson[1]  # lesson_number
            if (day, num) not in schedule_dict:
                schedule_dict[(day, num)] = lesson

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

        for slot_num, slot_time in time_slots:
            values = [f"{slot_num} урок\n{slot_time}"]
            tags = []

            for day in range(5):
                lesson = schedule_dict.get((day, int(slot_num)))
                if lesson:
                    subject_name = lesson[2]
                    room = lesson[3]
                    subject_id = lesson[7]
                    values.append(f"{subject_name}\n{room if room else ''}")
                    tags.append(f"subject_{subject_id}")
                else:
                    values.append('')
                    tags.append('')

            self.schedule_tree.insert('', 'end', values=values, tags=tags)
    
    def load_student_grades(self):
        if not self.selected_student_id:
            return

        schedule = self.db.get_schedule_for_class_by_week(
            int(self.selected_grade),
            self.selected_class,
            self.current_week_start
        )
        grades = self.db.get_student_grades_by_week(
            self.selected_student_id,
            self.current_week_start
        )

        grades_dict = {}
        for grade in grades:
            day = int(grade['weekday']) - 1
            if day == -1:
                day = 6
            subject_id = grade['subject_id']
            grades_dict[(day, subject_id)] = grade['value']

        items = self.schedule_tree.get_children()
        for i, item in enumerate(items):
            values = list(self.schedule_tree.item(item)['values'])
            for day in range(5):
                lesson = next(
                    (l for l in schedule if l[0] == day and l[1] == i + 1),
                    None
                )
                if lesson:
                    subject_id = lesson[7]
                    grade = grades_dict.get((day, subject_id))
                    col_idx = day + 1
                    current_value = values[col_idx]
                    if grade:
                        values[col_idx] = f"{current_value}\nОценка: {grade}"
                    else:
                        values[col_idx] = current_value.split('\nОценка:')[0]
            self.schedule_tree.item(item, values=values)
    
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
            self.schedule_tree.insert('', 'end', values=(
                f"{slot[0]} урок\n{slot[1]}", '', '', '', '', ''
            ))
    
    def on_schedule_double_click(self, event):
        if not self.selected_student_id:
            messagebox.showwarning("Предупреждение", "Выберите ученика")
            return

        item = self.schedule_tree.identify('item', event.x, event.y)
        column = self.schedule_tree.identify_column(event.x)
        
        if not item or not column:
            return

        col_idx = int(column[1]) - 1
        if col_idx == 0:
            return

        tags = self.schedule_tree.item(item)['tags']
        if not tags or not tags[col_idx - 1]:
            return
            
        try:
            subject_id = int(tags[col_idx - 1].split('_')[1])

            date = self.current_week_start + timedelta(days=col_idx - 1)

            dialog = AddGradeDialog(
                self,
                self.db,
                self.selected_student_id,
                subject_id,
                date.isoformat()
            )
            self.wait_window(dialog.top)
            self.load_student_grades()
            
        except (ValueError, IndexError):
            messagebox.showerror("Ошибка", "Не удалось определить предмет")
    
    def show_statistics(self):
        if not self.selected_student_id:
            messagebox.showwarning("Предупреждение", "Выберите ученика")
            return

        stats_window = tk.Toplevel(self)
        stats_window.title("Статистика успеваемости")
        stats_window.geometry("800x600")

        stats = self.db.get_student_detailed_stats(self.selected_student_id)

        columns = ('subject', 'average')
        tree = ttk.Treeview(stats_window, columns=columns, show='headings', height=10)

        tree.heading('subject', text='Предмет')
        tree.heading('average', text='Средний балл')

        tree.column('subject', width=300)
        tree.column('average', width=150, anchor='center')

        for stat in stats:
            tree.insert('', 'end', values=(
                stat[0],
                f"{stat[1]:.2f}" if stat[1] else "0.00"
            ))

        scrollbar = ttk.Scrollbar(stats_window, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        scrollbar.pack(side='right', fill='y')

        figure = Figure(figsize=(8, 4), dpi=100)
        plot = figure.add_subplot(1, 1, 1)

        subjects = [stat[0] for stat in stats]
        averages = [stat[1] if stat[1] else 0 for stat in stats]

        bars = plot.bar(subjects, averages)
        plot.set_ylim(0, 5)
        plot.grid(True, axis='y')

        plot.tick_params(axis='x', rotation=45)

        for bar in bars:
            height = bar.get_height()
            plot.text(bar.get_x() + bar.get_width()/2., height,
                     f'{height:.2f}',
                     ha='center', va='bottom')

        canvas = FigureCanvasTkAgg(figure, stats_window)
        canvas.draw()

        graph_frame = ttk.Frame(stats_window)
        graph_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        canvas.get_tk_widget().pack(in_=graph_frame, fill='both', expand=True)

        ttk.Button(stats_window, text="Закрыть",
                  command=stats_window.destroy).pack(pady=5)
    
    def update_statistics(self):
        if not self.selected_grade or not self.selected_class:
            return

        for item in self.stats_tree.get_children():
            self.stats_tree.delete(item)

        stats = self.db.get_class_average_grades(int(self.selected_grade), self.selected_class)

        for stat in stats:
            self.stats_tree.insert('', 'end', values=(
                stat[0],
                f"{stat[1]:.2f}" if stat[1] else "0.00"
            )) 
