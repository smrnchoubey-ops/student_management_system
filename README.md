# Student Management System - Advanced DBMS Project

A comprehensive Student Management System built with **Python**, **Tkinter (GUI)**, and **MySQL**. This project is designed to demonstrate core Database Management System (DBMS) concepts including DDL, DML, TCL, DCL, and various types of SQL JOINs.

## Features

- **Student Management:** Add, update, delete, and search students.
- **Subject & Marks Management:** Assign subjects and marks to students.
- **Advanced SQL Operations:**
  - **DDL (Data Definition Language):** Auto-creation of database and tables (`Students`, `Subjects`, `Marks`).
  - **DML (Data Manipulation Language):** Insert, Update, Delete records.
  - **TCL (Transaction Control Language):** Commit and Rollback mechanisms to ensure data integrity.
  - **JOINs:** Inner Join, Left Join, and Right Join implementations to generate complex reports.
- **Data Export:** Export treeview data (Students, Marks, etc.) directly to CSV files.
- **Interactive UI:** A modern, dark-themed GUI built using `tkinter` and `ttk`.

## Prerequisites

- **Python 3.x** installed on your system.
- **MySQL Server** installed and running locally.

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/smrnchoubey-ops/student_management_system.git
   cd student_management_system
   ```

2. **Install dependencies:**
   The project requires the MySQL Connector for Python. You can install it via pip:
   ```bash
   pip install mysql-connector-python
   ```

3. **Configure the Database Connection:**
   Open `student_management_system.py` and update the `DB_CONFIG` dictionary (around line 30) with your MySQL credentials:
   ```python
   DB_CONFIG = {
       "host":     "localhost",
       "user":     "root",        # Your MySQL username
       "password": "your_password", # Your MySQL password
       "port":     3306,
   }
   ```
   *Note: The script will automatically create the database `stu_mgmt_db` and the required tables on the first run.*

4. **Run the Application:**
   ```bash
   python student_management_system.py
   ```

## Database Schema

The system automatically provisions the following tables:
- **`Students`**: `student_id` (PK), `name`, `age`, `gender`, `course`, `created_at`
- **`Subjects`**: `subject_id` (PK), `subject_name` (Unique)
- **`Marks`**: `marks_id` (PK), `student_id` (FK), `subject_id` (FK), `marks`

## Troubleshooting

- **Database Connection Error:** Ensure your MySQL server is running and the credentials in `DB_CONFIG` are correct.
- **ModuleNotFoundError:** Ensure you have installed the `mysql-connector-python` package in your current Python environment.
