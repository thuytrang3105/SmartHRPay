from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Employee Model (Payroll DB) - Không sửa
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

# Department Model (Payroll DB) - Không sửa
class Department(db.Model):
    __bind_key__ = 'payroll'
    __tablename__ = 'departments'
    department_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    department_name = db.Column(db.String(255), nullable=False)
    manager_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'))

# Payroll Model (Payroll DB) - Không sửa
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

# Attendance Model (Payroll DB) - Không sửa
class Attendance(db.Model):
    __bind_key__ = 'payroll'
    __tablename__ = 'attendance'
    attendance_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum('present', 'absent', 'leave'), nullable=False)

# Job Model (Payroll DB) - Không sửa
class Job(db.Model):
    __bind_key__ = 'payroll'
    __tablename__ = 'jobs'
    job_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    job_title = db.Column(db.String(255), nullable=False)
    min_salary = db.Column(db.Numeric(10, 2))
    max_salary = db.Column(db.Numeric(10, 2))

# Applicant Model (Human DB) - Cập nhật
class Applicant(db.Model):
    __bind_key__ = 'human'
    __tablename__ = 'Applicants'
    ApplicantID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    FirstName = db.Column(db.String(50), nullable=False)
    LastName = db.Column(db.String(50), nullable=False)
    Email = db.Column(db.String(100), unique=True, nullable=False)
    Phone = db.Column(db.String(15))
    ApplicationDate = db.Column(db.Date, nullable=False)
    Status = db.Column(db.String(20), nullable=False, default='Pending')
    JobID = db.Column(db.Integer, db.ForeignKey('Jobs.JobID'))

# Employee Model (Human DB) - Cập nhật
class HumanEmployee(db.Model):
    __bind_key__ = 'human'
    __tablename__ = 'Employees'
    EmployeeID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ApplicantID = db.Column(db.Integer, db.ForeignKey('Applicants.ApplicantID'), unique=True, nullable=False)
    DepartmentID = db.Column(db.Integer, db.ForeignKey('Departments.DepartmentID'), nullable=False)
    HireDate = db.Column(db.Date, nullable=False)
    Salary = db.Column(db.Numeric(18, 2), nullable=False)
    Status = db.Column(db.String(20), nullable=False, default='Active')

# Department Model (Human DB) - Cập nhật
class HumanDepartment(db.Model):
    __bind_key__ = 'human'
    __tablename__ = 'Departments'
    DepartmentID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    DepartmentName = db.Column(db.String(100), nullable=False)
    ManagerID = db.Column(db.Integer, db.ForeignKey('Employees.EmployeeID'))

# Payroll Model (Human DB) - Cập nhật
class HumanPayroll(db.Model):
    __bind_key__ = 'human'
    __tablename__ = 'Payroll'
    PayrollID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    EmployeeID = db.Column(db.Integer, db.ForeignKey('Employees.EmployeeID'), nullable=False)
    PayDate = db.Column(db.Date, nullable=False)
    BaseSalary = db.Column(db.Numeric(18, 2), nullable=False)
    Bonus = db.Column(db.Numeric(18, 2), nullable=True, default=0)
    Deductions = db.Column(db.Numeric(18, 2), nullable=True, default=0)

# Shareholders Model (Human DB) - Cập nhật
class Shareholder(db.Model):
    __bind_key__ = 'human'
    __tablename__ = 'Shareholders'
    ShareholderID = db.Column(db.Integer, primary_key=True)
    FullName = db.Column(db.String(100), nullable=False)
    Email = db.Column(db.String(100), unique=True, nullable=False)
    Phone = db.Column(db.String(15))
    Address = db.Column(db.String(255))
    IsEmployee = db.Column(db.Boolean, default=False)
    EmployeeID = db.Column(db.Integer, db.ForeignKey('Employees.EmployeeID'), nullable=True)
    InvestmentAmount = db.Column(db.Numeric(18, 2))

# Dividends Model (Human DB) - Cập nhật
class Dividend(db.Model):
    __bind_key__ = 'human'
    __tablename__ = 'Dividends'
    DividendID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ShareholderID = db.Column(db.Integer, db.ForeignKey('Shareholders.ShareholderID'), nullable=False)
    DividendAmount = db.Column(db.Numeric(18, 2), nullable=False)
    PaymentDate = db.Column(db.Date, nullable=False)

# Job Model (Human DB) - Cập nhật
class HumanJob(db.Model):
    __bind_key__ = 'human'
    __tablename__ = 'Jobs'
    JobID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    JobTitle = db.Column(db.String(255), nullable=False)
    MinSalary = db.Column(db.Numeric(18, 2))
    MaxSalary = db.Column(db.Numeric(18, 2))

# Account Model (User HRPay DB) - Không sửa
class Account(db.Model):
    __bind_key__ = 'user_HRpay'
    __tablename__ = 'Account'
    AccountID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Username = db.Column(db.String(50), unique=True, nullable=False)
    PasswordHash = db.Column(db.String(100), nullable=False)
    FullName = db.Column(db.String(100), nullable=False)
    Email = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    employee_id = db.Column(db.Integer)

# Group Model (User HRPay DB) - Không sửa
class Group(db.Model):
    __bind_key__ = 'user_HRpay'
    __tablename__ = 'Group'
    GroupID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    GroupName = db.Column(db.String(50), nullable=False)
    Description = db.Column(db.String(255))

# Account_Group Model (User HRPay DB) - Không sửa
class AccountGroup(db.Model):
    __bind_key__ = 'user_HRpay'
    __tablename__ = 'Account_Group'
    AccountID = db.Column(db.Integer, db.ForeignKey('Account.AccountID'), primary_key=True)
    GroupID = db.Column(db.Integer, db.ForeignKey('Group.GroupID'), primary_key=True)
    Account_S = db.relationship('Account', backref='account_groups')
    Group = db.relationship('Group', backref='account_groups')

# Module Model (User HRPay DB) - Không sửa
class Module(db.Model):
    __bind_key__ = 'user_HRpay'
    __tablename__ = 'Module'
    ModuleID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ModuleName = db.Column(db.String(100), nullable=False)
    Description = db.Column(db.String(255))

# Function Model (User HRPay DB) - Không sửa
class Function(db.Model):
    __bind_key__ = 'user_HRpay'
    __tablename__ = 'Function'
    FunctionID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    FunctionName = db.Column(db.String(50), nullable=False)
    Description = db.Column(db.String(255))

# Function_Module Model (User HRPay DB) - Không sửa
class FunctionModule(db.Model):
    __bind_key__ = 'user_HRpay'
    __tablename__ = 'Function_Module'
    FunctionModuleID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    FunctionID = db.Column(db.Integer, db.ForeignKey('Function.FunctionID'), nullable=False)
    ModuleID = db.Column(db.Integer, db.ForeignKey('Module.ModuleID'), nullable=False)
    Function = db.relationship('Function', backref='function_modules')
    Module = db.relationship('Module', backref='function_modules')

# Permission Model (User HRPay DB) - Không sửa
class Permission(db.Model):
    __bind_key__ = 'user_HRpay'
    __tablename__ = 'Permission'
    PermissionID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    GroupID = db.Column(db.Integer, db.ForeignKey('Group.GroupID'), nullable=False)
    FunctionModuleID = db.Column(db.Integer, db.ForeignKey('Function_Module.FunctionModuleID'), nullable=False)
    IsAllowed = db.Column(db.Boolean, nullable=False)
    Group = db.relationship('Group', backref='permissions')
    FunctionModule = db.relationship('FunctionModule', backref='permissions')