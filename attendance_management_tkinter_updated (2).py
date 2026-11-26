import tkinter as tk
from tkinter import ttk, messagebox
import pymysql
from datetime import date

# Same database settings as your original code
def connect():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="12345",
        database="attendance_db"
    )


BATCHES = {
    1: "BCA",
    2: "Civil",
    3: "IT",
    4: "AIML"
}


class AttendanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Attendance Management System")
        self.root.geometry("1250x760")
        self.root.minsize(1050, 650)
        self.root.configure(bg="#f2f5fa")

        self.dark = "#142b4a"
        self.dark2 = "#1d3b61"
        self.accent = "#2f6fed"
        self.bg = "#f2f5fa"
        self.white = "#ffffff"
        self.text = "#24344d"

        self.setup_style()
        self.build_sidebar()
        self.main = tk.Frame(self.root, bg=self.bg)
        self.main.pack(side="left", fill="both", expand=True)

        self.show_dashboard()

    def setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background="white",
            foreground=self.text,
            rowheight=32,
            fieldbackground="white",
            font=("Arial", 10)
        )
        style.configure(
            "Treeview.Heading",
            background="#e7edf6",
            foreground=self.dark,
            font=("Arial", 10, "bold"),
            padding=8
        )
        style.map("Treeview", background=[("selected", "#d7e6ff")])
        style.configure("TCombobox", padding=6)

    def build_sidebar(self):
        sidebar = tk.Frame(self.root, bg=self.dark, width=245)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(
            sidebar,
            text="ATTENDANCE\nMANAGEMENT",
            bg=self.dark,
            fg="white",
            font=("Arial", 18, "bold"),
            justify="left"
        ).pack(anchor="w", padx=22, pady=(28, 8))

        tk.Label(
            sidebar, text="STUDENT PORTAL",
            bg=self.dark, fg="#9fb6d2",
            font=("Arial", 9, "bold")
        ).pack(anchor="w", padx=23, pady=(0, 28))

        menu_items = [
            ("▦", "Dashboard", self.show_dashboard),
            ("＋", "Add Student", self.add_student),
            ("▤", "View Students", self.view_students),
            ("✓", "Mark Attendance", self.mark_attendance),
            ("▣", "Batch-wise Attendance", self.batch_attendance),
            ("▧", "Student Attendance Report", self.student_report),
            ("✎", "Update Student", self.update_student),
            ("↻", "Update Attendance", self.update_attendance),
            ("★", "Add Marks", self.add_marks),
        ]

        for symbol, label, command in menu_items:
            btn = tk.Button(
                sidebar,
                text=f"  {symbol}    {label}",
                command=command,
                bg=self.dark,
                fg="white",
                activebackground=self.dark2,
                activeforeground="white",
                relief="flat",
                bd=0,
                anchor="w",
                padx=18,
                pady=13,
                font=("Arial", 10),
                cursor="hand2"
            )
            btn.pack(fill="x", padx=9, pady=2)

        tk.Frame(sidebar, bg="#36516f", height=1).pack(fill="x", padx=18, pady=15)

        tk.Button(
            sidebar, text="  ⏻    Exit",
            command=self.root.destroy,
            bg=self.dark, fg="#ffdddd",
            activebackground="#8b3030",
            activeforeground="white",
            relief="flat", bd=0, anchor="w",
            padx=18, pady=13, font=("Arial", 10, "bold"),
            cursor="hand2"
        ).pack(fill="x", padx=9, pady=2, side="bottom")

    def clear_main(self):
        for widget in self.main.winfo_children():
            widget.destroy()

    def page_heading(self, title, subtitle="Attendance Management System"):
        self.clear_main()
        header = tk.Frame(self.main, bg=self.bg)
        header.pack(fill="x", padx=30, pady=(25, 18))
        tk.Label(
            header, text=title, bg=self.bg, fg=self.dark,
            font=("Arial", 22, "bold")
        ).pack(anchor="w")
        tk.Label(
            header, text=subtitle, bg=self.bg, fg="#718096",
            font=("Arial", 10)
        ).pack(anchor="w", pady=(5, 0))

    def card(self, parent, title, value):
        box = tk.Frame(parent, bg="white", padx=22, pady=20,
                       highlightbackground="#e1e7f0", highlightthickness=1)
        box.pack(side="left", fill="both", expand=True, padx=8)
        tk.Label(box, text=title, bg="white", fg="#718096",
                 font=("Arial", 10, "bold")).pack(anchor="w")
        tk.Label(box, text=str(value), bg="white", fg=self.dark,
                 font=("Arial", 26, "bold")).pack(anchor="w", pady=(10, 0))

    def get_batches(self):
        return list(BATCHES.items())

    def batch_selector(self, parent, variable=None, all_option=False):
        names = list(BATCHES.values())
        if all_option:
            names = ["All"] + names
        if variable is None:
            variable = tk.StringVar()
        combo = ttk.Combobox(
            parent, textvariable=variable, values=names,
            state="readonly", width=18
        )
        return combo, variable

    def make_table(self, parent, columns, headings=None):
        frame = tk.Frame(parent, bg="white")
        frame.pack(fill="both", expand=True, padx=30, pady=15)

        tree = ttk.Treeview(frame, columns=columns, show="headings")
        for i, col in enumerate(columns):
            heading = headings[i] if headings else col.replace("_", " ").title()
            tree.heading(col, text=heading)
            tree.column(col, width=135, minwidth=90, anchor="center")

        y_scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        x_scroll = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        return tree

    def run_query(self, query, values=(), fetch=None):
        con = connect()
        cur = con.cursor()
        cur.execute(query, values)
        result = cur.fetchall() if fetch == "all" else (
            cur.fetchone() if fetch == "one" else None
        )
        if fetch is None:
            con.commit()
        cur.close()
        con.close()
        return result

    def show_dashboard(self):
        self.page_heading("Dashboard", "Welcome to your Attendance Management System")
        total_students = self.run_query(
            "SELECT COUNT(*) FROM students", fetch="one"
        )[0]
        total_batches = len(BATCHES)
        present_today = self.run_query(
            "SELECT COUNT(*) FROM attendance WHERE attendance_date=%s AND status='Present'",
            (date.today(),), "one"
        )[0]

        cards = tk.Frame(self.main, bg=self.bg)
        cards.pack(fill="x", padx=22, pady=15)
        self.card(cards, "TOTAL STUDENTS", total_students)
        self.card(cards, "PRESENT TODAY", present_today)
        self.card(cards, "TOTAL BATCHES", total_batches)

        welcome = tk.Frame(self.main, bg="white", padx=25, pady=24)
        welcome.pack(fill="x", padx=30, pady=22)
        tk.Label(
            welcome, text="Manage your college attendance in one place",
            bg="white", fg=self.dark, font=("Arial", 15, "bold")
        ).pack(anchor="w")
        tk.Label(
            welcome,
            text="Use the left menu to add students, mark attendance, view reports, update records and add marks.",
            bg="white", fg="#718096", font=("Arial", 10),
            wraplength=800, justify="left"
        ).pack(anchor="w", pady=(10, 0))

        batch_frame = tk.Frame(self.main, bg="white", padx=22, pady=18)
        batch_frame.pack(fill="x", padx=30, pady=5)
        tk.Label(batch_frame, text="AVAILABLE BATCHES",
                 bg="white", fg=self.dark, font=("Arial", 11, "bold")).pack(anchor="w")
        tk.Label(batch_frame, text="   1. BCA       2. Civil       3. IT       4. AIML",
                 bg="white", fg="#52647d", font=("Arial", 12)).pack(anchor="w", pady=12)

    def add_student(self):
        self.page_heading("Add Student", "Enter student details and select a batch")
        form = tk.Frame(self.main, bg="white", padx=30, pady=25)
        form.pack(anchor="nw", padx=30, pady=10)

        entries = {}
        labels = ["Student ID", "Student Name", "Batch", "Phone Number"]
        for i, label in enumerate(labels):
            tk.Label(form, text=label, bg="white", fg=self.text,
                     font=("Arial", 10, "bold")).grid(
                row=i, column=0, sticky="w", padx=(0, 35), pady=12
            )
            if label == "Batch":
                widget, batch_var = self.batch_selector(form)
                widget.grid(row=i, column=1, sticky="w", pady=12)
                entries[label] = batch_var
            else:
                widget = ttk.Entry(form, width=32)
                widget.grid(row=i, column=1, sticky="w", pady=12)
                entries[label] = widget

        def save():
            sid = entries["Student ID"].get().strip()
            name = entries["Student Name"].get().strip()
            batch_name = entries["Batch"].get()
            phone = entries["Phone Number"].get().strip()

            if not sid or not name or not batch_name:
                messagebox.showwarning("Missing details", "Enter Student ID, Student Name and Batch.")
                return
            if phone and (not phone.isdigit() or len(phone) != 10):
                messagebox.showwarning("Invalid phone", "Phone number must contain 10 digits.")
                return

            batch_id = [key for key, value in BATCHES.items() if value == batch_name][0]
            self.run_query(
                """INSERT INTO students
                   (student_id, student_name, batch_id, branch, phone)
                   VALUES (%s, %s, %s, %s, %s)""",
                (sid, name, batch_id, batch_name, phone)
            )
            messagebox.showinfo("Success", "Student added successfully.")
            for key in ["Student ID", "Student Name", "Phone Number"]:
                entries[key].delete(0, tk.END)
            entries["Batch"].set("")

        tk.Button(form, text="Save Student", command=save,
                  bg=self.accent, fg="white", relief="flat",
                  padx=22, pady=10, cursor="hand2").grid(
            row=4, column=1, sticky="e", pady=18
        )

    def view_students(self):
        self.page_heading("View Students", "View all students batch-wise or search one student by ID")

        # Search one student's details
        search_bar = tk.Frame(self.main, bg=self.bg)
        search_bar.pack(fill="x", padx=30, pady=(0, 8))
        tk.Label(search_bar, text="Enter Student ID", bg=self.bg,
                 fg=self.text, font=("Arial", 10, "bold")).pack(side="left")
        student_id_entry = ttk.Entry(search_bar, width=20)
        student_id_entry.pack(side="left", padx=10)

        detail_tree = self.make_table(
            self.main,
            ("student_id", "student_name", "batch_id", "branch", "phone", "marks"),
            ("Student ID", "Student Name", "Batch ID", "Branch", "Phone", "Marks")
        )
        detail_tree.configure(height=4)

        def search_student():
            for item in detail_tree.get_children():
                detail_tree.delete(item)

            sid = student_id_entry.get().strip()
            if not sid:
                messagebox.showwarning("Student ID required", "Please enter a Student ID.")
                return

            rows = self.run_query(
                """SELECT student_id, student_name, batch_id, branch, phone, marks
                   FROM students
                   WHERE student_id = %s""",
                (sid,), "all"
            )

            if not rows:
                messagebox.showinfo("Not found", "No student found with this Student ID.")
                return

            for row in rows:
                detail_tree.insert("", "end", values=row)

        tk.Button(search_bar, text="Search Student", command=search_student,
                  bg=self.accent, fg="white", relief="flat", padx=14, pady=6).pack(side="left")

        # Batch-wise list of all students
        tk.Label(self.main, text="ALL STUDENTS - BATCH WISE",
                 bg=self.bg, fg=self.dark, font=("Arial", 12, "bold")).pack(
            anchor="w", padx=30, pady=(8, 4)
        )
        bar = tk.Frame(self.main, bg=self.bg)
        bar.pack(fill="x", padx=30)
        tk.Label(bar, text="Select Batch", bg=self.bg, fg=self.text).pack(side="left")
        combo, batch_var = self.batch_selector(bar, all_option=True)
        combo.set("All")
        combo.pack(side="left", padx=10)

        tree = self.make_table(
            self.main,
            ("student_id", "student_name", "batch_id", "branch", "phone", "marks"),
            ("Student ID", "Student Name", "Batch ID", "Branch", "Phone", "Marks")
        )
        tree.configure(height=7)

        def load():
            for item in tree.get_children():
                tree.delete(item)
            if batch_var.get() == "All":
                rows = self.run_query(
                    """SELECT student_id, student_name, batch_id, branch, phone, marks
                       FROM students ORDER BY batch_id, student_id""", fetch="all"
                )
            else:
                batch_id = [k for k, v in BATCHES.items() if v == batch_var.get()][0]
                rows = self.run_query(
                    """SELECT student_id, student_name, batch_id, branch, phone, marks
                       FROM students WHERE batch_id=%s ORDER BY student_id""",
                    (batch_id,), "all"
                )
            for row in rows:
                tree.insert("", "end", values=row)

        tk.Button(bar, text="Show Students", command=load, bg=self.accent,
                  fg="white", relief="flat", padx=15, pady=6).pack(side="left")
        load()

    def mark_attendance(self):
        self.page_heading("Mark Attendance", "Select a batch and mark each student's status")
        bar = tk.Frame(self.main, bg=self.bg)
        bar.pack(fill="x", padx=30)
        tk.Label(bar, text="Batch", bg=self.bg).pack(side="left")
        combo, batch_var = self.batch_selector(bar)
        combo.pack(side="left", padx=8)
        tk.Label(bar, text="Attendance Date (YYYY-MM-DD)", bg=self.bg).pack(side="left", padx=(18, 6))
        date_entry = ttk.Entry(bar, width=15)
        date_entry.insert(0, str(date.today()))
        date_entry.pack(side="left")

        table_area = tk.Frame(self.main, bg="white")
        table_area.pack(fill="both", expand=True, padx=30, pady=15)
        tk.Label(table_area, text="Student ID", bg="white", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=35, pady=12)
        tk.Label(table_area, text="Student Name", bg="white", font=("Arial", 10, "bold")).grid(row=0, column=1, padx=35)
        tk.Label(table_area, text="Attendance Status", bg="white", font=("Arial", 10, "bold")).grid(row=0, column=2, padx=35)

        status_list = []

        def load_students():
            for widget in table_area.grid_slaves():
                if int(widget.grid_info()["row"]) > 0:
                    widget.destroy()
            status_list.clear()
            if not batch_var.get():
                messagebox.showwarning("Select batch", "Please select a batch.")
                return
            batch_id = [k for k, v in BATCHES.items() if v == batch_var.get()][0]
            students = self.run_query(
                "SELECT student_id, student_name FROM students WHERE batch_id=%s ORDER BY student_id",
                (batch_id,), "all"
            )
            if not students:
                messagebox.showinfo("No students", "No students found in this batch.")
                return
            for i, student in enumerate(students, start=1):
                tk.Label(table_area, text=student[0], bg="white").grid(row=i, column=0, pady=8)
                tk.Label(table_area, text=student[1], bg="white").grid(row=i, column=1, pady=8)
                status = ttk.Combobox(table_area, values=["Present", "Absent", "leave"],
                                      state="readonly", width=16)
                status.set("Present")
                status.grid(row=i, column=2, pady=8)
                status_list.append((student[0], status))

        def save_attendance():
            if not status_list:
                messagebox.showwarning("No students", "Load students before saving attendance.")
                return
            selected_date = date_entry.get().strip()
            for student_id, status_box in status_list:
                self.run_query(
                    """INSERT INTO attendance (student_id, attendance_date, status)
                       VALUES (%s, %s, %s)
                       ON DUPLICATE KEY UPDATE status=VALUES(status)""",
                    (student_id, selected_date, status_box.get())
                )
            messagebox.showinfo("Success", "Attendance saved successfully.")

        tk.Button(bar, text="Load Students", command=load_students,
                  bg=self.accent, fg="white", relief="flat", padx=12, pady=6).pack(side="left", padx=10)
        tk.Button(self.main, text="Save Attendance", command=save_attendance,
                  bg="#16804a", fg="white", relief="flat", padx=20, pady=9).pack(anchor="e", padx=32, pady=5)

    def batch_attendance(self):
        self.page_heading("Batch-wise Attendance", "View attendance for all students in a selected batch")
        bar = tk.Frame(self.main, bg=self.bg)
        bar.pack(fill="x", padx=30)
        tk.Label(bar, text="Batch", bg=self.bg).pack(side="left")
        combo, batch_var = self.batch_selector(bar)
        combo.pack(side="left", padx=8)
        tk.Label(bar, text="Date", bg=self.bg).pack(side="left", padx=(15, 5))
        date_entry = ttk.Entry(bar, width=15)
        date_entry.insert(0, str(date.today()))
        date_entry.pack(side="left")
        tree = self.make_table(
            self.main,
            ("student_id", "student_name", "batch_name", "attendance_date", "status"),
            ("Student ID", "Student Name", "Batch", "Attendance Date", "Status")
        )

        def load():
            for item in tree.get_children():
                tree.delete(item)
            if not batch_var.get():
                messagebox.showwarning("Select batch", "Please select a batch.")
                return
            batch_id = [k for k, v in BATCHES.items() if v == batch_var.get()][0]
            rows = self.run_query(
                """SELECT s.student_id, s.student_name, b.batch_name,
                          a.attendance_date, a.status
                   FROM students s
                   JOIN batches b ON s.batch_id=b.batch_id
                   LEFT JOIN attendance a
                     ON s.student_id=a.student_id AND a.attendance_date=%s
                   WHERE s.batch_id=%s
                   ORDER BY s.student_id""",
                (date_entry.get().strip(), batch_id), "all"
            )
            for row in rows:
                tree.insert("", "end", values=row)

        tk.Button(bar, text="Show Attendance", command=load,
                  bg=self.accent, fg="white", relief="flat", padx=14, pady=6).pack(side="left", padx=10)

    def student_report(self):
        self.page_heading("Student Attendance Report", "View total Present, Absent and Leave records")
        bar = tk.Frame(self.main, bg=self.bg)
        bar.pack(fill="x", padx=30)
        tk.Label(bar, text="Student ID", bg=self.bg).pack(side="left")
        id_entry = ttk.Entry(bar, width=18)
        id_entry.pack(side="left", padx=10)

        report = tk.Frame(self.main, bg="white", padx=25, pady=22)
        report.pack(fill="x", padx=30, pady=20)

        def load():
            for widget in report.winfo_children():
                widget.destroy()
            rows = self.run_query(
                """SELECT s.student_id, s.student_name, s.branch,
                          COUNT(a.attendance_id) AS total_days,
                          SUM(a.status='Present') AS present_days,
                          SUM(a.status='Absent') AS absent_days,
                          SUM(a.status='leave') AS leave_days
                   FROM students s
                   LEFT JOIN attendance a ON s.student_id=a.student_id
                   WHERE s.student_id=%s
                   GROUP BY s.student_id, s.student_name, s.branch""",
                (id_entry.get().strip(),), "all"
            )
            if not rows:
                messagebox.showinfo("Not found", "Student not found.")
                return
            row = rows[0]
            details = [
                ("Student ID", row[0]),
                ("Student Name", row[1]),
                ("Branch", row[2]),
                ("Total Attendance Records", row[3]),
                ("Present", row[4] or 0),
                ("Absent", row[5] or 0),
                ("Leave", row[6] or 0)
            ]
            for i, (label, value) in enumerate(details):
                tk.Label(report, text=label, bg="white", fg="#718096",
                         font=("Arial", 10, "bold")).grid(row=i, column=0, sticky="w", pady=7, padx=8)
                tk.Label(report, text=str(value), bg="white", fg=self.dark,
                         font=("Arial", 10)).grid(row=i, column=1, sticky="w", pady=7, padx=20)

        tk.Button(bar, text="Generate Report", command=load,
                  bg=self.accent, fg="white", relief="flat", padx=14, pady=6).pack(side="left")

    def update_student(self):
        self.page_heading("Update Student", "Search a student to view old details, then edit and update")
        form = tk.Frame(self.main, bg="white", padx=28, pady=24)
        form.pack(anchor="nw", padx=30, pady=10)
        fields = {}
        labels = ["Student ID", "Student Name", "Batch", "Phone Number"]

        for i, label in enumerate(labels):
            tk.Label(form, text=label, bg="white", fg=self.text).grid(
                row=i, column=0, sticky="w", padx=(0, 30), pady=11
            )
            if label == "Batch":
                widget, batch_var = self.batch_selector(form)
                widget.grid(row=i, column=1, sticky="w", pady=11)
                fields[label] = batch_var
            else:
                widget = ttk.Entry(form, width=30)
                widget.grid(row=i, column=1, pady=11)
                fields[label] = widget

        def search_student():
            sid = fields["Student ID"].get().strip()
            if not sid:
                messagebox.showwarning("Missing ID", "Enter Student ID first.")
                return
            row = self.run_query(
                "SELECT student_name, batch_id, phone FROM students WHERE student_id=%s",
                (sid,), "one"
            )
            if not row:
                messagebox.showinfo("Not found", "Student not found.")
                return
            fields["Student Name"].delete(0, tk.END)
            fields["Student Name"].insert(0, row[0] or "")
            fields["Batch"].set(BATCHES.get(row[1], ""))
            fields["Phone Number"].delete(0, tk.END)
            fields["Phone Number"].insert(0, row[2] or "")

        def update():
            sid = fields["Student ID"].get().strip()
            name = fields["Student Name"].get().strip()
            batch_name = fields["Batch"].get()
            phone = fields["Phone Number"].get().strip()
            if not sid or not name or not batch_name:
                messagebox.showwarning("Missing details", "Search a student and fill all details before updating.")
                return
            if phone and (not phone.isdigit() or len(phone) != 10):
                messagebox.showwarning("Invalid phone", "Phone number must contain 10 digits.")
                return
            batch_id = [k for k, v in BATCHES.items() if v == batch_name][0]
            self.run_query(
                "UPDATE students SET student_name=%s, batch_id=%s, branch=%s, phone=%s WHERE student_id=%s",
                (name, batch_id, batch_name, phone, sid)
            )
            messagebox.showinfo("Update", "Student details updated successfully if the Student ID exists.")

        tk.Button(form, text="Search Student", command=search_student,
                  bg=self.dark2, fg="white", relief="flat", padx=16, pady=8).grid(
            row=0, column=2, padx=(15, 0), pady=11
        )
        tk.Button(form, text="Update Student", command=update,
                  bg=self.accent, fg="white", relief="flat", padx=20, pady=9).grid(
            row=4, column=1, sticky="e", pady=16
        )

    def update_attendance(self):
        self.page_heading("Update Attendance", "Change a student's attendance status for a date")
        form = tk.Frame(self.main, bg="white", padx=28, pady=24)
        form.pack(anchor="nw", padx=30, pady=10)
        fields = {}
        labels = ["Student ID", "Attendance Date (YYYY-MM-DD)", "New Status"]
        for i, label in enumerate(labels):
            tk.Label(form, text=label, bg="white", fg=self.text).grid(
                row=i, column=0, sticky="w", padx=(0, 30), pady=12
            )
            if label == "New Status":
                widget = ttk.Combobox(form, values=["Present", "Absent", "leave"],
                                      state="readonly", width=27)
            else:
                widget = ttk.Entry(form, width=30)
            widget.grid(row=i, column=1, pady=12)
            fields[label] = widget

        def update():
            self.run_query(
                """UPDATE attendance SET status=%s
                   WHERE student_id=%s AND attendance_date=%s""",
                (fields["New Status"].get(),
                 fields["Student ID"].get().strip(),
                 fields["Attendance Date (YYYY-MM-DD)"].get().strip())
            )
            messagebox.showinfo("Update", "Attendance record updated if a matching record exists.")

        tk.Button(form, text="Update Attendance", command=update,
                  bg=self.accent, fg="white", relief="flat", padx=20, pady=9).grid(
            row=3, column=1, sticky="e", pady=16
        )

    def add_marks(self):
        self.page_heading("Add Marks", "Enter marks for students batch-wise")
        bar = tk.Frame(self.main, bg=self.bg)
        bar.pack(fill="x", padx=30)
        tk.Label(bar, text="Select Batch", bg=self.bg).pack(side="left")
        combo, batch_var = self.batch_selector(bar)
        combo.pack(side="left", padx=10)

        table_area = tk.Frame(self.main, bg="white")
        table_area.pack(fill="both", expand=True, padx=30, pady=15)
        tk.Label(table_area, text="Student ID", bg="white", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=30, pady=12)
        tk.Label(table_area, text="Student Name", bg="white", font=("Arial", 10, "bold")).grid(row=0, column=1, padx=30)
        tk.Label(table_area, text="Marks", bg="white", font=("Arial", 10, "bold")).grid(row=0, column=2, padx=30)

        mark_entries = []

        def load_students():
            for widget in table_area.grid_slaves():
                if int(widget.grid_info()["row"]) > 0:
                    widget.destroy()
            mark_entries.clear()
            if not batch_var.get():
                messagebox.showwarning("Select batch", "Please select a batch.")
                return
            batch_id = [k for k, v in BATCHES.items() if v == batch_var.get()][0]
            students = self.run_query(
                "SELECT student_id, student_name FROM students WHERE batch_id=%s ORDER BY student_id",
                (batch_id,), "all"
            )
            if not students:
                messagebox.showinfo("No students", "No students found in this batch.")
                return
            for i, student in enumerate(students, start=1):
                tk.Label(table_area, text=student[0], bg="white").grid(row=i, column=0, pady=8)
                tk.Label(table_area, text=student[1], bg="white").grid(row=i, column=1, pady=8)
                entry = ttk.Entry(table_area, width=16)
                entry.grid(row=i, column=2, pady=8)
                mark_entries.append((student[0], entry))

        def save_marks():
            if not mark_entries:
                messagebox.showwarning("No students", "Load students before saving marks.")
                return
            for student_id, entry in mark_entries:
                value = entry.get().strip()
                if value:
                    self.run_query(
                        "UPDATE students SET marks=%s WHERE student_id=%s",
                        (value, student_id)
                    )
            messagebox.showinfo("Success", "Marks saved for the entered students.")

        tk.Button(bar, text="Load Students", command=load_students,
                  bg=self.accent, fg="white", relief="flat", padx=12, pady=6).pack(side="left")
        tk.Button(self.main, text="Save Marks", command=save_marks,
                  bg="#16804a", fg="white", relief="flat", padx=20, pady=9).pack(
            anchor="e", padx=32, pady=5
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = AttendanceApp(root)
    root.mainloop()
