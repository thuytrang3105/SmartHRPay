# import pyodbc
# import random
# from faker import Faker
# from datetime import datetime, timedelta
# import mysql.connector
# import pymysql
# fake = Faker()

# # # Thông tin kết nối database
# # DB_HUMAN = {
# #     'server': '.', 
# #     'database': 'HUMAN_2025'
# # }

# # DB_PAYROLL = {
# #     'host': 'localhost',
# #     'database': 'payroll',
# #     'user': 'root',
# #     'password': '123456123456'
# # }

# # DB_USER = {
# #     'host': 'localhost',
# #     'database': 'user',
# #     'user': 'root',
# #     'password': '123456123456'
# # }

# # # Kết nối database
# # conn_human = pyodbc.connect(
# #     f"DRIVER={{SQL Server}};"
# #     f"SERVER={DB_HUMAN['server']};"
# #     f"DATABASE={DB_HUMAN['database']};"
# #     "Trusted_Connection=yes;"
# # )
# # ////////////////// đoạn này tui làm để có thể chạy được trên máy tui ////////////


# # Thông tin kết nối database MySQL
# DB_HUMAN = {
#     'host': 'localhost',
#     'database': 'human',
#     'user': 'root',
#     'password': 'Lovecode@05'
# }

# DB_PAYROLL = {
#     'host': 'localhost',
#     'database': 'payroll',
#     'user': 'root',
#     'password': 'Lovecode@05'
# }

# DB_USER = {
#     'host': 'localhost',
#     'database': 'user',
#     'user': 'root',
#     'password': 'Lovecode@05'
# }

# # Kết nối database MySQL
# conn_human = pymysql.connect(
#     host=DB_HUMAN['host'],
#     user=DB_HUMAN['user'],
#     password=DB_HUMAN['password'],
#     database=DB_HUMAN['database']
# )

# cursor_human = conn_human.cursor()

# conn_payroll = mysql.connector.connect(**DB_PAYROLL)
# cursor_payroll = conn_payroll.cursor()

# conn_user = mysql.connector.connect(**DB_USER)
# cursor_user = conn_user.cursor()

# print("Kết nối thành công!")

# # Xóa dữ liệu cũ trong bảng account để tránh trùng lặp
# cursor_user.execute("DELETE FROM account")
# conn_user.commit()

# # Tạo Jobs
# job_titles = [
#     "Software Engineer", "Backend Developer", "Frontend Developer", "Data Scientist",
#     "DevOps Engineer", "QA Engineer", "Product Manager", "UI/UX Designer",
#     "Scrum Master", "System Administrator"
# ]

# jobs = []
# for job_title in job_titles:
#     min_salary = round(random.uniform(1000, 5000), 2)
#     max_salary = min_salary + round(random.uniform(2000, 7000), 2)
    
#     cursor_human.execute("INSERT INTO Jobs (JobTitle, MinSalary, MaxSalary) OUTPUT INSERTED.JobID VALUES (?, ?, ?)",
#                         (job_title, min_salary, max_salary))
#     job_id = cursor_human.fetchone()[0]
#     cursor_payroll.execute("INSERT INTO jobs (job_id, job_title, min_salary, max_salary) VALUES (%s, %s, %s, %s)",
#                          (job_id, job_title, min_salary, max_salary))
#     jobs.append(job_id)

# # Tạo Departments
# departments_list = [
#     "Engineering", "Product Management", "Quality Assurance", "Human Resources",
#     "IT Support", "Marketing", "Finance", "Sales", "Customer Support", "R&D"
# ]

# departments = []
# for dept_name in departments_list:
#     cursor_human.execute("INSERT INTO Departments (DepartmentName) OUTPUT INSERTED.DepartmentID VALUES (?)", (dept_name,))
#     dept_id = cursor_human.fetchone()[0]
#     cursor_payroll.execute("INSERT INTO departments (department_id, department_name) VALUES (%s, %s)",
#                          (dept_id, dept_name))
#     departments.append(dept_id)

