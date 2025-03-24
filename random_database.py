import pyodbc
import random
from faker import Faker
from datetime import datetime, timedelta
import mysql.connector

fake = Faker()

# Thông tin kết nối database
DB_HUMAN = {
    'server': '.', 
    'database': 'HUMAN_2025'
}

DB_PAYROLL = {
    'host': 'localhost',
    'database': 'payroll',
    'user': 'root',
    'password': '123456123456'
}

DB_USER = {
    'host': 'localhost',
    'database': 'user',
    'user': 'root',
    'password': '123456123456'
}

# Kết nối database
conn_human = pyodbc.connect(
    f"DRIVER={{SQL Server}};"
    f"SERVER={DB_HUMAN['server']};"
    f"DATABASE={DB_HUMAN['database']};"
    "Trusted_Connection=yes;"
)
cursor_human = conn_human.cursor()

conn_payroll = mysql.connector.connect(**DB_PAYROLL)
cursor_payroll = conn_payroll.cursor()

# Sửa lỗi: Tạo kết nối riêng cho database user
conn_user = mysql.connector.connect(**DB_USER)
cursor_user = conn_user.cursor()

print("Kết nối thành công!")

# Tạo Jobs
job_titles = [
    "Software Engineer", "Backend Developer", "Frontend Developer", "Data Scientist",
    "DevOps Engineer", "QA Engineer", "Product Manager", "UI/UX Designer",
    "Scrum Master", "System Administrator"
]

jobs = []
for job_title in job_titles:
    min_salary = round(random.uniform(1000, 5000), 2)
    max_salary = min_salary + round(random.uniform(2000, 7000), 2)
    
    cursor_human.execute("INSERT INTO Jobs (JobTitle, MinSalary, MaxSalary) OUTPUT INSERTED.JobID VALUES (?, ?, ?)",
                        (job_title, min_salary, max_salary))
    job_id = cursor_human.fetchone()[0]
    cursor_payroll.execute("INSERT INTO jobs (job_id, job_title, min_salary, max_salary) VALUES (%s, %s, %s, %s)",
                         (job_id, job_title, min_salary, max_salary))
    jobs.append(job_id)

# Tạo Departments
departments_list = [
    "Engineering", "Product Management", "Quality Assurance", "Human Resources",
    "IT Support", "Marketing", "Finance", "Sales", "Customer Support", "R&D"
]

departments = []
for dept_name in departments_list:
    cursor_human.execute("INSERT INTO Departments (DepartmentName) OUTPUT INSERTED.DepartmentID VALUES (?)", (dept_name,))
    dept_id = cursor_human.fetchone()[0]
    cursor_payroll.execute("INSERT INTO departments (department_id, department_name) VALUES (%s, %s)",
                         (dept_id, dept_name))
    departments.append(dept_id)

