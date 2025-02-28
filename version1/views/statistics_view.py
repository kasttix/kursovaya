import tkinter as tk
from tkinter import ttk, messagebox
from database.db_manager import DatabaseManager

class StatisticsView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.db = DatabaseManager()
        self.setup_ui()
        
    def setup_ui(self):
        main_container = ttk.Frame(self)
        main_container.pack(fill='both', expand=True, padx=5, pady=5)

        top_panel = ttk.Frame(main_container)
        top_panel.pack(fill='x', padx=5, pady=5)
        
        stats_frame = ttk.LabelFrame(top_panel, text="Тип статистики")
        stats_frame.pack(side='left', padx=5)
        
        self.stats_type = tk.StringVar(value="class")
        ttk.Radiobutton(stats_frame, text="Успеваемость класса", 
                       variable=self.stats_type, value="class",
                       command=self.on_stats_type_changed).pack(side='left', padx=5)
        ttk.Radiobutton(stats_frame, text="Успеваемость ученика", 
                       variable=self.stats_type, value="student",
                       command=self.on_stats_type_changed).pack(side='left', padx=5)
        
        class_frame = ttk.LabelFrame(top_panel, text="Класс")
        class_frame.pack(side='left', padx=5)
        
        self.grade_combo = ttk.Combobox(class_frame, values=['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11'])
        self.grade_combo.pack(side='left', padx=5, pady=5)
        self.grade_combo.bind('<<ComboboxSelected>>', lambda e: self.on_grade_selected())
        
        self.class_combo = ttk.Combobox(class_frame, values=['А', 'Б', 'В', 'Г'])
        self.class_combo.pack(side='left', padx=5, pady=5)
        self.class_combo.bind('<<ComboboxSelected>>', lambda e: self.on_class_selected())
        
        # Выбор ученика
        self.student_frame = ttk.LabelFrame(top_panel, text="Ученик")
        self.student_frame.pack(side='left', padx=5, fill='x', expand=True)
        
        self.student_combo = ttk.Combobox(self.student_frame)
        self.student_combo.pack(side='left', padx=5, pady=5, fill='x', expand=True)
        self.student_combo.bind('<<ComboboxSelected>>', lambda e: self.update_statistics())
        
        ttk.Button(top_panel, text="Обновить", 
                  command=self.update_statistics).pack(side='right', padx=5)
        
        self.create_stats_table(main_container)
        
        self.student_frame.pack_forget()
    
    def create_stats_table(self, parent):
        table_frame = ttk.LabelFrame(parent, text="Статистика оценок")
        table_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        columns = ('subject', 'average')
        self.stats_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
        
        self.stats_tree.heading('subject', text='Предмет')
        self.stats_tree.heading('average', text='Средний балл')
        
        self.stats_tree.column('subject', width=300)
        self.stats_tree.column('average', width=150, anchor='center')
        
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.stats_tree.yview)
        self.stats_tree.configure(yscrollcommand=scrollbar.set)
        
        self.stats_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
    
    def on_stats_type_changed(self):
        if self.stats_type.get() == "class":
            self.student_frame.pack_forget()
        else:
            self.student_frame.pack(side='left', padx=5, fill='x', expand=True)
        self.update_statistics()
    
    def on_grade_selected(self):
        if self.grade_combo.get():
            self.on_class_selected()
    
    def on_class_selected(self):
        if not self.grade_combo.get() or not self.class_combo.get():
            return
            
        self.student_combo.set('')
        self.student_combo['values'] = []
        
        students = self.db.get_students_by_class(
            int(self.grade_combo.get()),
            self.class_combo.get()
        )
        
        student_list = []
        student_ids = []
        for student in students:
            student_list.append(student[1])
            student_ids.append(student[0])
            
        self.student_combo['values'] = student_list
        self.student_combo.student_ids = student_ids
        
        self.update_statistics()
    
    def update_statistics(self):
        for item in self.stats_tree.get_children():
            self.stats_tree.delete(item)
        
        if not self.grade_combo.get() or not self.class_combo.get():
            return
            
        if self.stats_type.get() == "class":
            self.show_class_statistics()
        else:
            if not self.student_combo.get():
                return
            self.show_student_statistics()
    
    def show_class_statistics(self):
        grade = int(self.grade_combo.get())
        class_name = self.class_combo.get()
        
        stats = self.db.get_class_average_grades(grade, class_name)
        
        for stat in stats:
            subject_name = stat[0]
            average = stat[1]
            
            self.stats_tree.insert('', 'end', values=(
                subject_name,
                f"{average:.2f}" if average else "0.00"
            ))
    
    def show_student_statistics(self):
        idx = self.student_combo.current()
        if idx < 0:
            return
            
        student_id = self.student_combo.student_ids[idx]
        
        stats = self.db.get_student_detailed_stats(student_id)
        
        for stat in stats:
            subject_name = stat[0]
            average = stat[1]
            count_5 = stat[2]
            count_4 = stat[3]
            count_3 = stat[4]
            count_2 = stat[5]
            total = stat[6]
            
            self.stats_tree.insert('', 'end', values=(
                subject_name,
                f"{average:.2f}" if average else "0.00",
                count_5,
                count_4,
                count_3,
                count_2,
                total
            )) 