# # Tạo Applicants và Employees
# applicants = []
# employees = []
# for _ in range(30):
#     first_name = fake.first_name()
#     last_name = fake.last_name()
#     email = f"{first_name.lower()}.{last_name.lower()}@company.com"
#     phone = fake.phone_number()[:15]
#     app_date = datetime.now() - timedelta(days=random.randint(1, 365))
#     status = random.choice(["Pending", "Interviewing", "Hired", "Rejected"])
#     job_id = random.choice(jobs)
    
#     cursor_human.execute("""
#         INSERT INTO Applicants (FirstName, LastName, Email, Phone, ApplicationDate, Status, JobID) 
#         OUTPUT INSERTED.ApplicantID 
#         VALUES (?, ?, ?, ?, ?, ?, ?)""",
#         (first_name, last_name, email, phone, app_date, status, job_id))
#     applicant_id = cursor_human.fetchone()[0]
#     applicants.append(applicant_id)
    
#     # Tạo Employees cho 20 applicants đầu tiên
#     if len(employees) < 20:
#         hire_date = datetime.now() - timedelta(days=random.randint(30, 1000))
#         dept_id = random.choice(departments)
#         salary = round(random.uniform(3000, 15000), 2)
#         emp_status = random.choice(["Active", "Inactive"])
        
#         cursor_human.execute("""
#             INSERT INTO Employees (ApplicantID, DepartmentID, HireDate, Salary, Status) 
#             OUTPUT INSERTED.EmployeeID 
#             VALUES (?, ?, ?, ?, ?)""",
#             (applicant_id, dept_id, hire_date, salary, emp_status))
#         emp_id = cursor_human.fetchone()[0]
        
#         # Đồng bộ sang MySQL (payroll)
#         cursor_payroll.execute("""
#             INSERT INTO employees (employee_id, first_name, last_name, email, phone, hire_date, department_id, job_id, salary, status) 
#             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#             ON DUPLICATE KEY UPDATE 
#             first_name=%s, last_name=%s, email=%s, phone=%s, hire_date=%s, department_id=%s, job_id=%s, salary=%s, status=%s""",
#             (emp_id, first_name, last_name, email, phone, hire_date, dept_id, job_id, salary, emp_status,
#              first_name, last_name, email, phone, hire_date, dept_id, job_id, salary, emp_status))
        
#         employees.append(emp_id)

# # Gán manager_id cho các phòng ban
# manager_ids = random.sample(employees, 5)
# for dept_id in departments:
#     if manager_ids:
#         manager_id = random.choice(manager_ids)
#         cursor_human.execute("UPDATE Departments SET ManagerID = ? WHERE DepartmentID = ?",
#                             (manager_id, dept_id))
#         cursor_payroll.execute("UPDATE departments SET manager_id = %s WHERE department_id = %s",
#                               (manager_id, dept_id))

# # Tạo dữ liệu cho bảng account (chỉ trong database user)
# cursor_payroll.execute("SELECT employee_id, first_name, last_name FROM employees")
# employee_data = cursor_payroll.fetchall()

# for emp in employee_data:
#     emp_id, first_name, last_name = emp
#     username = f"{first_name.lower()}_{emp_id}"
#     password_hash = "000000"
#     employee_name = f"{first_name} {last_name}"
#     role_name = "employee"
    
#     cursor_user.execute("""
#         INSERT INTO account (username, password_hash, employee_id, employee_name, role_name) 
#         VALUES (%s, %s, %s, %s, %s)""",
#         (username, password_hash, emp_id, employee_name, role_name))

# # Tạo Payroll
# for emp_id in employees:
#     for _ in range(3):
#         pay_date = datetime.now() - timedelta(days=random.randint(1, 90))
#         base_salary = round(random.uniform(3000, 15000), 2)
#         bonus = round(random.uniform(0, 5000), 2)
#         deductions = round(random.uniform(0, 1000), 2)
        
#         cursor_human.execute("""
#             INSERT INTO Payroll (EmployeeID, PayDate, BaseSalary, Bonus, Deductions) 
#             VALUES (?, ?, ?, ?, ?)""",
#             (emp_id, pay_date, base_salary, bonus, deductions))
        
#         cursor_payroll.execute("""
#             INSERT INTO payroll (employee_id, pay_date, base_salary, bonus, deductions, net_salary) 
#             VALUES (%s, %s, %s, %s, %s, %s)""",
#             (emp_id, pay_date, base_salary, bonus, deductions, base_salary + bonus - deductions))

