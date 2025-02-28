import tkinter as tk
from tkinter import ttk, messagebox
from database.db_manager import DatabaseManager

class AddSubjectDialog:
    def __init__(self, parent, db):
        self.top = tk.Toplevel(parent)
        self.db = db
        
        ttk.Label(self.top, text="Название предмета:").pack(pady=5)
        self.name_entry = ttk.Entry(self.top, width=30)
        self.name_entry.pack(pady=5)
        
        ttk.Label(self.top, text="Преподаватель:").pack(pady=5)
        self.teacher_entry = ttk.Entry(self.top, width=30)
        self.teacher_entry.pack(pady=5)
        
        ttk.Button(self.top, text="Добавить",
                  command=self.add_subject).pack(pady=10)

    def add_subject(self):
        name = self.name_entry.get()
        teacher = self.teacher_entry.get()
        
        if name and teacher:
            self.db.add_subject(name, teacher)
            self.top.destroy()
            messagebox.showinfo("Успех", "Предмет добавлен")
        else:
            messagebox.showerror("Ошибка", "Заполните все поля")

class EditSubjectDialog:
    def __init__(self, parent, db, values):
        self.top = tk.Toplevel(parent)
        self.db = db
        self.subject_id = values[0]
        
        ttk.Label(self.top, text="Название предмета:").pack(pady=5)
        self.name_entry = ttk.Entry(self.top, width=30)
        self.name_entry.insert(0, values[1])
        self.name_entry.pack(pady=5)
        
        ttk.Label(self.top, text="Преподаватель:").pack(pady=5)
        self.teacher_entry = ttk.Entry(self.top, width=30)
        self.teacher_entry.insert(0, values[2])
        self.teacher_entry.pack(pady=5)
        
        ttk.Button(self.top, text="Сохранить",
                  command=self.save_subject).pack(pady=10)

    def save_subject(self):
        name = self.name_entry.get()
        teacher = self.teacher_entry.get()
        
        if name and teacher:
            self.db.update_subject(self.subject_id, name, teacher)
            self.top.destroy()
            messagebox.showinfo("Успех", "Предмет обновлен")
        else:
            messagebox.showerror("Ошибка", "Заполните все поля")

class SubjectsView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.db = DatabaseManager()
        
        # Создание кнопок управления
        buttons_frame = ttk.Frame(self)
        buttons_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(buttons_frame, text="Добавить предмет",
                  command=self.show_add_dialog).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Редактировать",
                  command=self.edit_selected).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Удалить",
                  command=self.delete_selected).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Обновить",
                  command=self.update_table).pack(side='left', padx=5)
        
        columns = ('id', 'name', 'teacher')
        self.table = ttk.Treeview(self, columns=columns, show='headings')
        
        self.table.heading('id', text='ID')
        self.table.heading('name', text='Название')
        self.table.heading('teacher', text='Преподаватель')
        
        self.table.column('id', width=50)
        self.table.column('name', width=200)
        self.table.column('teacher', width=200)
        
        scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)
        
        self.table.pack(expand=True, fill='both', padx=5, pady=5)
        scrollbar.pack(side='right', fill='y')
        
        self.update_table()
        
        self.pack(fill='both', expand=True)

    def show_add_dialog(self):
        AddSubjectDialog(self, self.db)
    
    #добавляем данных
    def update_table(self):
        for item in self.table.get_children():
            self.table.delete(item)
        
        subjects = self.db.get_all_subjects()
        for subject in subjects:
            self.table.insert('', 'end', values=subject)

    def edit_selected(self):
        selected = self.table.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите предмет для редактирования")
            return
        
        item = self.table.item(selected[0])
        EditSubjectDialog(self, self.db, item['values'])
        self.update_table()
    
    def delete_selected(self):
        selected = self.table.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите предмет для удаления")
            return
        
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этот предмет?"):
            item = self.table.item(selected[0])
            self.db.delete_subject(item['values'][0])
            self.update_table() 
