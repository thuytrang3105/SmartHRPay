# model.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Employee Model (Payroll DB)
class Employee(db.Model):
    __bind_key__ = 'payroll'
    __tablename__ = 'employees'
    employee_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone = db.Column(db.String(255))
    hire_date = db.Column(db.Date)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.department_id'))
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.job_id'))
    salary = db.Column(db.Numeric(10, 2))
    status = db.Column(db.Enum('active', 'inactive'), nullable=False)

# Department Model (Payroll DB)
class Department(db.Model):
    __bind_key__ = 'payroll'
    __tablename__ = 'departments'
    department_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    department_name = db.Column(db.String(255), nullable=False)
    manager_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'))

# Payroll Model (Payroll DB)
class Payroll(db.Model):
    __bind_key__ = 'payroll'
    __tablename__ = 'payroll'
    payroll_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'), nullable=False)
    pay_date = db.Column(db.Date, nullable=False)
    base_salary = db.Column(db.Numeric(10, 2))
    bonus = db.Column(db.Numeric(10, 2))
    deductions = db.Column(db.Numeric(10, 2))
    net_salary = db.Column(db.Numeric(10, 2))

# Attendance Model (Payroll DB)
class Attendance(db.Model):
    __bind_key__ = 'payroll'
    __tablename__ = 'attendance'
    attendance_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum('present', 'absent', 'leave'), nullable=False)

# Job Model (Payroll DB)
class Job(db.Model):
    __bind_key__ = 'payroll'
    __tablename__ = 'jobs'
    job_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    job_title = db.Column(db.String(255), nullable=False)
    min_salary = db.Column(db.Numeric(10, 2))
    max_salary = db.Column(db.Numeric(10, 2))

# Applicant Model (Human DB)
class Applicant(db.Model):
    __bind_key__ = 'human'
    __tablename__ = 'Applicants'
    applicant_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone_number = db.Column(db.String(15))
    application_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending')
    job_id = db.Column(db.Integer, db.ForeignKey('Jobs.JobID'))

# Employee Model (Human DB)
class HumanEmployee(db.Model):
    __bind_key__ = 'human'
    __tablename__ = 'Employees'
    employee_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    applicant_id = db.Column(db.Integer, db.ForeignKey('Applicants.ApplicantID'), unique=True, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('Departments.DepartmentID'), nullable=False)
    hire_date = db.Column(db.Date, nullable=False)
    salary = db.Column(db.Numeric(18, 2), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Active')

# Department Model (Human DB)
class HumanDepartment(db.Model):
    __bind_key__ = 'human'
    __tablename__ = 'Departments'
    department_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    department_name = db.Column(db.String(100), nullable=False)
    manager_id = db.Column(db.Integer, db.ForeignKey('Employees.EmployeeID'))

# Payroll Model (Human DB)
class HumanPayroll(db.Model):
    __bind_key__ = 'human'
    __tablename__ = 'Payroll'
    PayrollID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    EmployeeID = db.Column(db.Integer, db.ForeignKey('Employees.EmployeeID'), nullable=False)
    PayDate = db.Column(db.Date, nullable=False)
    BaseSalary = db.Column(db.Numeric(18, 2), nullable=False)
    Bonus = db.Column(db.Numeric(18, 2), nullable=True, default=0)
    Deductions = db.Column(db.Numeric(18, 2), nullable=True, default=0)

# Shareholders Model (Human DB)
class Shareholder(db.Model):
    __bind_key__ = 'human'
    __tablename__ = 'Shareholders'
    shareholder_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone_number = db.Column(db.String(15))
    investment_amount = db.Column(db.Numeric(18, 2))
    is_employee = db.Column(db.Boolean, default=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('Employees.EmployeeID'), nullable=True)

# Dividends Model (Human DB)
class Dividend(db.Model):
    __bind_key__ = 'human'
    __tablename__ = 'Dividends'
    dividend_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    shareholder_id = db.Column(db.Integer, db.ForeignKey('Shareholders.ShareholderID'), nullable=False)
    dividend_amount = db.Column(db.Numeric(18, 2), nullable=False)
    payment_date = db.Column(db.Date, nullable=False)

# Job Model (Human DB)
class HumanJob(db.Model):
    __bind_key__ = 'human'
    __tablename__ = 'Jobs'
    job_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    job_title = db.Column(db.String(255), nullable=False)
    min_salary = db.Column(db.Numeric(18, 2))
    max_salary = db.Column(db.Numeric(18, 2))

# Account Model (User DB) - Chỉ có trong database user
class UserAccount(db.Model):
    __bind_key__ = 'user'
    __tablename__ = 'account'
    account_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    employee_id = db.Column(db.Integer, nullable=False)
    employee_name = db.Column(db.String(100), nullable=False)
    role_name = db.Column(db.String(50), nullable=False)