# # Tạo Attendance
# for emp_id in employees:
#     for day in range(90):
#         work_date = datetime.now() - timedelta(days=day)
#         status = random.choices(["present", "absent", "leave"], weights=[0.8, 0.1, 0.1], k=1)[0]
#         cursor_payroll.execute("""
#             INSERT INTO attendance (employee_id, date, status) 
#             VALUES (%s, %s, %s)""",
#             (emp_id, work_date, status))

# # Tạo Shareholders
# shareholders = []
# for _ in range(10):
#     first_name = fake.first_name()
#     last_name = fake.last_name()
#     full_name = f"{first_name} {last_name}"  # Kết hợp first_name và last_name thành FullName
#     unique_num = random.randint(1000, 9999)
#     email = f"{first_name.lower()}.{last_name.lower()}{unique_num}@shareholder.com"
#     phone = fake.phone_number()[:15]
#     investment = round(random.uniform(10000, 1000000), 2)
#     is_employee = random.choice([0, 1])
#     emp_id = random.choice(employees) if is_employee else None
    
#     cursor_human.execute("""
#         INSERT INTO Shareholders (FullName, Email, Phone, InvestmentAmount, IsEmployee, EmployeeID) 
#         OUTPUT INSERTED.ShareholderID 
#         VALUES (?, ?, ?, ?, ?, ?)""",
#         (full_name, email, phone, investment, is_employee, emp_id))
#     shareholder_id = cursor_human.fetchone()[0]
#     shareholders.append(shareholder_id)

# # Tạo Dividends
# for shareholder_id in shareholders:
#     for _ in range(2):
#         div_amount = round(random.uniform(1000, 50000), 2)
#         pay_date = datetime.now() - timedelta(days=random.randint(1, 180))
#         cursor_human.execute("""
#             INSERT INTO Dividends (ShareholderID, DividendAmount, PaymentDate) 
#             VALUES (?, ?, ?)""",
#             (shareholder_id, div_amount, pay_date))

# # Commit tất cả thay đổi
# conn_human.commit()
# conn_payroll.commit()
# conn_user.commit()

# # Đóng kết nối
# cursor_human.close()
# conn_human.close()
# cursor_payroll.close()
# conn_payroll.close()
# cursor_user.close()
# conn_user.close()

# print("✅ Dữ liệu đã được tạo thành công với đầy đủ thông tin và liên kết giữa các database!")
import random
from faker import Faker
from datetime import datetime, timedelta
import mysql.connector
import pymysql

fake = Faker()

# Database connection information
DB_HUMAN = {
    'host': 'localhost',
    'database': 'human',
    'user': 'root',
    'password': 'Lovecode@05'
}

DB_PAYROLL = {
    'host': 'localhost',
    'database': 'payroll',
    'user': 'root',
    'password': 'Lovecode@05'
}

DB_USER = {
    'host': 'localhost',
    'database': 'user',
    'user': 'root',
    'password': 'Lovecode@05'
}

# Connect to MySQL databases
try:
    conn_human = pymysql.connect(**DB_HUMAN)
    cursor_human = conn_human.cursor()

    conn_payroll = mysql.connector.connect(**DB_PAYROLL)
    cursor_payroll = conn_payroll.cursor()

    conn_user = mysql.connector.connect(**DB_USER)
    cursor_user = conn_user.cursor()

    print("✅ Connected successfully!")
except Exception as e:
    print(f"❌ Connection error: {e}")
    exit(1)

# Clear old data to avoid duplicates
try:
    cursor_user.execute("DELETE FROM account")
    conn_user.commit()
    print("✅ Cleared user accounts")
except Exception as e:
    print(f"❌ Error clearing user accounts: {e}")

# Create Jobs
job_titles = [
    "Software Engineer", "Backend Developer", "Frontend Developer", "Data Scientist",
    "DevOps Engineer", "QA Engineer", "Product Manager", "UI/UX Designer",
    "Scrum Master", "System Administrator"
]

