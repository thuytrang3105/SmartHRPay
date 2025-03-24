import pyodbc
import random
from faker import Faker
from datetime import datetime, timedelta
import mysql.connector

fake = Faker()

# Thông tin kết nối SQL Server (HUMAN_2025)
DB_HUMAN = {
    'server': '.',  # Hoặc 'localhost' nếu chạy cục bộ
    'database': 'HUMAN_2025'
}

# Thông tin kết nối MySQL (payroll)
DB_PAYROLL = {
    'host': 'localhost',
    'database': 'payroll',
    'user': 'root',
    'password': '123456123456'
}

# Kết nối đến SQL Server (HUMAN_2025) - Windows Authentication
conn_human = pyodbc.connect(
    f"DRIVER={{SQL Server}};"
    f"SERVER={DB_HUMAN['server']};"
    f"DATABASE={DB_HUMAN['database']};"
    "Trusted_Connection=yes;"
)
cursor_human = conn_human.cursor()

# Kết nối đến MySQL (payroll)
conn_payroll = mysql.connector.connect(
    host=DB_PAYROLL['host'],
    user=DB_PAYROLL['user'],
    password=DB_PAYROLL['password'],
    database=DB_PAYROLL['database']
)
cursor_payroll = conn_payroll.cursor()

print("Kết nối thành công!")

# 1️⃣ Tạo dữ liệu bảng Jobs (Chức vụ) trong Human
jobs = []
for _ in range(10):
    job_title = fake.job()
    min_salary = round(random.uniform(300, 2000), 2)
    max_salary = min_salary + round(random.uniform(1000, 5000), 2)
    
    cursor_human.execute("INSERT INTO jobs (jobtitle, minsalary, maxsalary) OUTPUT INSERTED.jobid VALUES (?, ?, ?)",
                         (job_title, min_salary, max_salary))
    job_id = cursor_human.fetchone()[0]
    jobs.append(job_id)
conn_human.commit()

# 2️⃣ Tạo dữ liệu bảng Departments (Phòng ban) trong Human
departments = []
for _ in range(5):
    department_name = fake.company()
    cursor_human.execute("INSERT INTO departments (departmentname) OUTPUT INSERTED.departmentid VALUES (?)", (department_name,))
    department_id = cursor_human.fetchone()[0]
    departments.append(department_id)
conn_human.commit()

# 3️⃣ Tạo dữ liệu bảng Applicants (Ứng viên)
applicants = []
for _ in range(30):
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = f"{first_name.lower()}.{last_name.lower()}{_}@company.com"
    phone = fake.phone_number()[:15]
    application_date = datetime.now() - timedelta(days=random.randint(1, 365))
    status = random.choice(["Pending", "Interviewing", "Hired", "Rejected"])
    job_id = random.choice(jobs) if jobs else None
    
    if job_id:
        cursor_human.execute("INSERT INTO applicants (firstname, lastname, email, phone, applicationdate, status, jobid) OUTPUT INSERTED.applicantid VALUES (?, ?, ?, ?, ?, ?, ?)",
                             (first_name, last_name, email, phone, application_date, status, job_id))
        applicant_id = cursor_human.fetchone()[0]
        applicants.append(applicant_id)
conn_human.commit()

# 4️⃣ Tạo dữ liệu bảng Employees (Nhân viên)
employees = []
for applicant_id in applicants[:20]:  # Chỉ tuyển 20 người
    hire_date = datetime.now() - timedelta(days=random.randint(30, 1000))
    department_id = random.choice(departments)
    salary = round(random.uniform(2000, 10000), 2)
    status = random.choice(["Active", "Inactive"])

    cursor_human.execute("INSERT INTO employees (applicantid, departmentid, hiredate, salary, status) OUTPUT INSERTED.employeeid VALUES (?, ?, ?, ?, ?)",
                         (applicant_id, department_id, hire_date, salary, status))
    employee_id = cursor_human.fetchone()[0]
    employees.append(employee_id)
conn_human.commit()

# Đồng bộ nhân viên từ HUMAN_2025 sang payroll trước khi thêm dữ liệu payroll
for emp_id in employees:
    cursor_payroll.execute("INSERT INTO employees (employee_id) VALUES (%s) ON DUPLICATE KEY UPDATE employee_id=employee_id", (emp_id,))
conn_payroll.commit()

# 5️⃣ Tạo dữ liệu bảng Payroll trong Payroll DB
for emp_id in employees:
    pay_date = datetime.now() - timedelta(days=random.randint(1, 30))
    base_salary = round(random.uniform(2000, 10000), 2)
    bonus = round(random.uniform(0, 2000), 2)
    deductions = round(random.uniform(0, 500), 2)
    net_salary = base_salary + bonus - deductions

    cursor_payroll.execute("INSERT INTO payroll (employee_id, pay_date, base_salary, bonus, deductions, net_salary) VALUES (%s, %s, %s, %s, %s, %s)", 
                           (emp_id, pay_date, base_salary, bonus, deductions, net_salary))

# 6️⃣ Tạo dữ liệu bảng Attendance (Chấm công)
for emp_id in employees:
    for _ in range(20):
        work_date = datetime.now() - timedelta(days=random.randint(1, 60))
        status = random.choice(["present", "absent", "leave"])
        cursor_payroll.execute("INSERT INTO attendance (employee_id, date, status) VALUES (%s, %s, %s)", 
                               (emp_id, work_date, status))
conn_payroll.commit()

# 7️⃣ Đồng bộ bảng Departments & Jobs giữa hai database
# Lấy danh sách departments từ SQL Server
cursor_human.execute("SELECT departmentid, departmentname FROM departments")
departments_human = cursor_human.fetchall()

# Chèn dữ liệu vào MySQL (payroll)
for dep_id, dep_name in departments_human:
    cursor_payroll.execute("INSERT INTO departments (department_id, department_name) VALUES (%s, %s) ON DUPLICATE KEY UPDATE department_name=%s",
                           (dep_id, dep_name, dep_name))

conn_payroll.commit()


# Đóng kết nối
cursor_human.close()
conn_human.close()
cursor_payroll.close()
conn_payroll.close()

print("✅ Dữ liệu đã được tạo thành công với đầy đủ liên kết giữa hai database!")