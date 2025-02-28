import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkfont
from views.students_view import StudentsView
from views.subjects_view import SubjectsView
from views.grades_view import GradesView
from views.statistics_view import StatisticsView
from views.schedule_view import ScheduleView
from database.db_manager import DatabaseManager

def create_gradient_frame(parent, color1, color2):
    canvas = tk.Canvas(parent, highlightthickness=0)
    canvas.pack(fill='both', expand=True)
    
    def gradient(canvas):
        height = canvas.winfo_height()
        width = canvas.winfo_width()
        for i in range(height):
            ratio = i / height
            r = int((1 - ratio) * int(color1[1:3], 16) + ratio * int(color2[1:3], 16))
            g = int((1 - ratio) * int(color1[3:5], 16) + ratio * int(color2[3:5], 16))
            b = int((1 - ratio) * int(color1[5:7], 16) + ratio * int(color2[5:7], 16))
            color = f'#{r:02x}{g:02x}{b:02x}'
            canvas.create_line(0, i, width, i, fill=color)
    
    canvas.bind('<Configure>', lambda e: gradient(canvas))
    return canvas

class LoginWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Электронный журнал - Вход")
        self.root.geometry("500x700")
        self.root.resizable(False, False)

        self.background = create_gradient_frame(self.root, "#1a237e", "#283593")
        
        style = ttk.Style()
        style.configure('Custom.TFrame', background='white')
        style.configure('Custom.TLabel', 
                       background='white',
                       font=('Segoe UI', 12))
        style.configure('Custom.TButton',
                       font=('Segoe UI', 11, 'bold'),
                       padding=12)
        
        shadow_color = '#1a237e'
        shadows = []
        for i in range(8):
            shadow = tk.Frame(self.background, bg=shadow_color, bd=0)
            shadow.place(relx=0.5, rely=0.5, anchor='center',
                        width=404+i, height=554+i)
            shadows.append(shadow)
        
        main_frame = tk.Frame(self.background, bg='white', bd=0,
                            highlightthickness=1,
                            highlightbackground='#E0E0E0')
        main_frame.place(relx=0.5, rely=0.5, anchor='center',
                        width=400, height=550)
        
        inner_frame = tk.Frame(main_frame, bg='white')
        inner_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Логотип
        logo_text = tk.Label(inner_frame,
                           text="📚",
                           font=('Segoe UI', 32),
                           bg='white',
                           fg='#1a237e')
        logo_text.pack(pady=(0, 10))
        
        title_font = tkfont.Font(family='Segoe UI', size=20, weight='bold')
        title = tk.Label(inner_frame, text="Электронный журнал",
                        font=title_font, bg='white', fg='#1a237e')
        title.pack(pady=(0, 5))
        
        subtitle = tk.Label(inner_frame, text="Система учета успеваемости",
                          font=('Segoe UI', 12), bg='white', fg='#666666')
        subtitle.pack(pady=(0, 20))
        
        entry_style = {'font': ('Segoe UI', 12),
                      'bg': '#F5F5F5',
                      'fg': '#333333',
                      'relief': 'flat',
                      'bd': 1}
        
        tk.Label(inner_frame, text="Логин",
                font=('Segoe UI', 12), bg='white', fg='#333333').pack(anchor='w')
        self.login = tk.Entry(inner_frame, **entry_style)
        self.login.pack(fill='x', pady=(5, 15), ipady=8)
        
        tk.Label(inner_frame, text="Пароль",
                font=('Segoe UI', 12), bg='white', fg='#333333').pack(anchor='w')
        self.password = tk.Entry(inner_frame, show="*", **entry_style)
        self.password.pack(fill='x', pady=(5, 25), ipady=8)
        
        #Кнопки
        button_style = {'font': ('Segoe UI', 12, 'bold'),
                       'relief': 'flat',
                       'bd': 0,
                       'cursor': 'hand2',
                       'width': 20,
                       'height': 1,
                       'wraplength': 0,
                       'justify': 'center',
                       'anchor': 'center'}
        
        teacher_btn = tk.Button(inner_frame,
                              text="ВОЙТИ В СИСТЕМУ",
                              command=self.login_teacher,
                              bg='#1a237e',
                              fg='white',
                              activebackground='#283593',
                              activeforeground='white',
                              **button_style)
        teacher_btn.pack(pady=5)
        
        copyright_label = tk.Label(inner_frame,
                                 text="© 2025 Электронный журнал",
                                 font=('Segoe UI', 9),
                                 bg='white',
                                 fg='#666666')
        copyright_label.pack(side='bottom', pady=(20, 0))
        
        self.db = DatabaseManager()
        
        def on_enter(e):
            e.widget.configure(background='#283593')
        
        def on_leave(e):
            e.widget.configure(background='#1a237e')
        
        teacher_btn.bind('<Enter>', on_enter)
        teacher_btn.bind('<Leave>', on_leave)
        
        main_frame.lift()
        
        self.root.mainloop()
        
    #Проверка данны учителя
    def login_teacher(self):
        if self.login.get() == "teacher" and self.password.get() == "password":
            self.root.destroy()
            TeacherWindow()
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")

class TeacherWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Электронный журнал - Учитель")
        self.root.geometry("1280x800")
        
        style = ttk.Style()
        style.configure('Leftnav.TFrame', background='#1a237e')
        style.configure('Main.TFrame', background='#F5F5F5')
        style.configure('Content.TFrame', background='white')
        
        main_container = ttk.Frame(self.root, style='Main.TFrame')
        main_container.pack(fill='both', expand=True)
        
        # Левая панель
        left_nav = ttk.Frame(main_container, style='Leftnav.TFrame', width=280)
        left_nav.pack(side='left', fill='y')
        left_nav.pack_propagate(False)
        
        header_frame = ttk.Frame(left_nav, style='Leftnav.TFrame')
        header_frame.pack(fill='x', pady=(30, 50))
        
        # Логотип
        logo_text = tk.Label(header_frame,
                           text="📚",
                           font=('Segoe UI', 40),
                           bg='#1a237e',
                           fg='white')
        logo_text.pack(pady=(0, 10))
        
        title = tk.Label(header_frame,
                        text="Электронный\nжурнал",
                        font=('Segoe UI', 18, 'bold'),
                        fg='white',
                        bg='#1a237e',
                        justify='center')
        title.pack()
        
        #Кнопки навигации
        nav_frame = tk.Frame(left_nav, bg='#1a237e')
        nav_frame.pack(fill='x', pady=20)
        
        self.nav_buttons = {}
        
        nav_items = [
            ('students', '👥 Ученики'),
            ('subjects', '📚 Предметы'),
            ('grades', '📊 Оценки'),
            ('statistics', '📈 Статистика'),
            ('schedule', '📅 Расписание')
        ]
        
        for key, text in nav_items:
            btn = tk.Button(nav_frame,
                          text=text,
                          font=('Segoe UI', 13),
                          bg='#1a237e',
                          fg='white',
                          activebackground='#1a237e',
                          activeforeground='white',
                          bd=0,
                          relief='flat',
                          cursor='hand2',
                          pady=15,
                          anchor='w',
                          padx=30,
                          width=25,
                          justify='left')
            btn.pack(pady=3)
            self.nav_buttons[key] = btn
            
            btn.configure(command=lambda k=key: self.show_frame(k))
        
        separator = ttk.Separator(left_nav, orient='horizontal')
        separator.pack(fill='x', pady=20, padx=20)
        
        #Добавляем информацию о пользователе
        user_frame = tk.Frame(left_nav, bg='#1a237e')
        user_frame.pack(fill='x', pady=10, padx=20)
        
        user_icon = tk.Label(user_frame,
                           text="👤",
                           font=('Segoe UI', 24),
                           bg='#1a237e',
                           fg='white')
        user_icon.pack(side='left', padx=(0, 10))
        
        user_info = tk.Frame(user_frame, bg='#1a237e')
        user_info.pack(side='left', fill='x')
        
        tk.Label(user_info,
                text="Учитель",
                font=('Segoe UI', 14, 'bold'),
                bg='#1a237e',
                fg='white').pack(anchor='w')
        
        tk.Label(user_info,
                text="Онлайн",
                font=('Segoe UI', 10),
                bg='#1a237e',
                fg='#90CAF9').pack(anchor='w')
        
        exit_btn = tk.Button(left_nav,
                           text="🚪 Выход из системы",
                           command=self.root.destroy,
                           font=('Segoe UI', 13),
                           bg='#C62828',
                           fg='white',
                           activebackground='#B71C1C',
                           activeforeground='white',
                           bd=0,
                           relief='flat',
                           cursor='hand2',
                           pady=15,
                           width=25)
        exit_btn.pack(side='bottom', pady=20)
        exit_btn.bind('<Enter>', lambda e: e.widget.configure(background='#B71C1C'))
        exit_btn.bind('<Leave>', lambda e: e.widget.configure(background='#C62828'))
        
        content_frame = ttk.Frame(main_container, style='Content.TFrame')
        content_frame.pack(side='right', fill='both', expand=True, padx=30, pady=30)
        
        students_frame = ttk.Frame(content_frame, style='Tab.TFrame')
        subjects_frame = ttk.Frame(content_frame, style='Tab.TFrame')
        grades_frame = ttk.Frame(content_frame, style='Tab.TFrame')
        statistics_frame = ttk.Frame(content_frame, style='Tab.TFrame')
        schedule_frame = ttk.Frame(content_frame, style='Tab.TFrame')
        
        self.frames = {
            'students': students_frame,
            'subjects': subjects_frame,
            'grades': grades_frame,
            'statistics': statistics_frame,
            'schedule': schedule_frame
        }
        
        self.students_view = StudentsView(students_frame)
        self.students_view.pack(fill='both', expand=True, padx=20)
        
        self.subjects_view = SubjectsView(subjects_frame)
        self.subjects_view.pack(fill='both', expand=True, padx=20)
        
        self.grades_view = GradesView(grades_frame)
        self.grades_view.pack(fill='both', expand=True, padx=20)
        
        self.statistics_view = StatisticsView(statistics_frame)
        self.statistics_view.pack(fill='both', expand=True, padx=20)
        
        self.schedule_view = ScheduleView(schedule_frame)
        self.schedule_view.pack(fill='both', expand=True, padx=20)
        
        for frame in self.frames.values():
            frame.pack_forget()
            
        self.show_frame('students')
        
        self.root.mainloop()
    
    def show_frame(self, frame_name):
        for frame in self.frames.values():
            frame.pack_forget()
        
        self.frames[frame_name].pack(fill='both', expand=True)
        
        for btn in self.nav_buttons.values():
            btn.configure(background='#1a237e')
        self.nav_buttons[frame_name].configure(background='#283593')

    def update_class_lists(self):
        classes = self.students_view.get_unique_classes()
        
        #Обновляем списки в каждом представлении
        self.grades_view.class_cb['values'] = classes
        self.statistics_view.class_cb['values'] = classes
        self.statistics_view.student_class_cb['values'] = classes
        self.schedule_view.class_cb['values'] = classes

if __name__ == "__main__":
    #Инициализируем базу данных при первом запуске
    db = DatabaseManager()
    db.init_database()
    
    app = LoginWindow()