jobs = []
for job_title in job_titles:
    min_salary = round(random.uniform(1000, 5000), 2)
    max_salary = min_salary + round(random.uniform(2000, 7000), 2)
    
    try:
        cursor_human.execute(
            "INSERT INTO Jobs (JobTitle, MinSalary, MaxSalary) VALUES (%s, %s, %s)",
            (job_title, min_salary, max_salary)
        )
        job_id = cursor_human.lastrowid
        jobs.append(job_id)

        cursor_payroll.execute(
            "INSERT INTO jobs (job_id, job_title, min_salary, max_salary) VALUES (%s, %s, %s, %s)",
            (job_id, job_title, min_salary, max_salary)
        )
    except Exception as e:
        print(f"❌ Error creating job {job_title}: {e}")

# Create Departments
departments_list = [
    "Engineering", "Product Management", "Quality Assurance", "Human Resources",
    "IT Support", "Marketing", "Finance", "Sales", "Customer Support", "R&D"
]

departments = []
for dept_name in departments_list:
    try:
        cursor_human.execute("INSERT INTO Departments (DepartmentName) VALUES (%s)", (dept_name,))
        dept_id = cursor_human.lastrowid
        departments.append(dept_id)

        cursor_payroll.execute("INSERT INTO departments (department_id, department_name) VALUES (%s, %s)",
                            (dept_id, dept_name))
    except Exception as e:
        print(f"❌ Error creating department {dept_name}: {e}")

# Create Applicants and Employees
applicants = []
employees = []

for _ in range(30):
    try:
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = f"{first_name.lower()}.{last_name.lower()}@company.com"
        phone = fake.phone_number()[:15]
        app_date = datetime.now() - timedelta(days=random.randint(1, 365))
        status = random.choice(["Pending", "Interviewing", "Hired", "Rejected"])
        job_id = random.choice(jobs)

        # Insert into Human.Applicants
        cursor_human.execute("""
        INSERT INTO Applicants (FirstName, LastName, Email, PhoneNumber, ApplicationDate, Status, JobID) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        (first_name, last_name, email, phone, app_date, status, job_id))
        applicant_id = cursor_human.lastrowid
        applicants.append(applicant_id)
        
        # Insert into Payroll.applicants
        cursor_payroll.execute("""
        INSERT INTO applicants (applicant_id, first_name, last_name, email, phone_number, application_date, status, job_id) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
        (applicant_id, first_name, last_name, email, phone, app_date, status, job_id))

        if len(employees) < 20 and status == "Hired":
            hire_date = datetime.now() - timedelta(days=random.randint(30, 1000))
            dept_id = random.choice(departments)
            salary = round(random.uniform(3000, 15000), 2)
            emp_status = random.choice(["Active", "Inactive"])

            # Insert into Human.Employees
            cursor_human.execute("""
                INSERT INTO Employees (ApplicantID, DepartmentID, HireDate, Salary, Status) 
                VALUES (%s, %s, %s, %s, %s)""",
                (applicant_id, dept_id, hire_date, salary, emp_status))
            emp_id = cursor_human.lastrowid
            employees.append(emp_id)

            # Insert into Payroll.employees
            cursor_payroll.execute("""
            INSERT INTO employees (employee_id, applicant_id, department_id, hire_date, salary, status)
            VALUES (%s, %s, %s, %s, %s, %s)""",
            (emp_id, applicant_id, dept_id, hire_date, salary, emp_status))
    except Exception as e:
        print(f"❌ Error creating applicant/employee: {e}")

# Assign manager_id to some departments
try:
    manager_ids = random.sample(employees, min(5, len(employees)))
    for dept_id in departments:
        if manager_ids:
            manager_id = random.choice(manager_ids)
            cursor_human.execute("UPDATE Departments SET ManagerID = %s WHERE DepartmentID = %s",
                                (manager_id, dept_id))
            cursor_payroll.execute("UPDATE departments SET manager_id = %s WHERE department_id = %s",
                                (manager_id, dept_id))
except Exception as e:
    print(f"❌ Error assigning managers: {e}")

