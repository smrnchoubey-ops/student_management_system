🎓 Student Management System (Advanced DBMS Project)

A professional Student Management System developed using Python, Tkinter, and MySQL. This project demonstrates real-world implementation of Database Management System (DBMS) concepts through a user-friendly desktop application.

---

🚀 Overview

This application enables efficient management of student records, subjects, and marks while showcasing advanced SQL concepts such as DDL, DML, TCL, and SQL JOIN operations. It is suitable for academic demonstrations, mini projects, and portfolio development.

---

✨ Key Features

👨‍🎓 Student Management

- Add new student records
- Update existing student information
- Delete student records
- Search students instantly

📚 Subject & Marks Management

- Add and manage subjects
- Assign marks to students
- View complete academic records

🗄️ Database Operations

- Automatic database creation
- Automatic table creation
- Foreign key relationships
- Data validation

⚡ SQL Concepts Demonstrated

DDL (Data Definition Language)

- CREATE DATABASE
- CREATE TABLE
- ALTER TABLE (where applicable)

DML (Data Manipulation Language)

- INSERT
- UPDATE
- DELETE
- SELECT

TCL (Transaction Control Language)

- COMMIT
- ROLLBACK

SQL JOIN Operations

- INNER JOIN
- LEFT JOIN
- RIGHT JOIN

📊 Export Feature

- Export student records to CSV
- Export marks reports to CSV
- Easy data sharing and backup

🎨 Modern User Interface

- Dark-themed GUI
- Interactive dashboard
- User-friendly navigation
- Responsive TreeView tables

---

🛠️ Tech Stack

- Language: Python 3.x
- GUI: Tkinter & ttk
- Database: MySQL
- Connector: mysql-connector-python

---

📂 Project Structure

student_management_system/
│
├── student_management_system.py
├── README.md
└── requirements.txt

---

⚙️ Installation

1. Clone the Repository

git clone https://github.com/smrnchoubey-ops/student_management_system.git

cd student_management_system

---

2. Install Required Package

pip install mysql-connector-python

---

3. Configure MySQL

Open student_management_system.py and update the database configuration.

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "your_password",
    "port": 3306
}

The application will automatically create:

- Database: "stu_mgmt_db"
- Students Table
- Subjects Table
- Marks Table

No manual SQL setup is required.

---

▶️ Run the Project

python student_management_system.py

---

🗃️ Database Schema

Students

Column| Description
student_id| Primary Key
name| Student Name
age| Age
gender| Gender
course| Course
created_at| Record Creation Time

---

Subjects

Column| Description
subject_id| Primary Key
subject_name| Unique Subject Name

---

Marks

Column| Description
marks_id| Primary Key
student_id| Foreign Key
subject_id| Foreign Key
marks| Student Marks

---

📸 Application Highlights

- Student Registration
- Subject Management
- Marks Management
- Search Functionality
- SQL Join Reports
- CSV Export
- Automatic Database Initialization
- Modern Dark Theme GUI

---

❗ Troubleshooting

Unable to Connect to MySQL

- Verify that MySQL Server is running.
- Check the username and password in "DB_CONFIG".
- Ensure the MySQL port is correct.

ModuleNotFoundError

Install the required package:

pip install mysql-connector-python

---

🎯 Learning Outcomes

This project demonstrates practical implementation of:

- Database Management Systems (DBMS)
- SQL Queries
- Relational Database Design
- Primary & Foreign Keys
- CRUD Operations
- Transactions (COMMIT & ROLLBACK)
- SQL JOINs
- Python GUI Development
- MySQL Database Connectivity
- CSV Data Export

---

👨‍💻 Author

Kshama Chaturvedi

If you found this project helpful, consider giving the repository a ⭐ on GitHub.
