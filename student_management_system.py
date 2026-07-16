"""
╔══════════════════════════════════════════════════════════════════╗
║         STUDENT MANAGEMENT SYSTEM — Advanced DBMS Project        ║
║         Demonstrates: DDL, DML, TCL, DCL, JOINs (SQL)            ║
║         Stack: Python 3 · Tkinter · MySQL                        ║
╚══════════════════════════════════════════════════════════════════╝

SETUP INSTRUCTIONS
──────────────────
1. Install dependencies:
       pip install mysql-connector-python

2. Configure MySQL credentials in the DB_CONFIG dict below.

3. Run:
       python student_management_system.py

   The program auto-creates the database & tables on first launch.
"""

from struct import pack
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import mysql.connector
from mysql.connector import Error
import csv
import datetime

# ─────────────────────────── CONFIGURATION ───────────────────────────
DB_CONFIG = {
    "host":     "localhost",
    "user":     "root",        # ← change if needed
    "password": "simi@7800",  # ← change to your MySQL password
    "port":     3306,
}
DATABASE_NAME = "stu_mgmt_db"

# ──────────────────────────── COLOR PALETTE ──────────────────────────
C = {
    "bg":          "#0F1117",
    "panel":       "#1A1D27",
    "card":        "#22263A",
    "border":      "#2E3350",
    "accent":      "#6C63FF",
    "accent2":     "#00D4AA",
    "accent3":     "#FF6B6B",
    "accent4":     "#FFD166",
    "text":        "#E8EAFF",
    "text_muted":  "#7B80A8",
    "green":       "#2ECC71",
    "red":         "#E74C3C",
    "orange":      "#F39C12",
    "blue":        "#3498DB",
    "purple":      "#9B59B6",
    "teal":        "#1ABC9C",
    "white":       "#FFFFFF",
    "tree_bg":     "#161924",
    "tree_sel":    "#3D4270",
    "tree_alt":    "#1E2235",
}

FONT_TITLE = ("Consolas", 22, "bold")
FONT_HEAD  = ("Consolas", 13, "bold")
FONT_LABEL = ("Consolas", 10)
FONT_ENTRY = ("Consolas", 10)
FONT_BTN   = ("Consolas", 10, "bold")
FONT_SMALL = ("Consolas", 9)
FONT_MONO  = ("Courier New", 9)


# ═════════════════════════════════════════════════════════════════════
#  DATABASE LAYER
# ═════════════════════════════════════════════════════════════════════