# Create accounts in user database
try:
    cursor_payroll.execute("SELECT employee_id, first_name, last_name FROM employees")
    employee_data = cursor_payroll.fetchall()

    for emp_id, first_name, last_name in employee_data:
        username = f"{first_name.lower()}_{emp_id}"
        password_hash = "000000"
        employee_name = f"{first_name} {last_name}"
        role_name = "employee"
        cursor_user.execute("""
            INSERT INTO account (username, password_hash, employee_id, employee_name, role_name) 
            VALUES (%s, %s, %s, %s, %s)""",
            (username, password_hash, emp_id, employee_name, role_name))
except Exception as e:
    print(f"❌ Error creating user accounts: {e}")

# Create Payroll entries
try:
    for emp_id in employees:
        for _ in range(3):
            pay_date = datetime.now() - timedelta(days=random.randint(1, 90))
            base_salary = round(random.uniform(3000, 15000), 2)
            bonus = round(random.uniform(0, 5000), 2)
            deductions = round(random.uniform(0, 1000), 2)

            cursor_human.execute("""
                INSERT INTO Payroll (EmployeeID, PayDate, BaseSalary, Bonus, Deductions) 
                VALUES (%s, %s, %s, %s, %s)""",
                (emp_id, pay_date, base_salary, bonus, deductions))

            # For payroll database, net_salary is computed by the database
            cursor_payroll.execute("""
                INSERT INTO payroll (employee_id, pay_date, base_salary, bonus, deductions) 
                VALUES (%s, %s, %s, %s, %s)""",
                (emp_id, pay_date, base_salary, bonus, deductions))
except Exception as e:
    print(f"❌ Error creating payroll entries: {e}")

# Create Attendance records
try:
    for emp_id in employees:
        for day in range(90):
            work_date = datetime.now() - timedelta(days=day)
            status = random.choices(["present", "absent", "leave"], weights=[0.8, 0.1, 0.1])[0]
            cursor_payroll.execute("""
                INSERT INTO attendance (employee_id, date, status) 
                VALUES (%s, %s, %s)""",
                (emp_id, work_date, status))
except Exception as e:
    print(f"❌ Error creating attendance records: {e}")

# Create Shareholders
try:
    shareholders = []
    for _ in range(10):
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1000, 9999)}@shareholder.com"
        phone = fake.phone_number()[:15]
        investment = round(random.uniform(10000, 1000000), 2)
        is_employee = random.choice([0, 1])
        emp_id = random.choice(employees) if is_employee else None

        # Insert into Human.Shareholders
        cursor_human.execute("""
            INSERT INTO Shareholders (FirstName, LastName, Email, PhoneNumber, InvestmentAmount, IsEmployee, EmployeeID) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (first_name, last_name, email, phone, investment, is_employee, emp_id))
        shareholder_id = cursor_human.lastrowid
        shareholders.append(shareholder_id)

        # Insert into Payroll.shareholders
        cursor_payroll.execute("""
            INSERT INTO shareholders (shareholder_id, first_name, last_name, email, phone_number, investment_amount, is_employee, employee_id) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (shareholder_id, first_name, last_name, email, phone, investment, is_employee, emp_id))
except Exception as e:
    print(f"❌ Error creating shareholders: {e}")

# Create Dividends
try:
    for shareholder_id in shareholders:
        for _ in range(2):
            div_amount = round(random.uniform(1000, 50000), 2)
            pay_date = datetime.now() - timedelta(days=random.randint(1, 180))
            cursor_human.execute("""
                INSERT INTO Dividends (ShareholderID, DividendAmount, PaymentDate) 
                VALUES (%s, %s, %s)""",
                (shareholder_id, div_amount, pay_date))
            
            cursor_payroll.execute("""
                INSERT INTO dividends (shareholder_id, dividend_amount, payment_date) 
                VALUES (%s, %s, %s)""",
                (shareholder_id, div_amount, pay_date))
except Exception as e:
    print(f"❌ Error creating dividends: {e}")

# Commit changes
try:
    conn_human.commit()
    conn_payroll.commit()
    conn_user.commit()
    print("✅ All changes committed!")
except Exception as e:
    print(f"❌ Error committing changes: {e}")

# Close connections
cursor_human.close()
conn_human.close()
cursor_payroll.close()
conn_payroll.close()
cursor_user.close()
conn_user.close()

print("✅ Data generated successfully!")