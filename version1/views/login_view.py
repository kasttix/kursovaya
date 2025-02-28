import tkinter as tk
from tkinter import ttk, messagebox
from database.db_manager import DatabaseManager

class LoginView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.db = DatabaseManager()
        self.setup_ui()
        
    # Создание и размещение элементов
    def setup_ui(self):
        ttk.Label(self, text="Логин:").pack(pady=5)
        self.login_entry = ttk.Entry(self)
        self.login_entry.pack(pady=5)
        
        ttk.Label(self, text="Пароль:").pack(pady=5)
        self.password_entry = ttk.Entry(self, show="*")
        self.password_entry.pack(pady=5)
        
        ttk.Button(self, text="Войти", command=self.login).pack(pady=20)
    
    #Проверка и вход
    def login(self):
        login = self.login_entry.get()
        password = self.password_entry.get()
        
        if login == "teacher" and password == "password":
            self.master.withdraw()
            
            from ..main import TeacherWindow
            main_window = TeacherWindow()
            main_window.protocol("WM_DELETE_WINDOW", lambda: self.on_window_close(main_window))
            main_window.mainloop()
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")
    
    def on_window_close(self, window):
        window.destroy()
        self.master.destroy() 