class Database:
    def __init__(self):
        self.conn   = None
        self.cursor = None

    # ── connect ──────────────────────────────────────────────────────
    def connect(self):
        try:
            self.conn = mysql.connector.connect(**DB_CONFIG)
            self.cursor = self.conn.cursor(dictionary=True)
            self._bootstrap()
            return True
        except Error as e:
            messagebox.showerror(
                "DB Connection Error",
                f"Cannot connect to MySQL.\n\n{e}\n\n"
                "Please check DB_CONFIG at the top of this file.")
            return False

    # ── DDL: create database + tables ────────────────────────────────
    def _bootstrap(self):
        print("── DCL Example ──────────────────────────────────────────")
        print("-- GRANT SELECT, INSERT, UPDATE, DELETE ON student_mgmt_db.*")
        print("--   TO 'app_user'@'localhost' IDENTIFIED BY 'password';")
        print()

        self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DATABASE_NAME}`")
        self.cursor.execute(f"USE `{DATABASE_NAME}`")
        self.conn.database = DATABASE_NAME

        ddl_statements = [
            """CREATE TABLE IF NOT EXISTS Students (
                student_id   INT          AUTO_INCREMENT PRIMARY KEY,
                name         VARCHAR(150) NOT NULL,
                age          INT          NOT NULL,
                gender       ENUM('Male','Female','Other') NOT NULL,
                course       VARCHAR(150) NOT NULL,
                created_at   TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS Subjects (
                subject_id   INT          AUTO_INCREMENT PRIMARY KEY,
                subject_name VARCHAR(150) NOT NULL UNIQUE
            )""",
            """CREATE TABLE IF NOT EXISTS Marks (
                marks_id   INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT NOT NULL,
                subject_id INT NOT NULL,
                marks      DECIMAL(5,2) NOT NULL,
                CONSTRAINT fk_student FOREIGN KEY (student_id)
                    REFERENCES Students(student_id) ON DELETE CASCADE,
                CONSTRAINT fk_subject FOREIGN KEY (subject_id)
                    REFERENCES Subjects(subject_id) ON DELETE CASCADE,
                UNIQUE KEY uq_student_subject (student_id, subject_id)
            )""",
        ]

        print("── DDL Statements ───────────────────────────────────────")
        for stmt in ddl_statements:
            print(stmt.strip()[:80] + "...")
            self.cursor.execute(stmt)
        self.conn.commit()
        print("Tables created / verified.\n")

    # ── helpers ──────────────────────────────────────────────────────
    def _exec(self, sql, params=None, fetch=False):
        print(f"SQL ▶  {sql.strip()}")
        if params:
            print(f"     PARAMS: {params}")
        self.cursor.execute(sql, params or ())
        if fetch:
            rows = self.cursor.fetchall()
            print(f"     → {len(rows)} row(s) returned\n")
            return rows
        print()
        return None

    def reset_database(self):
        try:
            self.cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            self.cursor.execute("TRUNCATE TABLE Marks")
            self.cursor.execute("TRUNCATE TABLE Students")
            self.cursor.execute("TRUNCATE TABLE Subjects")
            self.cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            self.conn.commit()
            print("TCL ▶  COMMIT (Database Reset)\n")
        except Error as e:
            self.conn.rollback()
            print("TCL ▶  ROLLBACK\n")
            raise e

    # ════ STUDENTS ════════════════════════════════════════════════════

    def add_student(self, name, age, gender, course):
        sql = "INSERT INTO Students (name, age, gender, course) VALUES (%s,%s,%s,%s)"
        self._exec(sql, (name, age, gender, course))
        self.conn.commit()
        print("TCL ▶  COMMIT\n")

    def get_students(self, search=None):
        if search:
            sql = "SELECT * FROM Students WHERE name LIKE %s ORDER BY student_id"
            return self._exec(sql, (f"%{search}%",), fetch=True)
        return self._exec("SELECT * FROM Students ORDER BY student_id", fetch=True)

    def update_student(self, sid, name, age, gender, course):
        sql = ("UPDATE Students SET name=%s, age=%s, gender=%s, course=%s "
               "WHERE student_id=%s")
        self._exec(sql, (name, age, gender, course, sid))
        self.conn.commit()
        print("TCL ▶  COMMIT\n")

    def delete_student(self, sid):
        try:
            self._exec("DELETE FROM Students WHERE student_id=%s", (sid,))
            self.conn.commit()
            print("TCL ▶  COMMIT\n")
        except Error as e:
            self.conn.rollback()
            print("TCL ▶  ROLLBACK\n")
            raise e

    def get_student_by_id(self, sid):
        rows = self._exec("SELECT * FROM Students WHERE student_id=%s",
                          (sid,), fetch=True)
        return rows[0] if rows else None

    # ════ SUBJECTS ════════════════════════════════════════════════════

    def add_subject(self, name):
        self._exec("INSERT INTO Subjects (subject_name) VALUES (%s)", (name,))
        self.conn.commit()
        print("TCL ▶  COMMIT\n")

    def get_subjects(self):
        return self._exec("SELECT * FROM Subjects ORDER BY subject_id", fetch=True)

    def delete_subject(self, subject_id):
        try:
            self._exec("DELETE FROM Subjects WHERE subject_id=%s", (subject_id,))
            self.conn.commit()
            print("TCL ▶  COMMIT\n")
        except Error as e:
            self.conn.rollback()
            print("TCL ▶  ROLLBACK\n")
            raise e

    # ════ MARKS ═══════════════════════════════════════════════════════

    def add_marks(self, student_id, subject_id, marks):
        sql = ("INSERT INTO Marks (student_id, subject_id, marks) "
               "VALUES (%s,%s,%s) "
               "ON DUPLICATE KEY UPDATE marks=%s")
        self._exec(sql, (student_id, subject_id, marks, marks))
        self.conn.commit()
        print("TCL ▶  COMMIT\n")

    def get_marks_for_student(self, student_id):
        sql = """
SELECT m.marks_id, s.subject_name, m.marks, m.student_id, m.subject_id
FROM Marks m
JOIN Subjects s ON m.subject_id = s.subject_id
WHERE m.student_id = %s
ORDER BY s.subject_name"""
        return self._exec(sql, (student_id,), fetch=True)

    def get_all_marks(self):
        sql = """
SELECT m.marks_id, st.student_id, st.name AS student_name,
       s.subject_id, s.subject_name, m.marks
FROM Marks m
JOIN Students st ON m.student_id = st.student_id
JOIN Subjects s  ON m.subject_id  = s.subject_id
ORDER BY st.student_id, s.subject_name"""
        return self._exec(sql, fetch=True)

    def update_marks(self, marks_id, new_marks):
        sql = "UPDATE Marks SET marks=%s WHERE marks_id=%s"
        self._exec(sql, (new_marks, marks_id))
        self.conn.commit()
        print("TCL ▶  COMMIT\n")

    def delete_marks(self, marks_id):
        try:
            self._exec("DELETE FROM Marks WHERE marks_id=%s", (marks_id,))
            self.conn.commit()
            print("TCL ▶  COMMIT\n")
        except Error as e:
            self.conn.rollback()
            print("TCL ▶  ROLLBACK\n")
            raise e

    def delete_all_marks(self):
     cursor = self.conn.cursor()
     cursor.execute("DELETE FROM Marks")
     self.conn.commit()
    
    # ════ JOINs ═══════════════════════════════════════════════════════

    def inner_join(self):
        sql = """
SELECT s.student_id, s.name, s.course,
       sub.subject_name, m.marks
FROM   Students s
INNER JOIN Marks    m   ON s.student_id = m.student_id
INNER JOIN Subjects sub ON m.subject_id  = sub.subject_id
ORDER BY s.student_id, sub.subject_name"""
        print("── INNER JOIN ───────────────────────────────────────────")
        return self._exec(sql, fetch=True)

    def left_join(self):
        sql = """
SELECT s.student_id, s.name, s.course,
       COALESCE(sub.subject_name, '—') AS subject_name,
       COALESCE(CAST(m.marks AS CHAR), 'N/A') AS marks
FROM   Students s
LEFT JOIN Marks    m   ON s.student_id = m.student_id
LEFT JOIN Subjects sub ON m.subject_id  = sub.subject_id
ORDER BY s.student_id"""
        print("── LEFT JOIN ────────────────────────────────────────────")
        return self._exec(sql, fetch=True)

    def right_join(self):
        sql = """
SELECT COALESCE(s.name, 'No Student')  AS student_name,
       COALESCE(s.course, '—')         AS course,
       sub.subject_id, sub.subject_name,
       COALESCE(CAST(m.marks AS CHAR), 'N/A') AS marks
FROM   Subjects sub
LEFT JOIN Marks    m ON sub.subject_id  = m.subject_id
LEFT JOIN Students s ON m.student_id   = s.student_id
ORDER BY sub.subject_id"""
        print("── RIGHT JOIN (simulated via LEFT JOIN swap) ─────────────")
        return self._exec(sql, fetch=True)

    def student_summary(self):
        sql = """
SELECT s.student_id, s.name, s.course,
       COUNT(m.marks)                     AS subjects_taken,
       COALESCE(SUM(m.marks), 0)          AS total_marks,
       COALESCE(ROUND(AVG(m.marks), 2), 0) AS percentage
FROM   Students s
LEFT JOIN Marks m ON s.student_id = m.student_id
GROUP BY s.student_id, s.name, s.course
ORDER BY s.student_id"""
        return self._exec(sql, fetch=True)

    # ── close ─────────────────────────────────────────────────────────
    def close(self):
        if self.conn and self.conn.is_connected():
            self.cursor.close()
            self.conn.close()


# ═════════════════════════════════════════════════════════════════════
#  REUSABLE UI WIDGETS
# ═════════════════════════════════════════════════════════════════════

def styled_button(parent, text, command, color=C["accent"],
                  width=18, pady=6):
    btn = tk.Button(
        parent, text=text, command=command,
        bg=color, fg=C["white"],
        font=FONT_BTN, relief="flat",
        activebackground=color, activeforeground=C["white"],
        bd=0, padx=8, pady=pady, width=width, cursor="hand2",
    )
    btn.bind("<Enter>", lambda e: btn.config(bg=_lighten(color)))
    btn.bind("<Leave>", lambda e: btn.config(bg=color))
    return btn


def _lighten(hex_color, amount=30):
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return f"#{min(255,r+amount):02X}{min(255,g+amount):02X}{min(255,b+amount):02X}"


def labelled_entry(parent, label, row, options=None, width=22):
    tk.Label(parent, text=label, bg=C["card"], fg=C["text_muted"],
             font=FONT_LABEL, anchor="w").grid(
        row=row, column=0, sticky="w", padx=(8, 4), pady=4)
    if options:
        var = tk.StringVar(value=options[0])
        om  = tk.OptionMenu(parent, var, *options)
        om.config(bg=C["border"], fg=C["text"], font=FONT_ENTRY,
                  relief="flat", bd=0, highlightthickness=0,
                  activebackground=C["accent"], activeforeground=C["white"])
        om["menu"].config(bg=C["border"], fg=C["text"], font=FONT_ENTRY)
        om.grid(row=row, column=1, sticky="ew", padx=(0, 8), pady=4)
        return var
    else:
        var = tk.StringVar()
        ent = tk.Entry(parent, textvariable=var, font=FONT_ENTRY,
                       bg=C["border"], fg=C["text"],
                       insertbackground=C["accent"],
                       relief="flat", bd=4, width=width)
        ent.grid(row=row, column=1, sticky="ew", padx=(0, 8), pady=4)
        return var


def build_treeview(parent, columns, heights=14):
    style = ttk.Style()
    style.theme_use("default")
    style.configure("Custom.Treeview",
                    background=C["tree_bg"], fieldbackground=C["tree_bg"],
                    foreground=C["text"], font=FONT_SMALL,
                    rowheight=22, borderwidth=0)
    style.configure("Custom.Treeview.Heading",
                    background=C["accent"], foreground=C["white"],
                    font=FONT_LABEL, relief="flat")
    style.map("Custom.Treeview",
              background=[("selected", C["tree_sel"])],
              foreground=[("selected", C["white"])])

    frame = tk.Frame(parent, bg=C["tree_bg"])
    frame.pack(fill="both", expand=True, padx=4, pady=4)

    vsb = ttk.Scrollbar(frame, orient="vertical")
    hsb = ttk.Scrollbar(frame, orient="horizontal")

    tree = ttk.Treeview(frame, columns=columns, show="headings",
                        height=heights,
                        yscrollcommand=vsb.set, xscrollcommand=hsb.set,
                        style="Custom.Treeview")
    vsb.config(command=tree.yview)
    hsb.config(command=tree.xview)

    for col in columns:
        tree.heading(col, text=col.replace("_", " ").title())
        tree.column(col, width=110, anchor="center", minwidth=60)

    vsb.pack(side="right", fill="y")
    hsb.pack(side="bottom", fill="x")
    tree.pack(fill="both", expand=True)

    tree.tag_configure("odd",  background=C["tree_bg"])
    tree.tag_configure("even", background=C["tree_alt"])
    return tree


def populate_tree(tree, rows):
    tree.delete(*tree.get_children())
    for i, row in enumerate(rows):
        tag = "even" if i % 2 == 0 else "odd"
        tree.insert("", "end", values=list(row.values()), tags=(tag,))


# ═════════════════════════════════════════════════════════════════════
#  MAIN APPLICATION
# ═════════════════════════════════════════════════════════════════════

class StudentManagementApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Student Management System  ·  DBMS Project")
        self.configure(bg=C["bg"])
        self.geometry("1280x820")
        self.resizable(True, True)
        self.minsize(1000, 700)

        self.db = Database()
        if not self.db.connect():
            self.destroy()
            return

        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── helpers ──────────────────────────────────────────────────────
    def _sep(self, parent, color=C["border"]):
        tk.Frame(parent, bg=color, height=1).pack(fill="x", padx=6, pady=8)

    def _card(self, parent, title="", color=C["accent"]):
        outer = tk.Frame(parent, bg=C["card"], bd=0, relief="flat")
        outer.pack(fill="x", padx=8, pady=(0, 6))
        if title:
            tk.Label(outer, text=title, bg=color, fg=C["white"],
                     font=FONT_HEAD, anchor="w", padx=8, pady=4
                     ).pack(fill="x")
        inner = tk.Frame(outer, bg=C["card"])
        inner.pack(fill="x", padx=6, pady=6)
        return inner

    # ── Export Logic ─────────────────────────────────────────────────
    def _export_treeview_to_csv(self, tree, filename_prefix):
        """Generic function to export any Treeview data to a CSV file."""
        data = []
        cols = tree["columns"]
        data.append(cols)  # Header row

        for child in tree.get_children():
            data.append(tree.item(child)["values"])

        if not data or len(data) <= 1:
            messagebox.showwarning("Export", "No data available to export!")
            return

        fpath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"{filename_prefix}.csv"
        )

        if fpath:
            try:
                with open(fpath, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerows(data)
                messagebox.showinfo("Success", f"Data exported successfully to:\n{fpath}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Could not save file: {e}")

    # ── top-level layout ─────────────────────────────────────────────
    def _build_ui(self):
        # Header
        header = tk.Frame(self, bg=C["accent"], height=56)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="⬡  STUDENT MANAGEMENT SYSTEM",
                 bg=C["accent"], fg=C["white"],
                 font=FONT_TITLE).pack(side="left", padx=20, pady=10)
        tk.Label(header, text="DBMS · SQL · JOINs · Python + MySQL",
                 bg=C["accent"], fg="#C8C4FF",
                 font=FONT_SMALL).pack(side="right", padx=20)

        # Notebook
        nb_style = ttk.Style()
        nb_style.theme_use("default")
        nb_style.configure("TNotebook", background=C["bg"],
                            borderwidth=0, tabmargins=[2, 5, 2, 0])
        nb_style.configure("TNotebook.Tab",
                            background=C["panel"], foreground=C["text_muted"],
                            font=FONT_BTN, padding=[16, 8])
        nb_style.map("TNotebook.Tab",
                     background=[("selected", C["card"])],
                     foreground=[("selected", C["accent"])])

        self.nb = ttk.Notebook(self, style="TNotebook")
        self.nb.pack(fill="both", expand=True, padx=8, pady=(4, 8))

        self._tab_students()
        self._tab_subjects_marks()
        self._tab_joins()
        self._tab_summary()
        self._tab_reports()
        self._tab_sql_log()

    # ── reset ─────────────────────────────────────────────────────────
    def _reset_db(self):
        confirm = messagebox.askyesno(
            "Warning", "पूरी database delete हो जाएगी!\nContinue?")
        if confirm:
            try:
                self.db.reset_database()
                messagebox.showinfo("Success", "Database Reset Successfully!")
                self._view_students()
                self._refresh_subjects_tree()
                self._refresh_marks_tree()
            except Exception as e:
                messagebox.showerror("Error", str(e))

   # ══════════════════════════════════════════════════════════════════
    #  TAB 1 — STUDENTS
    # ══════════════════════════════════════════════════════════════════
    def _tab_students(self):
        tab = tk.Frame(self.nb, bg=C["bg"])
        self.nb.add(tab, text=" 👤  Students ")

        # ── left panel: form ─────────────────────────────────────────
        left = tk.Frame(tab, bg=C["panel"], width=300)
        left.pack(side="left", fill="y", padx=(8, 4), pady=8)
        left.pack_propagate(False)

        tk.Label(left, text="STUDENT FORM", bg=C["panel"],
                 fg=C["accent"], font=FONT_HEAD).pack(pady=(12, 4))
        self._sep(left)

        form = tk.Frame(left, bg=C["card"])
        form.pack(fill="x", padx=8, pady=4)
        form.columnconfigure(1, weight=1)

        self.s_id_var     = labelled_entry(form, "ID (for update/delete)", 0)
        self.s_name_var   = labelled_entry(form, "Full Name *", 1)
        self.s_age_var    = labelled_entry(form, "Age *", 2)
        self.s_gender_var = labelled_entry(form, "Gender *", 3,
                                           options=["Male", "Female", "Other"])
        self.s_course_var = labelled_entry(form, "Course *", 4)

        self._sep(left)

        btn_frame = tk.Frame(left, bg=C["panel"])
        btn_frame.pack(fill="x", padx=8)

        styled_button(btn_frame, "➕  Add Student",
                      self._add_student, C["accent"]).pack(fill="x", pady=2)
        styled_button(btn_frame, "✏️  Update Student",
                      self._update_student, C["blue"]).pack(fill="x", pady=2)
        styled_button(btn_frame, "🗑️  Delete Student",
                      self._delete_student, C["red"]).pack(fill="x", pady=2)
        styled_button(btn_frame, "🔄  Clear Fields",
                      self._clear_student_form, C["text_muted"]).pack(fill="x", pady=2)
        self._sep(left)
        styled_button(btn_frame, "⚠️  Reset Database",
                      self._reset_db, C["orange"]).pack(fill="x", pady=2)

        # ── right panel: table ───────────────────────────────────────
        right = tk.Frame(tab, bg=C["bg"])
        right.pack(side="right", fill="both", expand=True, padx=(4, 8), pady=8)

        # search bar
        search_bar = tk.Frame(right, bg=C["panel"])
        search_bar.pack(fill="x", pady=(0, 4))
        tk.Label(search_bar, text="🔍 Search:", bg=C["panel"],
                 fg=C["text_muted"], font=FONT_LABEL).pack(side="left", padx=8)
        self.search_var = tk.StringVar()
        tk.Entry(search_bar, textvariable=self.search_var, font=FONT_ENTRY,
                 bg=C["border"], fg=C["text"], insertbackground=C["accent"],
                 relief="flat", bd=4, width=25).pack(side="left", padx=4)
        styled_button(search_bar, "Search", self._search_students,
                      C["accent2"], width=10, pady=4).pack(side="left", padx=4)
        styled_button(search_bar, "Show All", self._view_students,
                      C["text_muted"], width=10, pady=4).pack(side="left", padx=4)
        styled_button(search_bar, "Export CSV", 
                      lambda: self._export_treeview_to_csv(self.student_tree, "Students"),
                      C["teal"], width=12, pady=4).pack(side="right", padx=8)

        cols = ("student_id", "name", "age", "gender", "course", "created_at")
        self.student_tree = build_treeview(right, cols)
        self.student_tree.bind("<ButtonRelease-1>", self._on_student_select)

        self._view_students()

    # ── student actions ───────────────────────────────────────────────
    def _add_student(self):
        name   = self.s_name_var.get().strip()
        age    = self.s_age_var.get().strip()
        gender = self.s_gender_var.get().strip()
        course = self.s_course_var.get().strip()
        if not name or not age or not gender or not course:
            messagebox.showwarning("Input Error", "All fields marked * are required!")
            return
        try:
            self.db.add_student(name, int(age), gender, course)
            messagebox.showinfo("Success", f"Student '{name}' added successfully!")
            self._view_students()
            self._clear_student_form()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _update_student(self):
        sid = self.s_id_var.get().strip()
        if not sid:
            messagebox.showwarning("Input Error", "Enter Student ID to update!")
            return
        name   = self.s_name_var.get().strip()
        age    = self.s_age_var.get().strip()
        gender = self.s_gender_var.get().strip()
        course = self.s_course_var.get().strip()
        if not name or not age or not gender or not course:
            messagebox.showwarning("Input Error", "All fields marked * are required!")
            return
        try:
            self.db.update_student(int(sid), name, int(age), gender, course)
            messagebox.showinfo("Success", f"Student ID {sid} updated!")
            self._view_students()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _delete_student(self):
        sid = self.s_id_var.get().strip()
        if not sid:
            messagebox.showwarning("Input Error", "Enter Student ID to delete!")
            return
        if messagebox.askyesno("Confirm Delete", f"Delete student ID {sid}?"):
            try:
                self.db.delete_student(int(sid))
                messagebox.showinfo("Success", "Student deleted!")
                self._view_students()
                self._clear_student_form()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _view_students(self):
        rows = self.db.get_students()
        populate_tree(self.student_tree, rows)

    def _search_students(self):
        q = self.search_var.get().strip()
        rows = self.db.get_students(search=q if q else None)
        populate_tree(self.student_tree, rows)

    def _on_student_select(self, event):
        sel = self.student_tree.focus()
        if not sel:
            return
        vals = self.student_tree.item(sel, "values")
        if vals:
            self.s_id_var.set(vals[0])
            self.s_name_var.set(vals[1])
            self.s_age_var.set(vals[2])
            self.s_gender_var.set(vals[3])
            self.s_course_var.set(vals[4])

    def _clear_student_form(self):
        for v in (self.s_id_var, self.s_name_var,
                  self.s_age_var, self.s_course_var):
            v.set("")
        self.s_gender_var.set("Male")

    # ══════════════════════════════════════════════════════════════════
    #  TAB 2 — SUBJECTS & MARKS
    # ══════════════════════════════════════════════════════════════════
    def _tab_subjects_marks(self):
        tab = tk.Frame(self.nb, bg=C["bg"])
        self.nb.add(tab, text=" 📚  Subjects & Marks ")

        # ── top half: split into subjects (left) and marks form (right) ──
        top = tk.Frame(tab, bg=C["bg"])
        top.pack(fill="both", expand=True)

        # ── SUBJECTS PANEL ───────────────────────────────────────────
        subj_panel = tk.Frame(top, bg=C["panel"], width=340)
        subj_panel.pack(side="left", fill="both", padx=(8, 4), pady=8)
        subj_panel.pack_propagate(False)

        tk.Label(subj_panel, text="SUBJECTS", bg=C["accent2"],
                 fg=C["bg"], font=FONT_HEAD, anchor="w",
                 padx=8, pady=4).pack(fill="x")

        # add subject
        add_frame = tk.Frame(subj_panel, bg=C["card"])
        add_frame.pack(fill="x", padx=8, pady=8)
        add_frame.columnconfigure(1, weight=1)
        self.subj_name_var = labelled_entry(add_frame, "Subject Name *", 0)

        btn_row = tk.Frame(subj_panel, bg=C["panel"])
        btn_row.pack(fill="x", padx=8, pady=(0, 4))
        styled_button(btn_row, "➕ Add Subject",
                      self._add_subject, C["accent2"], width=16
                      ).pack(side="left", padx=(0, 4))
        styled_button(btn_row, "🗑️ Delete",
                      self._delete_subject, C["red"], width=10
                      ).pack(side="left")

        self._sep(subj_panel, C["border"])

        cols_s = ("subject_id", "subject_name")
        self.subject_tree = build_treeview(subj_panel, cols_s, heights=10)
        self.subject_tree.bind("<ButtonRelease-1>", self._on_subject_select)
        self._refresh_subjects_tree()

        # ── MARKS PANEL ──────────────────────────────────────────────
        marks_panel = tk.Frame(top, bg=C["panel"])
        marks_panel.pack(side="right", fill="both", expand=True,
                         padx=(4, 8), pady=8)

        tk.Label(marks_panel, text="ASSIGN / UPDATE MARKS",
                 bg=C["accent4"], fg=C["bg"], font=FONT_HEAD,
                 anchor="w", padx=8, pady=4).pack(fill="x")

        form_frame = tk.Frame(marks_panel, bg=C["card"])
        form_frame.pack(fill="x", padx=8, pady=8)
        form_frame.columnconfigure(1, weight=1)

        self.m_student_id_var = labelled_entry(form_frame, "Student ID *", 0)
        self.m_subject_id_var = labelled_entry(form_frame, "Subject ID *", 1)
        self.m_marks_var      = labelled_entry(form_frame, "Marks (0–100) *", 2)

        hint = ("💡 Tip: Click a student row in Tab 1, a subject row here,\n"
                "       then enter marks and click Save Marks.")
        tk.Label(form_frame, text=hint, bg=C["card"], fg=C["text_muted"],
                 font=FONT_SMALL, justify="left").grid(
            row=3, column=0, columnspan=2, sticky="w", padx=8, pady=(4, 0))

        btn_row2 = tk.Frame(marks_panel, bg=C["panel"])
        btn_row2.pack(fill="x", padx=8, pady=(0, 4))

        styled_button(btn_row2, "💾 Save Marks",
                      self._save_marks, C["accent4"], width=16
                      ).pack(side="left", padx=(0, 4))
        styled_button(btn_row2, "✏️ Update Marks",
                      self._update_marks_selected, C["blue"], width=16
                      ).pack(side="left", padx=(0, 4))
        styled_button(btn_row2, "🗑️ Delete Mark",
                      self._delete_marks_selected, C["red"], width=14
                      ).pack(side="left")
        styled_button(btn_row2, "Clear Form", self._clear_marks_form, C["text_muted"], width=12).pack(side="right")

        styled_button(btn_row2, "🗑️ Delete All",
                      self._delete_all_marks, C["blue"], width=14
                      ).pack(side="left")
       

        self._sep(marks_panel, C["border"])
        self._sep(marks_panel, C["border"])

        # view-marks sub-controls
        vm_bar = tk.Frame(marks_panel, bg=C["panel"])
        vm_bar.pack(fill="x", padx=8, pady=(0, 4))
        tk.Label(vm_bar, text="Filter by Student ID:",
                 bg=C["panel"], fg=C["text_muted"],
                 font=FONT_LABEL).pack(side="left")
        self.view_marks_id = tk.StringVar()
        tk.Entry(vm_bar, textvariable=self.view_marks_id,
                 font=FONT_ENTRY, bg=C["border"], fg=C["text"],
                 insertbackground=C["accent"],
                 relief="flat", bd=4, width=10).pack(side="left", padx=6)
        styled_button(vm_bar, "View Marks",
                      self._view_marks_for_student,
                      C["purple"], width=12, pady=4
                      ).pack(side="left", padx=4)
        styled_button(vm_bar, "All Marks",
                      self._refresh_marks_tree,
                      C["text_muted"], width=10, pady=4
                      ).pack(side="left", padx=4)
        styled_button(vm_bar, "Export CSV",
                      lambda: self._export_treeview_to_csv(self.marks_tree, "Marks"),
                      C["teal"], width=12, pady=4
                      ).pack(side="right", padx=8)

        cols_m = ("marks_id", "student_id", "student_name",
                  "subject_id", "subject_name", "marks")
        self.marks_tree = build_treeview(marks_panel, cols_m, heights=10)
        self.marks_tree.bind("<ButtonRelease-1>", self._on_marks_select)
        self._refresh_marks_tree()

    # ── subject actions ───────────────────────────────────────────────
    def _add_subject(self):
        name = self.subj_name_var.get().strip()
        if not name:
            messagebox.showwarning("Input Error", "Enter a subject name!")
            return
        try:
            self.db.add_subject(name)
            messagebox.showinfo("Success", f"Subject '{name}' added!")
            self.subj_name_var.set("")
            self._refresh_subjects_tree()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _delete_subject(self):
        sel = self.subject_tree.focus()
        if not sel:
            messagebox.showwarning("Select", "Click a subject row to delete!")
            return
        vals = self.subject_tree.item(sel, "values")
        if not vals:
            return
        if messagebox.askyesno("Confirm",
                               f"Delete subject '{vals[1]}'?\n"
                               "All related marks will also be deleted!"):
            try:
                self.db.delete_subject(int(vals[0]))
                messagebox.showinfo("Success", "Subject deleted!")
                self._refresh_subjects_tree()
                self._refresh_marks_tree()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _on_subject_select(self, event):
        sel = self.subject_tree.focus()
        if not sel:
            return
        vals = self.subject_tree.item(sel, "values")
        if vals:
            self.m_subject_id_var.set(vals[0])

    def _refresh_subjects_tree(self):
        rows = self.db.get_subjects()
        populate_tree(self.subject_tree, rows)

    # ── marks actions ─────────────────────────────────────────────────
    def _save_marks(self):
        sid   = self.m_student_id_var.get().strip()
        subid = self.m_subject_id_var.get().strip()
        marks = self.m_marks_var.get().strip()
        if not sid or not subid or not marks:
            messagebox.showwarning("Input Error",
                                   "Student ID, Subject ID and Marks are required!")
            return
        try:
            m = float(marks)
            if not (0 <= m <= 100):
                messagebox.showwarning("Input Error", "Marks must be between 0 and 100!")
                return
            self.db.add_marks(int(sid), int(subid), m)
            messagebox.showinfo("Success",
                                f"Marks saved — Student {sid}, Subject {subid}: {m}")
            self._refresh_marks_tree()
            self._clear_marks_form()
        except ValueError:
            messagebox.showerror("Error", "Marks must be a valid number!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _update_marks_selected(self):
        """Update marks for the currently selected row in the marks tree."""
        sel = self.marks_tree.focus()
        if not sel:
            messagebox.showwarning("Select", "Click a marks row to update!")
            return
        vals = self.marks_tree.item(sel, "values")
        if not vals:
            return
        marks_id = vals[0]
        new_marks = self.m_marks_var.get().strip()
        if not new_marks:
            messagebox.showwarning("Input Error",
                                   "Enter new marks in the Marks field!")
            return
        try:
            m = float(new_marks)
            if not (0 <= m <= 100):
                messagebox.showwarning("Input Error",
                                       "Marks must be between 0 and 100!")
                return
            self.db.update_marks(int(marks_id), m)
            messagebox.showinfo("Success",
                                f"Marks updated to {m} (ID: {marks_id})")
            self._refresh_marks_tree()
            self._clear_marks_form()
        except ValueError:
            messagebox.showerror("Error", "Marks must be a valid number!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _delete_marks_selected(self):
        sel = self.marks_tree.focus()
        if not sel:
            messagebox.showwarning("Select", "Click a marks row to delete!")
            return
        vals = self.marks_tree.item(sel, "values")
        if not vals:
            return
        marks_id = vals[0]
        if messagebox.askyesno("Confirm Delete",
                               f"Delete marks record ID {marks_id}?"):
            try:
                self.db.delete_marks(int(marks_id))
                messagebox.showinfo("Success", "Marks record deleted!")
                self._refresh_marks_tree()
                self._clear_marks_form()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _view_marks_for_student(self):
        sid = self.view_marks_id.get().strip()
        if not sid:
            messagebox.showwarning("Input Error", "Enter a Student ID to filter!")
            return
        try:
            rows = self.db.get_marks_for_student(int(sid))
            # Remap to match the 6-column tree
            display = []
            for r in rows:
                display.append({
                    "marks_id":     r["marks_id"],
                    "student_id":   r["student_id"],
                    "student_name": f"(Student {r['student_id']})",
                    "subject_id":   r["subject_id"],
                    "subject_name": r["subject_name"],
                    "marks":        r["marks"],
                })
            populate_tree(self.marks_tree, display)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _refresh_marks_tree(self):
        rows = self.db.get_all_marks()
        populate_tree(self.marks_tree, rows)

    def _on_marks_select(self, event):
        sel = self.marks_tree.focus()
        if not sel:
            return
        vals = self.marks_tree.item(sel, "values")
        if vals:
            # Fill marks form with selected row's data
            self.m_student_id_var.set(vals[1])   # student_id
            self.m_subject_id_var.set(vals[3])   # subject_id
            self.m_marks_var.set(vals[5])        # marks

    def _clear_marks_form(self):
        self.m_student_id_var.set("")
        self.m_subject_id_var.set("")
        self.m_marks_var.set("")

    def _delete_all_marks(self):
     confirm = messagebox.askyesno(
        "Confirm Delete",
        "Are you sure you want to delete ALL marks for ALL students?"
    )
     if confirm:
        try:
            self.db.delete_all_marks()  # Database class me ye method hona chahiye
            messagebox.showinfo("Success", "All marks have been deleted!")
            self._refresh_marks_tree()  # tree refresh
        except Exception as e:
            messagebox.showerror("Error", str(e))
# ══════════════════════════════════════════════════════════════════
    #  TAB 3 — JOIN RESULTS
    # ══════════════════════════════════════════════════════════════════
    def _tab_joins(self):
        tab = tk.Frame(self.nb, bg=C["bg"])
        self.nb.add(tab, text=" 🔗  JOIN Queries ")

        # control bar
        bar = tk.Frame(tab, bg=C["panel"], height=60)
        bar.pack(fill="x", padx=8, pady=(8, 0))
        bar.pack_propagate(False)

        tk.Label(bar, text="Run a JOIN query:",
                 bg=C["panel"], fg=C["text_muted"],
                 font=FONT_LABEL).pack(side="left", padx=12)

        styled_button(bar, "⬡ INNER JOIN",
                      self._run_inner_join, C["accent"], width=14, pady=6
                      ).pack(side="left", padx=4, pady=8)
        styled_button(bar, "⬡ LEFT JOIN",
                      self._run_left_join, C["accent2"], width=14, pady=6
                      ).pack(side="left", padx=4, pady=8)
        styled_button(bar, "⬡ RIGHT JOIN",
                      self._run_right_join, C["purple"], width=14, pady=6
                      ).pack(side="left", padx=4, pady=8)

        # label to show which JOIN is active
        self.join_label = tk.Label(tab, text="",
                                   bg=C["bg"], fg=C["accent4"],
                                   font=FONT_HEAD)
        self.join_label.pack(anchor="w", padx=12, pady=(4, 0))

        # dynamic treeview container
        self.join_frame = tk.Frame(tab, bg=C["bg"])
        self.join_frame.pack(fill="both", expand=True, padx=8, pady=4)

    def _run_inner_join(self):
        rows = self.db.inner_join()
        self._show_join_result("INNER JOIN  — Students ⟵⟶ Marks ⟵⟶ Subjects",
                               rows, C["accent"])

    def _run_left_join(self):
        rows = self.db.left_join()
        self._show_join_result("LEFT JOIN  — All Students (with or without marks)",
                               rows, C["accent2"])

    def _run_right_join(self):
        rows = self.db.right_join()
        self._show_join_result("RIGHT JOIN  — All Subjects (with or without students)",
                               rows, C["purple"])

    def _show_join_result(self, title, rows, color):
        self.join_label.config(text=title, fg=color)
        for w in self.join_frame.winfo_children():
            w.destroy()
        if not rows:
            tk.Label(self.join_frame, text="No data found.",
                     bg=C["bg"], fg=C["text_muted"],
                     font=FONT_HEAD).pack(pady=40)
            return
        cols = list(rows[0].keys())
        tree = build_treeview(self.join_frame, cols, heights=18)
        populate_tree(tree, rows)

        # ══════════════════════════════════════════════════════════════════
    #  TAB 4 — STUDENT SUMMARY
    # ══════════════════════════════════════════════════════════════════
    def _tab_summary(self):
        tab = tk.Frame(self.nb, bg=C["bg"])
        self.nb.add(tab, text=" 📊  Summary ")

        bar = tk.Frame(tab, bg=C["panel"], height=56)
        bar.pack(fill="x", padx=8, pady=(8, 0))
        bar.pack_propagate(False)

        tk.Label(bar, text="Aggregate per student (SUM, AVG, COUNT):",
                 bg=C["panel"], fg=C["text_muted"],
                 font=FONT_LABEL).pack(side="left", padx=12)
        styled_button(bar, "📊 Load Summary",
                      self._load_summary, C["teal"], width=16, pady=6
                      ).pack(side="left", padx=8, pady=8)
        styled_button(bar, "📄 Export CSV",
                      lambda: self._export_treeview_to_csv(self.summary_tree, "Student_Summary"),
                      C["accent2"], width=16, pady=6
                      ).pack(side="right", padx=12, pady=8)

        cols = ("student_id", "name", "course",
                "subjects_taken", "total_marks", "percentage")
        self.summary_tree = build_treeview(tab, cols, heights=20)

    def _load_summary(self):
        rows = self.db.student_summary()
        populate_tree(self.summary_tree, rows)

    # ══════════════════════════════════════════════════════════════════
    #  TAB 5 — STUDENT REPORTS
    # ══════════════════════════════════════════════════════════════════
    def _tab_reports(self):
        tab = tk.Frame(self.nb, bg=C["bg"])
        self.nb.add(tab, text=" 📜  Reports ")

        # Control Bar
        bar = tk.Frame(tab, bg=C["panel"], height=60)
        bar.pack(fill="x", padx=8, pady=(8, 0))
        bar.pack_propagate(False)

        tk.Label(bar, text="Enter Student ID for Report:",
                 bg=C["panel"], fg=C["text_muted"],
                 font=FONT_LABEL).pack(side="left", padx=12)
        
        self.report_sid_var = tk.StringVar()
        ent = tk.Entry(bar, textvariable=self.report_sid_var, font=FONT_ENTRY,
                       bg=C["border"], fg=C["text"], insertbackground=C["accent"],
                       relief="flat", bd=4, width=15)
        ent.pack(side="left", padx=4, pady=10)

        styled_button(bar, "📋 Generate Report",
                      self._generate_report, C["accent"], width=18, pady=6
                      ).pack(side="left", padx=8, pady=8)
        
        styled_button(bar, "💾 Save as Text",
                      self._save_report_txt, C["blue"], width=16, pady=6
                      ).pack(side="right", padx=12, pady=8)

        # Report Display Area
        self.report_frame = tk.Frame(tab, bg=C["card"], bd=1, relief="flat")
        self.report_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.report_text = tk.Text(self.report_frame, bg=C["tree_bg"], fg=C["text"],
                                   font=FONT_MONO, padx=20, pady=20, relief="flat",
                                   state="disabled")
        self.report_text.pack(fill="both", expand=True)

    def _generate_report(self):
        sid = self.report_sid_var.get().strip()
        if not sid:
            messagebox.showwarning("Input Error", "Please enter a Student ID!")
            return
        
        try:
            student = self.db.get_student_by_id(int(sid))
            if not student:
                messagebox.showerror("Error", f"No student found with ID {sid}")
                return
            
            marks = self.db.get_marks_for_student(int(sid))
            
            # Formatting the report text
            report = []
            report.append("═" * 60)
            report.append(f"{'STUDENT PERFORMANCE REPORT':^60}")
            report.append("═" * 60)
            report.append(f"Student ID : {student['student_id']}")
            report.append(f"Full Name  : {student['name']}")
            report.append(f"Course     : {student['course']}")
            report.append(f"Age        : {student['age']}")
            report.append(f"Gender     : {student['gender']}")
            report.append("-" * 60)
            report.append(f"{'SUBJECT':<30} | {'MARKS':>10}")
            report.append("-" * 60)
            
            total = 0
            count = 0
            for m in marks:
                report.append(f"{m['subject_name']:<30} | {m['marks']:>10.2f}")
                total += float(m['marks'])
                count += 1
            
            report.append("-" * 60)
            if count > 0:
                avg = total / count
                report.append(f"{'TOTAL MARKS':<30} | {total:>10.2f}")
                report.append(f"{'AVERAGE':<30} | {avg:>10.2f}%")
                status = "PASS" if avg >= 40 else "FAIL"
                report.append(f"{'RESULT STATUS':<30} | {status:>10}")
            else:
                report.append("No marks recorded for this student.")
            
            report.append("═" * 60)
            report.append(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            final_report = "\n".join(report)
            
            self.report_text.config(state="normal")
            self.report_text.delete("1.0", tk.END)
            self.report_text.insert(tk.END, final_report)
            self.report_text.config(state="disabled")
            
        except Exception as e:
            messagebox.showerror("Report Error", str(e))

    def _save_report_txt(self):
        content = self.report_text.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("Empty Report", "Generate a report first!")
            return
        
        sid = self.report_sid_var.get().strip()
        fpath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            initialfile=f"Student_Report_{sid}.txt"
        )
        
        if fpath:
            try:
                with open(fpath, "w", encoding="utf-8") as f:
                    f.write(content)
                messagebox.showinfo("Success", f"Report saved to:\n{fpath}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    # ══════════════════════════════════════════════════════════════════
    #  TAB 6 — SQL LOG
    # ══════════════════════════════════════════════════════════════════
    def _tab_sql_log(self):
        tab = tk.Frame(self.nb, bg=C["bg"])
        self.nb.add(tab, text=" 🖥️  SQL Log ")

        tk.Label(tab,
                 text="All SQL statements are printed to the terminal / console.\n"
                      "Monitor your terminal to see live DDL · DML · TCL output.",
                 bg=C["bg"], fg=C["text_muted"],
                 font=FONT_LABEL, justify="left"
                 ).pack(anchor="w", padx=16, pady=12)

        info = [
            ("DDL", "CREATE TABLE, ALTER TABLE, DROP TABLE",          C["accent"]),
            ("DML", "INSERT, UPDATE, DELETE, SELECT",                  C["accent2"]),
            ("TCL", "COMMIT after every write · ROLLBACK on error",    C["accent4"]),
            ("DCL", "GRANT / REVOKE printed as comment on startup",    C["purple"]),
            ("JOIN", "INNER · LEFT · RIGHT (simulated) in Tab 3",     C["teal"]),
        ]
        for tag, desc, col in info:
            row = tk.Frame(tab, bg=C["card"])
            row.pack(fill="x", padx=16, pady=3)
            tk.Label(row, text=f"  {tag:<6}", bg=col, fg=C["bg"],
                     font=FONT_BTN, width=8).pack(side="left")
            tk.Label(row, text=f"  {desc}", bg=C["card"], fg=C["text"],
                     font=FONT_LABEL).pack(side="left", padx=8)

    # ── close ─────────────────────────────────────────────────────────
    def _on_close(self):
        self.db.close()
        self.destroy()


# ═════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = StudentManagementApp()
    app.mainloop()