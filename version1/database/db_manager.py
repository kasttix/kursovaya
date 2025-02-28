import sqlite3
from datetime import datetime, timedelta

class DatabaseManager:
    def __init__(self, db_name="school.db"):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Создаем таблицу students
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                grade INTEGER,
                class_name TEXT,
                login TEXT UNIQUE,
                password TEXT,
                last_login TEXT
            )
        ''')
        
        # Создаем таблицу subjects
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                teacher TEXT
            )
        ''')
        
        # Создаем таблицу grades
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS grades (
                id INTEGER PRIMARY KEY,
                student_id INTEGER,
                subject_id INTEGER,
                value INTEGER,
                date TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students (id),
                FOREIGN KEY (subject_id) REFERENCES subjects (id)
            )
        ''')

        # Создаем таблицу schedule
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS schedule (
                id INTEGER PRIMARY KEY,
                grade INTEGER,
                class_name TEXT,
                day_of_week INTEGER,  -- 0 = Понедельник, 6 = Воскресенье
                lesson_number INTEGER,  -- Номер урока (1-8)
                subject_id INTEGER,
                room_number TEXT,
                start_time TEXT,
                end_time TEXT,
                FOREIGN KEY (subject_id) REFERENCES subjects (id)
            )
        ''')
        
        conn.commit()
        conn.close()

    def add_student(self, name, grade, class_name, login, password):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO students (name, grade, class_name, login, password)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, grade, class_name, login, password))
        student_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return student_id

    def add_subject(self, name, teacher):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO subjects (name, teacher)
            VALUES (?, ?)
        ''', (name, teacher))
        subject_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return subject_id

    def add_grade(self, student_id, subject_id, value, date=None):
        if date is None:
            date = datetime.now().date().isoformat()
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id FROM grades 
            WHERE student_id = ? AND subject_id = ? AND date = ?
        ''', (student_id, subject_id, date))
        existing_grade = cursor.fetchone()
        
        if existing_grade:
            cursor.execute('''
                UPDATE grades 
                SET value = ? 
                WHERE student_id = ? AND subject_id = ? AND date = ?
            ''', (value, student_id, subject_id, date))
        else:
            cursor.execute('''
                INSERT INTO grades (student_id, subject_id, value, date)
                VALUES (?, ?, ?, ?)
            ''', (student_id, subject_id, value, date))
        
        grade_id = cursor.lastrowid if not existing_grade else existing_grade[0]
        conn.commit()
        conn.close()
        return grade_id

    def get_all_students(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM students')
        students = cursor.fetchall()
        conn.close()
        return students

    def get_all_subjects(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM subjects')
        subjects = cursor.fetchall()
        conn.close()
        return subjects

    def get_students_by_class(self, grade, class_name):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, grade, class_name
            FROM students
            WHERE grade = ? AND class_name = ?
            ORDER BY name
        ''', (grade, class_name))
        students = cursor.fetchall()
        conn.close()
        return students

    def get_schedule_by_class(self, grade, class_name):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT schedule.lesson_number, schedule.day_of_week, 
                   subjects.name, schedule.room_number,
                   schedule.start_time, schedule.end_time, subjects.id
            FROM schedule
            LEFT JOIN subjects ON schedule.subject_id = subjects.id
            WHERE schedule.grade = ? AND schedule.class_name = ?
            ORDER BY schedule.lesson_number, schedule.day_of_week
        ''', (grade, class_name))
        schedule = cursor.fetchall()
        conn.close()
        return schedule

    def get_student_grades_for_subject(self, student_id, subject_id, date):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT value
            FROM grades
            WHERE student_id = ? AND subject_id = ? AND date = ?
        ''', (student_id, subject_id, date))
        grade = cursor.fetchone()
        conn.close()
        return grade[0] if grade else None

    def update_student(self, student_id, name, grade, class_name):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE students
            SET name = ?, grade = ?, class_name = ?
            WHERE id = ?
        ''', (name, grade, class_name, student_id))
        conn.commit()
        conn.close()

    def delete_student(self, student_id):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM grades WHERE student_id = ?', (student_id,))
        cursor.execute('DELETE FROM students WHERE id = ?', (student_id,))
        conn.commit()
        conn.close()

    def update_grade(self, grade_id, student_id, subject_id, value, date=None):
        if date is None:
            date = datetime.now()
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE grades
            SET student_id = ?, subject_id = ?, value = ?, date = ?
            WHERE id = ?
        ''', (student_id, subject_id, value, date, grade_id))
        conn.commit()
        conn.close()

    def delete_grade(self, grade_id):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM grades WHERE id = ?', (grade_id,))
        conn.commit()
        conn.close()

    def add_schedule_entry(self, grade, class_name, day_of_week, lesson_number, subject_id, room_number=None):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Определяем время начала и конца урока
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
        
        start_time, end_time = time_slots.get(lesson_number, (None, None))
        
        cursor.execute('''
            INSERT INTO schedule (grade, class_name, day_of_week, lesson_number, 
                                subject_id, room_number, start_time, end_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (grade, class_name, day_of_week, lesson_number, 
              subject_id, room_number, start_time, end_time))
        
        schedule_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return schedule_id

    def get_all_grades(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT grades.id, students.name, subjects.name, grades.value, grades.date
            FROM grades
            JOIN students ON grades.student_id = students.id
            JOIN subjects ON grades.subject_id = subjects.id
        ''')
        grades = cursor.fetchall()
        conn.close()
        return grades

    def update_subject(self, subject_id, name, teacher):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE subjects
            SET name = ?, teacher = ?
            WHERE id = ?
        ''', (name, teacher, subject_id))
        conn.commit()
        conn.close()

    def delete_subject(self, subject_id):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM grades WHERE subject_id = ?', (subject_id,))
        cursor.execute('DELETE FROM subjects WHERE id = ?', (subject_id,))
        conn.commit()
        conn.close()

    def get_average_grades_by_subject(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT subjects.name, AVG(grades.value) as average
            FROM grades
            JOIN subjects ON grades.subject_id = subjects.id
            GROUP BY subjects.id, subjects.name
            ORDER BY average DESC
        ''')
        averages = cursor.fetchall()
        conn.close()
        return averages

    def check_student_login(self, login, password):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name FROM students
            WHERE login = ? AND password = ?
        ''', (login, password))
        result = cursor.fetchone()
        conn.close()
        return result

    def update_last_login(self, student_id):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        current_time = datetime.now().isoformat()
        cursor.execute('''
            UPDATE students
            SET last_login = ?
            WHERE id = ?
        ''', (current_time, student_id))
        conn.commit()
        conn.close()

    def get_students_with_last_login(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, 
                   CASE 
                       WHEN grade IS NOT NULL AND class_name IS NOT NULL 
                       THEN grade || class_name
                       ELSE COALESCE(grade || '', class_name, 'Не указан')
                   END as full_class,
                   last_login 
            FROM students 
            ORDER BY name
        ''')
        return cursor.fetchall()

    def get_student_schedule(self, student_id):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                s.grade,
                s.class_name
            FROM students s
            WHERE s.id = ?
        ''', (student_id,))
        student = cursor.fetchone()
        if student:
            grade, class_name = student
            return self.get_schedule_for_class(grade, class_name)
        conn.close()
        return []

    def get_class_average_grades(self, grade, class_name):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                subjects.name as subject_name,
                ROUND(AVG(CAST(grades.value AS FLOAT)), 2) as average_grade
            FROM (
                SELECT DISTINCT subject_id
                FROM schedule
                WHERE grade = ? AND class_name = ?
            ) class_subjects
            JOIN subjects ON subjects.id = class_subjects.subject_id
            LEFT JOIN grades ON subjects.id = grades.subject_id
            LEFT JOIN students ON grades.student_id = students.id 
                AND students.grade = ? AND students.class_name = ?
            GROUP BY subjects.id, subjects.name
            ORDER BY subjects.name
        ''', (grade, class_name, grade, class_name))
        results = cursor.fetchall()
        conn.close()
        return results

    def get_student_detailed_stats(self, student_id):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            WITH grade_counts AS (
                SELECT 
                    subject_id,
                    SUM(CASE WHEN value = 5 THEN 1 ELSE 0 END) as count_5,
                    SUM(CASE WHEN value = 4 THEN 1 ELSE 0 END) as count_4,
                    SUM(CASE WHEN value = 3 THEN 1 ELSE 0 END) as count_3,
                    SUM(CASE WHEN value = 2 THEN 1 ELSE 0 END) as count_2
                FROM grades
                WHERE student_id = ?
                GROUP BY subject_id
            )
            SELECT 
                subjects.name as subject_name,
                ROUND(AVG(CAST(grades.value AS FLOAT)), 2) as average_grade,
                COALESCE(gc.count_5, 0) as count_5,
                COALESCE(gc.count_4, 0) as count_4,
                COALESCE(gc.count_3, 0) as count_3,
                COALESCE(gc.count_2, 0) as count_2,
                COUNT(DISTINCT grades.id) as total_grades
            FROM (
                SELECT DISTINCT subject_id
                FROM schedule
                JOIN students ON students.grade = schedule.grade 
                    AND students.class_name = schedule.class_name
                WHERE students.id = ?
            ) student_subjects
            JOIN subjects ON subjects.id = student_subjects.subject_id
            LEFT JOIN grades ON subjects.id = grades.subject_id AND grades.student_id = ?
            LEFT JOIN grade_counts gc ON subjects.id = gc.subject_id
            GROUP BY subjects.id, subjects.name
            ORDER BY subjects.name
        ''', (student_id, student_id, student_id))
        results = cursor.fetchall()
        conn.close()
        return results

    def get_schedule_for_class_by_week(self, grade, class_name, week_start_date):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                schedule.day_of_week,
                schedule.lesson_number,
                subjects.name,
                schedule.room_number,
                schedule.start_time,
                schedule.end_time,
                schedule.id,
                subjects.id
            FROM schedule
            JOIN subjects ON schedule.subject_id = subjects.id
            WHERE schedule.grade = ? AND schedule.class_name = ?
            ORDER BY schedule.day_of_week, schedule.lesson_number
        ''', (grade, class_name))
        schedule = cursor.fetchall()
        conn.close()
        return schedule

    def get_student_grades_by_week(self, student_id, week_start_date):
        week_end_date = week_start_date + timedelta(days=6)
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                subjects.name as subject_name,
                grades.value,
                strftime('%w', grades.date) as weekday,
                subjects.id as subject_id
            FROM grades
            JOIN subjects ON grades.subject_id = subjects.id
            WHERE grades.student_id = ? 
            AND date(grades.date) BETWEEN date(?) AND date(?)
        ''', (student_id, week_start_date.isoformat(), week_end_date.isoformat()))
        grades = cursor.fetchall()
        conn.close()
        return [{'subject_name': g[0], 'value': g[1], 'weekday': int(g[2]), 'subject_id': g[3]} for g in grades]

    def get_student_schedule_by_week(self, student_id, week_start_date):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                schedule.day_of_week as weekday,
                schedule.lesson_number,
                subjects.name as subject_name,
                schedule.room_number,
                schedule.start_time,
                schedule.end_time,
                subjects.id as subject_id
            FROM students
            JOIN schedule ON students.grade = schedule.grade 
                AND students.class_name = schedule.class_name
            JOIN subjects ON schedule.subject_id = subjects.id
            WHERE students.id = ?
            ORDER BY schedule.day_of_week, schedule.lesson_number
        ''', (student_id,))
        schedule = cursor.fetchall()
        conn.close()
        return [{
            'weekday': row[0],
            'lesson_number': row[1],
            'subject_name': row[2],
            'room': row[3],
            'start_time': row[4],
            'end_time': row[5],
            'subject_id': row[6]
        } for row in schedule]
