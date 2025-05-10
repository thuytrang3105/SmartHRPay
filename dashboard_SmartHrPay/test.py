from flask import Flask, render_template, request, jsonify, redirect , url_for ,session, flash
from functools import wraps
from module  import db, Account, AccountGroup,Attendance , Group ,Employee, Department, Job, Payroll , HumanEmployee, HumanPayroll, HumanDepartment, HumanJob, Shareholder , Applicant, Dividend
import config
from datetime import date, datetime,  timedelta
import json
from werkzeug.security import check_password_hash
from sqlalchemy import extract, func
import bcrypt
import traceback
import os 
from sqlalchemy.exc import NoReferencedColumnError, IntegrityError
import logging

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

app = Flask(__name__)
DATA_FILE = "data.json"

# Cấu hình database (đảm bảo đã cấu hình đúng trong ứng dụng Flask của bạn)
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQL_SERVER_CONN  # Set the primary database to the SQL Server database

app.config["SQLALCHEMY_BINDS"] = {
    "human": config.SQL_SERVER_CONN,
    "payroll": config.MYSQL_CONN_PAYROLL,
    "user_HRpay":config.MYSQL_CONN_USER_HrPay
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SECRET_KEY'] = os.urandom(24)

# Khởi tạo db với ứng dụng Flask
db.init_app(app)

# HR ROUTES

# Các API mới cho quản lý nhân viên
@app.route('/employees', methods=['GET'])
def employee_hr():
    try:
        employees = HumanEmployee.query.all()
        employees_data = []
        for emp in employees:
            applicant = Applicant.query.get(emp.ApplicantID)
            department = HumanDepartment.query.get(emp.DepartmentID)
            job = HumanJob.query.get(applicant.JobID) if applicant else None
            payroll = HumanPayroll.query.filter_by(EmployeeID=emp.EmployeeID).order_by(HumanPayroll.PayDate.desc()).first()

            if not applicant or not department:
                continue

            employee_data = {
                'employee_id': emp.EmployeeID,
                'first_name': applicant.FirstName,
                'last_name': applicant.LastName,
                'full_name': f"{applicant.LastName} {applicant.FirstName}",
                'email': applicant.Email,
                'phone': applicant.Phone,
                'hire_date': emp.HireDate.strftime('%Y-%m-%d') if emp.HireDate else None,
                'department_id': emp.DepartmentID,
                'department_name': department.DepartmentName if department else None,
                'job_id': applicant.JobID if applicant else None,
                'job_title': job.JobTitle if job else None,
                'base_salary': float(emp.Salary) if emp.Salary else 0.0,
                'status': emp.Status,
                'bonus': float(payroll.Bonus) if payroll and payroll.Bonus else 0.0,
                'deductions': float(payroll.Deductions) if payroll and payroll.Deductions else 0.0
            }
            employees_data.append(employee_data)
        return render_template('employee_HR.html', employees=employees_data)
    except Exception as e:
        logger.error(f"Error in /employees GET: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/employees', methods=['POST'])
def add_employee():
    try:
        data = request.form
        required_fields = ['first_name', 'last_name', 'email', 'hire_date', 'job_title', 'department_name', 'base_salary']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Check if email already exists
        existing_applicant = Applicant.query.filter_by(Email=data['email']).first()
        if existing_applicant:
            return jsonify({"error": "Email already exists"}), 409

        # Find or create department
        department = HumanDepartment.query.filter_by(DepartmentName=data['department_name']).first()
        if not department:
            department = HumanDepartment(DepartmentName=data['department_name'])
            db.session.add(department)
            db.session.flush()

        # Find or create job
        job = HumanJob.query.filter_by(JobTitle=data['job_title']).first()
        if not job:
            job = HumanJob(JobTitle=data['job_title'])
            db.session.add(job)
            db.session.flush()

        # Create new applicant
        new_applicant = Applicant(
            FirstName=data['first_name'],
            LastName=data['last_name'],
            Email=data['email'],
            Phone=data.get('phone', ''),
            ApplicationDate=datetime.strptime(data['hire_date'], '%Y-%m-%d'),
            Status="Hired",
            JobID=job.JobID
        )
        db.session.add(new_applicant)
        db.session.flush()

        # Create new employee
        new_employee = HumanEmployee(
            ApplicantID=new_applicant.ApplicantID,
            DepartmentID=department.DepartmentID,
            HireDate=datetime.strptime(data['hire_date'], '%Y-%m-%d'),
            Salary=float(data['base_salary']),
            Status=data.get('status', 'Active')
        )
        db.session.add(new_employee)
        db.session.commit()

        return redirect(url_for('get_employees'))
    except Exception as e:
        logger.error(f"Error in /employees POST: {str(e)}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/employees/<int:id>', methods=['GET'])
def get_employee(id):
    try:
        employee = HumanEmployee.query.get(id)
        if not employee:
            return jsonify({"error": "Employee not found"}), 404

        applicant = Applicant.query.get(employee.ApplicantID)
        department = HumanDepartment.query.get(employee.DepartmentID)
        job = HumanJob.query.get(applicant.JobID) if applicant else None
        payroll = HumanPayroll.query.filter_by(EmployeeID=employee.EmployeeID).order_by(HumanPayroll.PayDate.desc()).first()

        if not applicant or not department:
            return jsonify({"error": "Related data not found"}), 404

        employee_data = {
            'employee_id': employee.EmployeeID,
            'first_name': applicant.FirstName,
            'last_name': applicant.LastName,
            'full_name': f"{applicant.LastName} {applicant.FirstName}",
            'email': applicant.Email,
            'phone': applicant.Phone,
            'hire_date': employee.HireDate.strftime('%Y-%m-%d') if employee.HireDate else None,
            'department_id': employee.DepartmentID,
            'department_name': department.DepartmentName if department else None,
            'job_id': applicant.JobID if applicant else None,
            'job_title': job.JobTitle if job else None,
            'base_salary': float(employee.Salary) if employee.Salary else 0.0,
            'status': employee.Status,
            'bonus': float(payroll.Bonus) if payroll and payroll.Bonus else 0.0,
            'deductions': float(payroll.Deductions) if payroll and payroll.Deductions else 0.0
        }
        return jsonify(employee_data)
    except Exception as e:
        logger.error(f"Error in /employees/<id> GET: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/employees/<int:id>', methods=['DELETE'])
def delete_employee(id):
    try:
        employee = HumanEmployee.query.get(id)
        if not employee:
            return jsonify({"error": "Employee not found"}), 404

        applicant = Applicant.query.get(employee.ApplicantID)
        if applicant:
            db.session.delete(applicant)
        db.session.delete(employee)
        db.session.commit()
        return redirect(url_for('get_employees'))
    except Exception as e:
        logger.error(f"Error in /employees/<id> DELETE: {str(e)}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
 
#recruitments
   
# Đường dẫn tới file JSON
JSON_FILE = "data/recruitments.json"

# Hàm đọc dữ liệu từ file JSON
def load_recruitments():
    try:
        if os.path.exists(JSON_FILE):
            with open(JSON_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Error reading {JSON_FILE}: {e}")
        return []

# Hàm ghi dữ liệu vào file JSON
def save_recruitments(recruitments):
    try:
        with open(JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(recruitments, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error writing to {JSON_FILE}: {e}")

# Đọc dữ liệu ban đầu
recruitments = load_recruitments()

@app.route('/recruitments')
def recruitment_HR():
    return render_template('recruitment_HR.html')

# API: Lấy danh sách tất cả vị trí tuyển dụng
@app.route('/api/recruitments', methods=['GET'])
def get_recruitments():
    return jsonify(recruitments)

# API: Lấy thông tin chi tiết một vị trí tuyển dụng
@app.route('/api/recruitments/<int:id>', methods=['GET'])
def get_recruitment(id):
    recruitment = next((r for r in recruitments if r['id'] == id), None)
    if recruitment:
        return jsonify(recruitment)
    return jsonify({"error": "Recruitment not found"}), 404

# API: Thêm vị trí tuyển dụng mới
@app.route('/api/recruitments', methods=['POST'])
def add_recruitment():
    global recruitments
    data = request.get_json()
    new_recruitment = {
        "id": max([r['id'] for r in recruitments], default=0) + 1,
        "title": data.get('title'),
        "department": data.get('department'),
        "posted_date": data.get('posted_date'),
        "status": data.get('status'),
        "description": data.get('description'),
        "requirements": data.get('requirements'),
        "applicants": data.get('applicants', [])
    }
    recruitments.append(new_recruitment)
    save_recruitments(recruitments)
    return jsonify(new_recruitment), 201

# API: Cập nhật vị trí tuyển dụng
@app.route('/api/recruitments/<int:id>', methods=['PUT'])
def update_recruitment(id):
    global recruitments
    data = request.get_json()
    recruitment = next((r for r in recruitments if r['id'] == id), None)
    if recruitment:
        recruitment.update({
            "title": data.get('title', recruitment['title']),
            "department": data.get('department', recruitment['department']),
            "posted_date": data.get('posted_date', recruitment['posted_date']),
            "status": data.get('status', recruitment['status']),
            "description": data.get('description', recruitment['description']),
            "requirements": data.get('requirements', recruitment['requirements']),
            "applicants": data.get('applicants', recruitment['applicants'])
        })
        save_recruitments(recruitments)
        return jsonify(recruitment)
    return jsonify({"error": "Recruitment not found"}), 404

# API: Xóa vị trí tuyển dụng
@app.route('/api/recruitments/<int:id>', methods=['DELETE'])
def delete_recruitment(id):
    global recruitments
    recruitment = next((r for r in recruitments if r['id'] == id), None)
    if recruitment:
        recruitments = [r for r in recruitments if r['id'] != id]
        save_recruitments(recruitments)
        return jsonify({"message": "Recruitment deleted"})
    return jsonify({"error": "Recruitment not found"}), 404   
    
if __name__ == '__main__':
    app.run(debug=True)
