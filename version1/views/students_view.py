import tkinter as tk
from tkinter import ttk, messagebox
from database.db_manager import DatabaseManager
import sqlite3
from datetime import datetime

class AddStudentDialog:
    def __init__(self, parent, db, grade, class_name):
        self.top = tk.Toplevel(parent)
        self.db = db
        
        # Создание элементов
        ttk.Label(self.top, text="ФИО:").pack(pady=5)
        self.name_entry = ttk.Entry(self.top, width=30)
        self.name_entry.pack(pady=5)
        
        ttk.Label(self.top, text="Класс:").pack(pady=5)
        self.grade_entry = ttk.Entry(self.top, width=10)
        self.grade_entry.insert(0, str(grade))
        self.grade_entry.pack(pady=5)
        
        ttk.Label(self.top, text="Буква класса:").pack(pady=5)
        self.class_entry = ttk.Entry(self.top, width=10)
        self.class_entry.insert(0, class_name)
        self.class_entry.pack(pady=5)
        
        ttk.Label(self.top, text="Логин:").pack(pady=5)
        self.login_entry = ttk.Entry(self.top, width=20)
        self.login_entry.pack(pady=5)
        
        ttk.Label(self.top, text="Пароль:").pack(pady=5)
        self.password_entry = ttk.Entry(self.top, width=20, show="*")
        self.password_entry.pack(pady=5)
        
        ttk.Button(self.top, text="Добавить",
                  command=self.add_student).pack(pady=10)

    def add_student(self):
        name = self.name_entry.get()
        grade = self.grade_entry.get()
        class_name = self.class_entry.get()
        login = self.login_entry.get()
        password = self.password_entry.get()
        
        if name and grade and class_name and login and password:
            try:
                self.db.add_student(name, int(grade), class_name, login, password)
                self.top.destroy()
                messagebox.showinfo("Успех", "Ученик добавлен")
            except ValueError:
                messagebox.showerror("Ошибка", "Класс должен быть числом")
            except sqlite3.IntegrityError:
                messagebox.showerror("Ошибка", "Такой логин уже существует")
        else:
            messagebox.showerror("Ошибка", "Заполните все поля")

class EditStudentDialog:
    def __init__(self, parent, db, values, grade, class_name):
        self.top = tk.Toplevel(parent)
        self.db = db
        self.student_id = values[0]
        
        # Создаем и размещаем элементы
        ttk.Label(self.top, text="ФИО:").pack(pady=5)
        self.name_entry = ttk.Entry(self.top, width=30)
        self.name_entry.insert(0, values[1])  # Имя
        self.name_entry.pack(pady=5)
        
        ttk.Label(self.top, text="Класс:").pack(pady=5)
        self.grade_entry = ttk.Entry(self.top, width=10)
        self.grade_entry.insert(0, str(grade))
        self.grade_entry.pack(pady=5)
        
        ttk.Label(self.top, text="Буква класса:").pack(pady=5)
        self.class_entry = ttk.Entry(self.top, width=10)
        self.class_entry.insert(0, class_name)
        self.class_entry.pack(pady=5)
        
        ttk.Button(self.top, text="Сохранить",
                  command=self.save_student).pack(pady=10)

    def save_student(self):
        name = self.name_entry.get()
        grade = self.grade_entry.get()
        class_name = self.class_entry.get()
        
        if name and grade and class_name:
            try:
                self.db.update_student(self.student_id, name, int(grade), class_name)
                self.top.destroy()
                messagebox.showinfo("Успех", "Данные ученика обновлены")
            except ValueError:
                messagebox.showerror("Ошибка", "Класс должен быть числом")
        else:
            messagebox.showerror("Ошибка", "Заполните все поля")

class AddClassDialog:
    def __init__(self, parent, db):
        self.top = tk.Toplevel(parent)
        self.db = db
        self.parent = parent
        self.main_window = self.find_main_window(parent)
        self.top.title("Добавить класс")
        
        ttk.Label(self.top, text="Номер класса:").pack(pady=5)
        self.grade_entry = ttk.Entry(self.top, width=10)
        self.grade_entry.pack(pady=5)
        
        ttk.Label(self.top, text="Буква класса:").pack(pady=5)
        self.class_entry = ttk.Entry(self.top, width=10)
        self.class_entry.pack(pady=5)
        
        ttk.Button(self.top, text="Добавить",
                  command=self.add_class).pack(pady=10)

    def find_main_window(self, widget):
        parent = widget
        while parent:
            if hasattr(parent, 'update_class_lists'):
                return parent
            if hasattr(parent, 'master'):
                parent = parent.master
            else:
                break
        return None

    def add_class(self):
        grade = self.grade_entry.get()
        class_name = self.class_entry.get()
        
        if grade and class_name:
            try:
                grade = int(grade)
                if grade < 1 or grade > 11:
                    messagebox.showerror("Ошибка", "Номер класса должен быть от 1 до 11")
                    return
                    
                if not class_name.isalpha() or len(class_name) != 1:
                    messagebox.showerror("Ошибка", "Буква класса должна быть одной буквой")
                    return
                    
                classes = self.parent.get_unique_classes()
                new_class = f"{grade}{class_name}"
                if new_class in classes:
                    messagebox.showerror("Ошибка", "Такой класс уже существует")
                    return
                    
                self.top.destroy()
                
                classes.append(new_class)
                classes.sort()
                self.parent.class_cb['values'] = classes
                self.parent.class_var.set(new_class)
                self.parent.on_class_selected()
                
                if self.main_window:
                    self.main_window.update_class_lists()
                
                messagebox.showinfo("Успех", "Класс добавлен")
                
            except ValueError:
                messagebox.showerror("Ошибка", "Номер класса должен быть числом")
        else:
            messagebox.showerror("Ошибка", "Заполните все поля")