# Tạo Applicants và Employees
applicants = []
employees = []
for _ in range(30):
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = f"{first_name.lower()}.{last_name.lower()}@company.com"
    phone = fake.phone_number()[:15]
    app_date = datetime.now() - timedelta(days=random.randint(1, 365))
    status = random.choice(["Pending", "Interviewing", "Hired", "Rejected"])
    job_id = random.choice(jobs)
    
    cursor_human.execute("""
        INSERT INTO Applicants (FirstName, LastName, Email, Phone, ApplicationDate, Status, JobID) 
        OUTPUT INSERTED.ApplicantID 
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (first_name, last_name, email, phone, app_date, status, job_id))
    applicant_id = cursor_human.fetchone()[0]
    applicants.append(applicant_id)
    
    # Tạo Employees cho 20 applicants đầu tiên
    if len(employees) < 20:
        hire_date = datetime.now() - timedelta(days=random.randint(30, 1000))
        dept_id = random.choice(departments)
        salary = round(random.uniform(3000, 15000), 2)
        emp_status = random.choice(["Active", "Inactive"])
        
        cursor_human.execute("""
            INSERT INTO Employees (ApplicantID, DepartmentID, HireDate, Salary, Status) 
            OUTPUT INSERTED.EmployeeID 
            VALUES (?, ?, ?, ?, ?)""",
            (applicant_id, dept_id, hire_date, salary, emp_status))
        emp_id = cursor_human.fetchone()[0]
        
        # Đồng bộ sang MySQL (payroll)
        cursor_payroll.execute("""
            INSERT INTO employees (employee_id, first_name, last_name, email, phone, hire_date, department_id, job_id, salary, status) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
            first_name=%s, last_name=%s, email=%s, phone=%s, hire_date=%s, department_id=%s, job_id=%s, salary=%s, status=%s""",
            (emp_id, first_name, last_name, email, phone, hire_date, dept_id, job_id, salary, emp_status,
             first_name, last_name, email, phone, hire_date, dept_id, job_id, salary, emp_status))
        
        employees.append(emp_id)

# Tạo dữ liệu cho bảng account
# Lấy danh sách nhân viên từ bảng employees trong database payroll (MySQL)
cursor_payroll.execute("SELECT employee_id, first_name, last_name FROM employees")
employee_data = cursor_payroll.fetchall()

# Tạo dữ liệu cho bảng account và thêm vào cả HUMAN_2025 và user
for emp in employee_data:
    emp_id, first_name, last_name = emp
    username = f"{first_name}{emp_id}"  # Tạo username theo định dạng first_name + employee_id
    password_hash = "000000"  # Mật khẩu mặc định
    employee_name = f"{first_name} {last_name}"
    role_name = "employee"
    
    # Thêm vào SQL Server (HUMAN_2025)
    cursor_human.execute("""
        INSERT INTO account (username, password_hash, employee_id, employee_name, role_name) 
        VALUES (?, ?, ?, ?, ?)""",
        (username, password_hash, emp_id, employee_name, role_name))
    
    # Thêm vào MySQL (database user, không phải payroll)
    cursor_user.execute("""
        INSERT INTO account (username, password_hash, employee_id, employee_name, role_name) 
        VALUES (%s, %s, %s, %s, %s)""",
        (username, password_hash, emp_id, employee_name, role_name))

# Tạo Payroll
for emp_id in employees:
    for _ in range(3):  # 3 bản ghi payroll cho mỗi nhân viên
        pay_date = datetime.now() - timedelta(days=random.randint(1, 90))
        base_salary = round(random.uniform(3000, 15000), 2)
        bonus = round(random.uniform(0, 5000), 2)
        deductions = round(random.uniform(0, 1000), 2)
        
        cursor_human.execute("""
            INSERT INTO Payroll (EmployeeID, PayDate, BaseSalary, Bonus, Deductions) 
            VALUES (?, ?, ?, ?, ?)""",
            (emp_id, pay_date, base_salary, bonus, deductions))
        
        cursor_payroll.execute("""
            INSERT INTO payroll (employee_id, pay_date, base_salary, bonus, deductions, net_salary) 
            VALUES (%s, %s, %s, %s, %s, %s)""",
            (emp_id, pay_date, base_salary, bonus, deductions, base_salary + bonus - deductions))

# Tạo Attendance
for emp_id in employees:
    for _ in range(20):
        work_date = datetime.now() - timedelta(days=random.randint(1, 60))
        status = random.choice(["present", "absent", "leave"])
        cursor_payroll.execute("""
            INSERT INTO attendance (employee_id, date, status) 
            VALUES (%s, %s, %s)""",
            (emp_id, work_date, status))

# Tạo Shareholders
shareholders = []
for _ in range(10):
    full_name = fake.first_name()
    unique_num = random.randint(1000, 9999)  # Thêm số ngẫu nhiên
    email = f"{first_name.lower()}.{last_name.lower()}{unique_num}@shareholder.com"
    phone = fake.phone_number()[:15]
    investment = round(random.uniform(10000, 1000000), 2)
    is_employee = random.choice([0, 1])
    emp_id = random.choice(employees) if is_employee else None
    
    cursor_human.execute("""
        INSERT INTO Shareholders (FullName, Email, Phone, InvestmentAmount, IsEmployee, EmployeeID) 
        OUTPUT INSERTED.ShareholderID 
        VALUES (?, ?, ?, ?, ?, ?)""",
        (full_name, email, phone, investment, is_employee, emp_id))
    shareholder_id = cursor_human.fetchone()[0]
    shareholders.append(shareholder_id)

# Tạo Dividends
for shareholder_id in shareholders:
    for _ in range(2):  # 2 lần chia cổ tức
        div_amount = round(random.uniform(1000, 50000), 2)
        pay_date = datetime.now() - timedelta(days=random.randint(1, 180))
        cursor_human.execute("""
            INSERT INTO Dividends (ShareholderID, DividendAmount, PaymentDate) 
            VALUES (?, ?, ?)""",
            (shareholder_id, div_amount, pay_date))

# Commit tất cả thay đổi
conn_human.commit()
conn_payroll.commit()
conn_user.commit()

# Đóng kết nối
cursor_human.close()
conn_human.close()
cursor_payroll.close()
conn_payroll.close()
cursor_user.close()
conn_user.close()

print("✅ Dữ liệu đã được tạo thành công với đầy đủ thông tin và liên kết giữa các database!")