class StudentsView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.db = DatabaseManager()
        self.setup_ui()
        self.pack(fill='both', expand=True)
        
    #Панель
    def setup_ui(self):
        class_frame = ttk.Frame(self)
        class_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(class_frame, text="Класс:").pack(side='left', padx=5)
        
        classes = self.get_unique_classes()
        self.class_var = tk.StringVar()
        self.class_cb = ttk.Combobox(class_frame, textvariable=self.class_var, values=classes)
        self.class_cb.pack(side='left', padx=5)
        self.class_cb.bind('<<ComboboxSelected>>', self.on_class_selected)
        
        #Добавление кнопок управления
        ttk.Button(class_frame, text="Добавить класс",
                  command=self.show_add_class_dialog).pack(side='left', padx=5)
        
        buttons_frame = ttk.Frame(self)
        buttons_frame.pack(fill='x', padx=5, pady=5)
        
        self.add_button = ttk.Button(buttons_frame, text="Добавить ученика",
                  command=self.show_add_dialog, state='disabled')
        self.add_button.pack(side='left', padx=5)
        
        self.edit_button = ttk.Button(buttons_frame, text="Редактировать",
                  command=self.edit_selected, state='disabled')
        self.edit_button.pack(side='left', padx=5)
        
        self.delete_button = ttk.Button(buttons_frame, text="Удалить",
                  command=self.delete_selected, state='disabled')
        self.delete_button.pack(side='left', padx=5)
        
        self.refresh_button = ttk.Button(buttons_frame, text="Обновить",
                  command=self.load_students, state='disabled')
        self.refresh_button.pack(side='left', padx=5)
        
        columns = ('id', 'name', 'class', 'last_login')
        self.tree = ttk.Treeview(self, columns=columns, show='headings')
        
        self.tree.heading('id', text='ID')
        self.tree.heading('name', text='ФИО')
        self.tree.heading('class', text='Класс')
        self.tree.heading('last_login', text='Последний вход')
        
        self.tree.column('id', width=50)
        self.tree.column('name', width=200)
        self.tree.column('class', width=100)
        self.tree.column('last_login', width=150)
        
        scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        scrollbar.pack(side='right', fill='y')

    def get_unique_classes(self):
        students = self.db.get_all_students()
        classes = set()
        for student in students:
            if student[2] and student[3]: 
                classes.add(f"{student[2]}{student[3]}")
        return sorted(list(classes))
    
    def on_class_selected(self, event=None):
        """Обработчик выбора класса"""
        if not self.class_var.get():
            return
            
        self.add_button['state'] = 'normal'
        self.edit_button['state'] = 'normal'
        self.delete_button['state'] = 'normal'
        self.refresh_button['state'] = 'normal'
        
        self.load_students()
    
    def load_students(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not self.class_var.get():
            return
            
        class_str = self.class_var.get()
        grade = int(''.join(filter(str.isdigit, class_str)))
        class_name = ''.join(filter(str.isalpha, class_str))
        
        students = self.db.get_students_by_class(grade, class_name)
        
        for student in students:
            student_id, name, grade, class_name = student
            class_str = f"{grade}{class_name}"
            self.tree.insert('', 'end', values=(student_id, name, class_str, ""))

    def show_add_dialog(self):
        if not self.class_var.get():
            messagebox.showwarning("Предупреждение", "Выберите класс")
            return
            
        class_str = self.class_var.get()
        grade = int(''.join(filter(str.isdigit, class_str)))
        class_name = ''.join(filter(str.isalpha, class_str))
        
        dialog = AddStudentDialog(self, self.db, grade, class_name)
        self.wait_window(dialog.top)
        self.load_students()

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите ученика для удаления")
            return
        
        item = self.tree.item(selected[0])
        student_name = item['values'][1]
        
        if messagebox.askyesno("Подтверждение", 
                             f"Вы уверены, что хотите удалить ученика {student_name}?\n"
                             "Все его оценки также будут удалены."):
            self.db.delete_student(item['values'][0])  # Передаем ID
            self.load_students()
            messagebox.showinfo("Успех", "Ученик удален")

    def edit_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите ученика для редактирования")
            return
        
        item = self.tree.item(selected[0])
        student_id = item['values'][0]
        
        conn = sqlite3.connect(self.db.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, grade, class_name FROM students WHERE id = ?', (student_id,))
        student_data = cursor.fetchone()
        conn.close()
        
        if student_data:
            class_str = self.class_var.get()
            grade = int(''.join(filter(str.isdigit, class_str)))
            class_name = ''.join(filter(str.isalpha, class_str))
            
            EditStudentDialog(self, self.db, student_data, grade, class_name)
            self.load_students()

    def update_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        students = self.db.get_all_students()
        for student in students:
            self.tree.insert('', 'end', values=student)

    def show_add_class_dialog(self):
        AddClassDialog(self, self.db)

    def show_add_dialog(self):
        if not self.class_var.get():
            messagebox.showwarning("Предупреждение", "Выберите класс")
            return
            
        class_str = self.class_var.get()
        grade = int(''.join(filter(str.isdigit, class_str)))
        class_name = ''.join(filter(str.isalpha, class_str))
        
        dialog = AddStudentDialog(self, self.db, grade, class_name)
        self.wait_window(dialog.top)
        self.load_students() 
