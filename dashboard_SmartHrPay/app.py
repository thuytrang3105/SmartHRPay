from flask import Flask, render_template, request, jsonify, redirect , url_for ,session, flash
from functools import wraps
from module  import db, Account, AccountGroup,Attendance , Group ,Employee, Department, Job, Payroll , HumanEmployee, HumanPayroll, HumanDepartment, HumanJob, Shareholder , Applicant, Dividend, Group, Permission, Function, Module, FunctionModule
import config
from datetime import  datetime,  timedelta
import json
from sqlalchemy import extract, func, or_
import bcrypt
import traceback
import os 
from sqlalchemy.exc import NoReferencedColumnError, IntegrityError
import logging

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

app = Flask(__name__)

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

atc=""

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if 'permission' not in session or session['permission'] not in roles:
                flash("Bạn không có quyền truy cập.")
                return redirect(url_for('home'))
            return f(*args, **kwargs)
        return wrapper
    return decorator

@app.route('/login', methods=['POST'])
def login():
    email_or_username = request.form.get('email')
    password = request.form.get('password')

    # Truy vấn người dùng theo Email hoặc Username chỉ từ bảng Account
    user = db.session.query(Account).filter(
        (Account.Username == email_or_username) | (Account.Email == email_or_username)
    ).first()

    # Kiểm tra người dùng và mật khẩu
    if user and user.PasswordHash and bcrypt.checkpw(password.encode(), user.PasswordHash.encode()):
        # Lưu thông tin vào session
        session['user_id'] = user.employee_id
        session['username'] = user.Username
        session['full_name'] = user.FullName
        session['permission'] = user.role or 'employee'  # Sử dụng role từ cột role trong Account
        session['session_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"Session after login: {session}")
        session["atc"] = session.get("atc", "") + " Đăng nhập"
        return redirect(url_for('home'))

    # Nếu thông tin đăng nhập sai
    flash("Sai thông tin đăng nhập hoặc tài khoản không hợp lệ.")
    return redirect(url_for('home'))

@app.route("/")
def home():
    user_id = session.get('user_id')
    username = session.get('username')
    full_name = session.get('full_name')
    role = session.get('permission')
    session_time = session.get('session_time')

    return render_template(
        'home.html',
        user_id=user_id,
        username=username,
        full_name=full_name,
        role=role,
        session_time=session_time
    )

@app.route('/logout', methods=['GET'])
def logout():
    # Đọc dữ liệu hiện tại
    activity_data = r_activity_history()
    
    # Tạo bản ghi đăng xuất
    data = {
        "time": session.get('session_time'),
        "user": session.get('full_name'),
        "role": session.get('permission'),
        "action": session.get('atc', '') + ", Đăng xuất"
    }
    
    # Thêm bản ghi vào activity_logs
    activity_data["activity_logs"].append(data)
    session["atc"] = ""  # ng # dùng lại
    
    # Ghi lại dữ liệu vào file JSON
    save_activity_history(activity_data)
    
    session.clear()
    flash("Bạn đã đăng xuất thành công.")
    return redirect(url_for('home'))

######################ADMINADMIN###############################################################################
#Phan quyen 
@app.route('/user-authorization')
@role_required('Admin')
def user_authorization():
    # Truy vấn dữ liệu từ bảng Account, ghép với AccountGroup và Group
    users = db.session.query(Account, Group.GroupName)\
        .outerjoin(AccountGroup, Account.AccountID == AccountGroup.AccountID)\
        .outerjoin(Group, AccountGroup.GroupID == Group.GroupID)\
        .all()
    
    # Chuyển đổi dữ liệu thành định dạng phù hợp
    user_list = [
        {
            "user_id": user.Account.AccountID,
            "username": user.Account.Username,
            "role": user.GroupName or "Chưa thuộc nhóm",
            "employee_name": user.Account.FullName
        }
        for user in users
    ] 
    session["atc"] = session.get("atc", "") + ", Xem quyền người dùng"
    # Trả về template HTML với danh sách người dùng
    return render_template('user_authorization.html', users=user_list)
# Cổ đông ##########################################################33
@app.route('/shareholder')
@role_required('Admin')
def shareholder():
    try:
        shareholders = db.session.query(Shareholder).all()
        shareholders_list = [
            {
                "id": shareholder.ShareholderID,
                "FullName": shareholder.FullName,  # Đổi thành full_name
                "Email": shareholder.Email,
                "PhoneNumber": shareholder.Phone,
                "InvestmentAmount": float(shareholder.InvestmentAmount) if shareholder.InvestmentAmount else 0
            }
            for shareholder in shareholders
        ]
        session["atc"] = session.get("atc", "") + ", Xem Cổ đông"
        return render_template('shareholder.html', shareholders=shareholders_list)
    except Exception as e:
        # In ra chi tiết lỗi
        print("Lỗi xảy ra tại:", traceback.format_exc())
        flash(f"Lỗi khi truy xuất danh sách cổ đông: {str(e)}")
        return redirect(url_for('home'))

@app.route('/shareholder/<int:id>')
@role_required('Admin')
def shareholder_detail(id):
    try:
        # Lấy thông tin cổ đông từ cơ sở dữ liệu theo ID
        shareholder = db.session.query(Shareholder).filter_by(ShareholderID=id).first()
        if shareholder:
            # Kiểm tra xem cổ đông có phải là nhân viên không (join với bảng Employee)
            employee = db.session.query(Employee).filter_by(employee_id=shareholder.EmployeeID).first()
            print("cổ đông!!!")
            # Tạo dữ liệu chi tiết cổ đông
            shareholder_data = {
                "id": shareholder.ShareholderID,
                "FullName": shareholder.FullName,  
                "Email": shareholder.Email,
                "PhoneNumber": shareholder.Phone,
                "InvestmentAmount": float(shareholder.InvestmentAmount) if shareholder.InvestmentAmount else 0,
                "IsEmployee": "Có" if employee else "Không",
                "EmployeeID": employee.employee_id if employee else None
            }
            
            print("cổ đông!")
            session["atc"] = session.get("atc", "") + ", Xem Chi tiết Cổ Đông"
            # Trả về trang HTML chi tiết cổ đông
            return render_template('shareholder_detail.html', shareholder=shareholder_data)
        else:
            # Nếu không tìm thấy cổ đông
            flash("Không tìm thấy cổ đông!")
            print("Không tìm thấy cổ đông!")
            return redirect(url_for('shareholder'))
    
    except Exception as e:
        # Xử lý lỗi và hiển thị thông báo
        flash(f"Lỗi khi truy xuất chi tiết cổ đông: {str(e)}")
        return redirect(url_for('shareholder'))
    
# Lich su hoat dong 
@app.route('/activity_history')
@role_required('Admin')
def activity_history():
    with open('data/activity_history.json', encoding='utf-8') as f:
        activity_logs = json.load(f)["activity_logs"]
    session["atc"] = session.get("atc", "") + ", Xem lịch sử hoạt động"
    return render_template('activity_history.html', activity_logs=activity_logs)



######################HRHRHR#######################################################################################
@app.route('/report')
@role_required('Admin', 'Hiring')
def report():
    try:
        current_date = datetime.now()

        # Total active employees
        total_employees = db.session.query(Employee).filter_by(status='active').count()

        # New employees (hired in the last 30 days)
        thirty_days_ago = current_date - timedelta(days=30)
        new_employees = db.session.query(Employee).filter(
            Employee.hire_date >= thirty_days_ago,
            Employee.status == 'active'
        ).count()

        # Resigned employees
        resigned_employees = db.session.query(Employee).filter_by(status='resigned').count()

        # Number of departments
        departments = db.session.query(Department).distinct().count()

        # Department distribution (active employees per department)
        dept_distribution = dict(
            db.session.query(
                Department.department_name,
                func.count(Employee.employee_id)
            )
            .join(Employee, Employee.department_id == Department.department_id)
            .filter(Employee.status == 'active')
            .group_by(Department.department_name)
            .all()
        )
        # Growth data (active employees per month for the last 5 months)
        growth_data = []
        for i in range(5, 0, -1):
            month_start = (current_date.replace(day=1) - timedelta(days=30 * i)).replace(day=1)
            month_end = (month_start + timedelta(days=31)).replace(day=1) - timedelta(days=1)
            monthly_count = db.session.query(Employee).filter(
                Employee.status == 'active',
                Employee.hire_date <= month_end
            ).count() - db.session.query(Employee).filter(
                Employee.status == 'resigned',
                Employee.hire_date <= month_end
            ).count()
            growth_data.append(monthly_count)

        # Prepare data dictionary
        data = {
            "totalEmployees": total_employees,
            "newEmployees": new_employees,
            "resignedEmployees": resigned_employees,
            "departments": departments,
            "deptDistribution": dept_distribution,
            "growthData": growth_data
        }
        session["atc"] = session.get("atc", "") + ", Xem báo cáo nhân sự"
        return render_template('report.html', data=data)
    except Exception as e:
        flash(f"Lỗi khi truy xuất báo cáo: {str(e)}")
        return redirect(url_for('home'))

######################EMPLOYEEEE################################################################################

@app.route('/employee', methods=['GET', 'POST'])
@role_required('Admin', 'Acounting','Hiring','Employee')
def employee():
    employee_id = session.get('user_id')
    print(f"Employee ID from session: {employee_id}")

    # Fetch dữ liệu nhân viên từ cơ sở dữ liệu, liên kết với Department và Job
    employee = db.session.query(Employee, Department.department_name, Job.job_title).\
        join(Department, Employee.department_id == Department.department_id).\
        join(Job, Employee.job_id == Job.job_id).\
        filter(Employee.employee_id == employee_id).first()

    if not employee:
        flash("Chưa đăng nhập hoặc không tìm thấy nhân viên.") 
        return redirect(url_for('home'))  # Nếu không tìm thấy nhân viên

    # Tạo object employee để dễ sử dụng trong template
    employee_data = {
        "employee_id": employee.Employee.employee_id,
        "last_name": employee.Employee.last_name,
        "first_name": employee.Employee.first_name,
        "email": employee.Employee.email,
        "phone": employee.Employee.phone,
        "start_date": employee.Employee.hire_date.strftime("%d/%m/%Y") if employee.Employee.hire_date else "N/A",
        "department_name": employee.department_name,
        "job_title": employee.job_title,
        "status": employee.Employee.status
    }

    # Fetch dữ liệu lương cho nhân viên theo tháng và năm
    selected_month = request.args.get('month', '3')  # Tháng mặc định là tháng 3
    selected_year = request.args.get('year', '2025')  # Năm mặc định là 2025

    # Truy vấn dữ liệu lương
    payroll_data = db.session.query(Payroll).join(Employee).filter(
        extract('month', Payroll.pay_date) == int(selected_month),
        extract('year', Payroll.pay_date) == int(selected_year),
        Employee.employee_id == employee_id,
        Employee.status == 'active'
    ).first()

    if payroll_data:
        salary = {
            "base_salary": str(payroll_data.base_salary),
            "bonus": str(payroll_data.bonus),
            "date": payroll_data.pay_date.day,
            "deductions": str(payroll_data.deductions),
            "net_salary": str(payroll_data.net_salary)
        }
    else:
        salary = {
            "base_salary": "N/A",
            "bonus": "N/A",
            "date": "N/A",
            "deductions": "N/A",
            "net_salary": "N/A"
        }

    # Truy vấn dữ liệu ngày công
    attendance_records = db.session.query(Attendance).join(Employee).filter(
        extract('month', Attendance.date) == int(selected_month),
        extract('year', Attendance.date) == int(selected_year),
        Employee.employee_id == employee_id,
        Employee.status == 'active'
    ).all()

    attendance = [{
        "date": record.date.strftime("%d/%m/%Y"),
        "status": record.status
    } for record in attendance_records] if attendance_records else []

    # Get current year
    current_year = datetime.now().year
    session["atc"] = session.get("atc", "") + ", Xem thông tin cá nhân"
    return render_template("employee.html", 
                           employee=employee_data, 
                           salary=salary, 
                           attendance=attendance, 
                           selected_month=selected_month, 
                           selected_year=selected_year,
                           current_year=current_year)

######################PAYROLLPAYROLL#############################################################################
#home 
@app.route('/Xinchao')
def Xinchao():
    return render_template('Xinchao.html')

#Bangluong 
@app.route('/payroll')
@role_required('Admin', 'Acounting')
def payroll():
    with app.app_context():
        latest_payroll_subquery = db.session.query(
            Payroll.employee_id, db.func.max(Payroll.pay_date).label('latest_date')
        ).group_by(Payroll.employee_id).subquery()

        payroll_query = db.session.query(
            Payroll.payroll_id,
            Employee.employee_id,
            db.func.concat(Employee.first_name, ' ', Employee.last_name).label('employee_name'),
            Department.department_name,
            Job.job_title,
            Payroll.base_salary,
            Payroll.bonus,
            Payroll.deductions,
            Payroll.pay_date
        ).join(
            Employee, Payroll.employee_id == Employee.employee_id
        ).join(
            Department, Employee.department_id == Department.department_id
        ).join(
            Job, Employee.job_id == Job.job_id
        ).join(
            latest_payroll_subquery,
            db.and_(
                Payroll.employee_id == latest_payroll_subquery.c.employee_id,
                Payroll.pay_date == latest_payroll_subquery.c.latest_date
            )
        ).all()

        payroll_data = [
            (
                {"payroll_id": row.payroll_id, "pay_date": row.pay_date},
                {
                    "employee_id": row.employee_id,
                    "id_display": f"NV{row.employee_id:02d}" if isinstance(row.employee_id, int) else "NV" + str(int(row.employee_id.replace("NV", ""))),  
                    "employee_name": row.employee_name,
                    "department_name": row.department_name,
                    "job_title": row.job_title,
                    "base_salary": float(row.base_salary or 0),
                    "bonus": float(row.bonus or 0),
                    "deduction": float(row.deductions or 0),
                    "total_salary": float(row.base_salary or 0) + float(row.bonus or 0) - float(row.deductions or 0)
                }
            )
            for row in payroll_query
        ]
        departments = Department.query.all()
        jobs = Job.query.all()
        session["atc"] = session.get("atc", "") + ", Xem Bảng lương "
    return render_template(
        'payroll.html',
        payroll_data=payroll_data,
        department=departments,
        job=jobs 
    )
    
@app.route('/get_employee_details/<int:employee_id>')
@role_required('Admin', 'Acounting')
def get_employee_details(employee_id):
    latest_payroll_subquery = db.session.query(
        Payroll.employee_id, db.func.max(Payroll.pay_date).label('latest_date')
    ).filter(Payroll.employee_id == employee_id).group_by(Payroll.employee_id).subquery()

    employee_query = db.session.query(
        Employee.employee_id,
        db.func.concat(Employee.first_name, ' ', Employee.last_name).label('employee_name'),
        Department.department_name,
        Job.job_title,
        Payroll.base_salary,
        Payroll.bonus,
        Payroll.deductions
    ).join(
        Department, Employee.department_id == Department.department_id
    ).join(
        Job, Employee.job_id == Job.job_id
    ).outerjoin(
        Payroll, Employee.employee_id == Payroll.employee_id
    ).outerjoin(
        latest_payroll_subquery,
        db.and_(
            Payroll.employee_id == latest_payroll_subquery.c.employee_id,
            Payroll.pay_date == latest_payroll_subquery.c.latest_date
        )
    ).filter(
        Employee.employee_id == employee_id
    ).first()

    if employee_query:
        return jsonify({
            'employee_id': employee_query.employee_id,
            'employee_name': employee_query.employee_name,
            'department_name': employee_query.department_name,
            'job_title': employee_query.job_title,
            'base_salary': float(employee_query.base_salary or 0),
            'bonus': float(employee_query.bonus or 0),
            'deduction': float(employee_query.deductions or 0)
        })
    else:
        return jsonify({'error': 'Không tìm thấy nhân viên'})

# Route để cập nhật thông tin nhân viên
@app.route('/update_employee', methods=['POST'])
def update_employee():
    employee_id = request.form['id']
    employee = Employee.query.get_or_404(employee_id)

    employee.employee_name = request.form['employee_name']
    employee.department_name = request.form['department_name']
    employee.job_title = request.form['job_title']
    employee.base_salary = request.form['base_salary']
    employee.bonus = request.form['bonus']
    employee.deduction = request.form['deduction']
    employee.notes = request.form['notes']

    try:
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

# Route tìm kiếm nhân viên
@app.route('/search_employee', methods=['GET'])
def search_employee():
    search_term = request.args.get('search_term', '').lower()
    
    employees = Employee.query.filter(
        or_(
            Employee.employee_id.ilike(f"%{search_term}%"),
            Employee.employee_name.ilike(f"%{search_term}%"),
            Employee.department_name.ilike(f"%{search_term}%"),
            Employee.job_title.ilike(f"%{search_term}%")
        )
    ).all()
    
    if employees:
        # Trả về thông tin chi tiết của nhân viên tìm được
        return jsonify([
            {
                'employee_id': employee.employee_id,
                'employee_name': employee.employee_name,
                'department_name': employee.department_name,
                'job_title': employee.job_title,
                'base_salary': employee.base_salary,
                'bonus': employee.bonus,
                'deduction': employee.deduction,
                'notes': employee.notes
            }for e in employees
        ])
    else:
        return jsonify({'error': 'Không tìm thấy nhân viên'})
    
#Thongbao ############################################################################

DATA_FILE = "data/notification.json"

def load_notifications():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data.get("notification", [])
    except (FileNotFoundError, json.JSONDecodeError):
            return []
    
def save_notifications(notifications):
    data = {"notification": notifications}
    with open(DATA_FILE, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

@app.route('/save_notification', methods=['POST'])
@role_required('Admin', 'Acounting', 'Hiring')
def save_notification():
    title = request.form.get('title')
    recipients = request.form.get('recipients')
    content = request.form.get('content')
    status = request.form.get('status', 'draft')  
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    new_notification = {
        'title': title,
        'recipients': recipients,
        'content': content,
        'status': status,
        'timestamp': timestamp
    }
    notifications = load_notifications()
    notifications.append(new_notification)
    save_notifications(notifications)
    return redirect(url_for('get_notifications'))


@app.route('/notification')
@role_required('Admin', 'Acounting', 'Hiring', 'Employee')
def get_notifications():
    role = session.get('permission')  # Lấy role từ session

    notifications = load_notifications()

    if role == 'Employee':
        notifications = [
            n for n in notifications 
            if n.get('status', '').strip().lower() == 'sent' and
            n.get('recipients', '').strip().lower() in ['tất cả nhân viên', 'all']
        ]
    session["atc"] = session.get("atc", "") + ", Xem thông báo "
    return render_template('notification.html', notifications=notifications)

 # Chấm công =============================================================
STATUS_MAP = {
    'present': 'Có mặt',
    'absent': 'Vắng',
    'leave': 'Nghỉ'
}
REVERSE_STATUS_MAP = {v: k for k, v in STATUS_MAP.items()}

@app.route('/attendance')
@role_required('Admin', 'Acounting')
def attendance():
    # Find the most recent date with attendance records
    latest_date = db.session.query(func.max(Attendance.date)).scalar()

    if not latest_date:
        # No attendance records found, use current date as fallback
        latest_date = datetime.now().date()
        date_str = latest_date.strftime('%Y-%m-%d')
    else:
        date_str = latest_date.strftime('%Y-%m-%d')

    # Query all active employees, left join with Attendance for the latest date
    employees_with_attendance = (
        db.session.query(
            Attendance.attendance_id,
            Employee.employee_id,
            Employee.first_name,
            Employee.last_name,
            Attendance.date,
            Attendance.status
        )
        .outerjoin(Attendance, (Employee.employee_id == Attendance.employee_id) & (Attendance.date == latest_date))
        .filter(Employee.status == 'active')
        .distinct(Employee.employee_id)  # Ensure no duplicate employees
        .all()
    )


    # Format attendance data for template
    attendance_data = [
        {
            "attendance_id": att.attendance_id if att.attendance_id else "N/A",
            "employee_id": att.employee_id,
            "employee_name": f"{att.first_name} {att.last_name}",
            "date": date_str,
            "status": STATUS_MAP.get(att.status, "Không có thông tin")  # Show "Không có thông tin" if no status
        }
        for att in employees_with_attendance
    ]
    session["atc"] = session.get("atc", "") + ", Xem thông tin chấm công  "
    return render_template(
        'attendance.html',
        attendances=attendance_data,
        current_date=date_str,
        current_year=datetime.now().year
    )

@app.route('/api/attendance_detail')
@role_required('Admin', 'Acounting')
def attendance_detail():
    employee_id = request.args.get('employee_id')
    month = request.args.get('month')
    year = request.args.get('year')

    # Validate inputs
    if not (employee_id and month and year):
        return jsonify({"error": "Missing employee_id, month, or year"}), 400

    try:
        month = int(month)
        year = int(year)
        if not (1 <= month <= 12):
            raise ValueError("Invalid month")
    except ValueError:
        return jsonify({"error": "Invalid month or year"}), 400

    # Query attendance details for the employee, month, and year
    details = (
        db.session.query(Attendance.date, Attendance.status)
        .filter(
            Attendance.employee_id == employee_id,
            extract('month', Attendance.date) == month,
            extract('year', Attendance.date) == year
        )
        .all()
    )

    # Format response
    attendance_details = [
        {
            "date": d.date.strftime('%Y-%m-%d'),
            "status": STATUS_MAP.get(d.status, d.status)  # Map to Vietnamese
        }
        for d in details
    ]

    return jsonify(attendance_details)

@app.route('/api/employee_detail')
@role_required('Admin', 'Acounting')
def employee_detail():
    employee_id = request.args.get('employee_id')
    if not employee_id:
        return jsonify({"error": "Missing employee_id"}), 400

    try:
        employee = (
            db.session.query(
                Employee.employee_id,
                Employee.first_name,
                Employee.last_name,
                Department.department_name,
                Job.job_title
            )
            .join(Department, Employee.department_id == Department.department_id)
            .join(Job, Employee.job_id == Job.job_id)
            .filter(Employee.employee_id == employee_id, Employee.status == 'active')
            .first()
        )

        if not employee:
            return jsonify({"error": "Employee not found or inactive"}), 404

        return jsonify({
            "employee_id": employee.employee_id,
            "employee_name": f"{employee.first_name} {employee.last_name}",
            "department": employee.department_name,
            "job_title": employee.job_title
        })
    except Exception as e:
        logger.error(f"Error in employee_detail: {str(e)}")
        return jsonify({"error": f"Failed to fetch employee details: {str(e)}"}), 500

@app.route('/api/update_attendance', methods=['POST'])
@role_required('Admin', 'Accounting', 'Hiring')
def update_attendance():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    employee_id = data.get('employee_id')
    date_str = data.get('date')
    status = data.get('status')

    # Validate inputs
    if not (employee_id and date_str and status):
        return jsonify({"error": "Missing employee_id, date, or status"}), 400

    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"error": "Invalid date format, use YYYY-MM-DD"}), 400

    if status not in REVERSE_STATUS_MAP:
        return jsonify({"error": f"Invalid status, must be one of: {', '.join(REVERSE_STATUS_MAP.keys())}"}), 400

    # Check if employee exists and is active
    employee = db.session.query(Employee).filter_by(employee_id=employee_id, status='active').first()
    if not employee:
        return jsonify({"error": "Employee not found or inactive"}), 404

    # Check if attendance record exists
    attendance = db.session.query(Attendance).filter_by(employee_id=employee_id, date=date).first()

    try:
        if attendance:
            # Update existing record
            attendance.status = REVERSE_STATUS_MAP[status]
        else:
            # Create new record
            attendance = Attendance(
                employee_id=employee_id,
                date=date,
                status=REVERSE_STATUS_MAP[status]
            )
            db.session.add(attendance)
        
        db.session.commit()
        return jsonify({"message": "Attendance updated successfully", "attendance_id": attendance.attendance_id})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update attendance: {str(e)}"}), 500


# bao cao theo phong ban
@app.route('/report_depart')
@role_required('Admin', 'Acounting')
def report_depart():
    # Query all departments
    departments = db.session.query(Department).all()
    department_names = [dept.department_name for dept in departments]
    
    # Query payroll data grouped by department
    payroll_data = (
        db.session.query(
            Department.department_name,
            func.count(Employee.employee_id).label('employee_count'),
            func.sum(Payroll.base_salary).label('total_salary'),
            func.sum(Payroll.bonus).label('total_bonus'),
            func.sum(Payroll.deductions).label('total_deductions')
        )
        .join(Employee, Employee.department_id == Department.department_id)
        .outerjoin(Payroll, Payroll.employee_id == Employee.employee_id)
        .filter(Employee.status == 'active')
        .group_by(Department.department_name)
        .all()
    )

    # Initialize data structure
    data = {
        "departments": department_names,
        "salaries": [0] * len(department_names),  # Initialize with zeros
        "summary": {
            "total_employees": 0,
            "total_salary": 0.0,
            "total_bonus": 0.0,
            "total_deductions": 0.0
        },
        "details": []
    }

    # Process payroll data
    department_salary_map = {row.department_name: row.total_salary or 0 for row in payroll_data}
    for dept in departments:
        # Find matching payroll data for this department
        payroll_row = next((row for row in payroll_data if row.department_name == dept.department_name), None)
        
        employee_count = payroll_row.employee_count if payroll_row else 0
        total_salary = float(payroll_row.total_salary or 0) if payroll_row else 0.0
        avg_salary = total_salary / employee_count if employee_count > 0 else 0.0

        # Update salaries list
        dept_index = department_names.index(dept.department_name)
        data["salaries"][dept_index] = total_salary

        # Update details
        data["details"].append({
            "department": dept.department_name,
            "employees": employee_count,
            "total_salary": total_salary,
            "avg_salary": avg_salary
        })

        # Update summary
        data["summary"]["total_employees"] += employee_count
        data["summary"]["total_salary"] += total_salary
        if payroll_row:
            data["summary"]["total_bonus"] += float(payroll_row.total_bonus or 0)
            data["summary"]["total_deductions"] += float(payroll_row.total_deductions or 0)
    session["atc"] = session.get("atc", "") + ", Xem báo cáo phòng ban"
    return render_template('report_depart.html', data=data)

# Lịch Sử Lương 
@app.route('/history_salary')
@role_required('Admin', 'Acounting')
def history_salary():
    try:
        # Lấy tháng và năm hiện tại
        current_year = datetime.now().year
        current_month = datetime.now().month

        # Lấy tháng và năm được chọn từ request, mặc định là tháng và năm hiện tại
        selected_month = request.args.get("month", str(current_month))
        selected_year = request.args.get("year", str(current_year))

        # Truy vấn các tháng và năm có dữ liệu
        available_months_query = (
            db.session.query(extract('month', Payroll.pay_date).label('month'))
            .filter(extract('year', Payroll.pay_date) == int(selected_year))
            .filter(Payroll.pay_date.isnot(None))
            .distinct()
            .order_by(extract('month', Payroll.pay_date).asc())
        )
        available_months = [str(int(row.month)) for row in available_months_query.all()]

        available_years_query = (
            db.session.query(extract('year', Payroll.pay_date).label('year'))
            .filter(Payroll.pay_date.isnot(None))
            .distinct()
            .order_by(extract('year', Payroll.pay_date).desc())
        )
        available_years = [str(int(row.year)) for row in available_years_query.all()]

        # Truy vấn chính cho dữ liệu lương
        query = (
            db.session.query(
                Payroll.payroll_id,  # Added payroll_id for detail link
                Employee.employee_id,
                Employee.first_name,
                Employee.last_name,
                Department.department_name,
                Job.job_title,
                extract('month', Payroll.pay_date).label('month'),
                extract('year', Payroll.pay_date).label('year'),
                Payroll.base_salary,
                Payroll.bonus,
                Payroll.deductions,
                Payroll.net_salary
            )
            .join(Payroll, Payroll.employee_id == Employee.employee_id)
            .join(Department, Employee.department_id == Department.department_id)
            .join(Job, Employee.job_id == Job.job_id)
            .filter(Employee.status == 'active')
            .filter(Payroll.pay_date.isnot(None))
        )

        # Lọc theo năm và tháng nếu hợp lệ
        if selected_year in available_years:
            query = query.filter(extract('year', Payroll.pay_date) == int(selected_year))
        else:
            selected_year = available_years[0] if available_years else str(current_year)
            query = query.filter(extract('year', Payroll.pay_date) == int(selected_year))

        if selected_month in available_months:
            query = query.filter(extract('month', Payroll.pay_date) == int(selected_month))
        else:
            selected_month = available_months[-1] if available_months else str(current_month)
            query = query.filter(extract('month', Payroll.pay_date) == int(selected_month))

        # Thực thi truy vấn
        results = query.all()

        # Định dạng dữ liệu cho template
        payroll_data = [
            {
                "payroll_id": row.payroll_id,  # Added for detail link
                "id": row.employee_id,
                "name": f"{row.first_name} {row.last_name}",
                "department": row.department_name,
                "position": row.job_title,
                "month": str(int(row.month)),
                "year": str(int(row.year)),
                "base_salary": float(row.base_salary or 0),
                "bonus": float(row.bonus or 0),
                "deduction": float(row.deductions or 0),
                "total_salary": float(row.net_salary or 0)
            }
            for row in results
        ]
        session["atc"] = session.get("atc", "") + ", Xem lịch sử lương "
        return render_template(
            "history_salary.html",
            payroll_data=payroll_data,
            selected_month=selected_month,
            selected_year=selected_year,
            available_months=available_months,
            available_years=available_years,
            current_year=current_year
        )

    except Exception as e:
        logger.error(f"Error in history_salary: {str(e)}")
        return render_template(
            "error.html",
            error_message=f"Đã xảy ra lỗi khi truy xuất dữ liệu lương: {str(e)}"
        )

@app.route('/payroll_detail/<payroll_id>')
@role_required('Admin', 'Acounting')
def payroll_detail(payroll_id):
    try:
        # Truy vấn chi tiết bảng lương dựa trên payroll_id
        payroll = (
            db.session.query(
                Payroll.payroll_id,
                Employee.employee_id,
                Employee.first_name,
                Employee.last_name,
                Department.department_name,
                Job.job_title,
                Payroll.pay_date,
                Payroll.base_salary,
                Payroll.bonus,
                Payroll.deductions,
                Payroll.net_salary
            )
            .join(Employee, Payroll.employee_id == Employee.employee_id)
            .join(Department, Employee.department_id == Department.department_id)
            .join(Job, Employee.job_id == Job.job_id)
            .filter(Payroll.payroll_id == payroll_id)
            .first()
        )

        if not payroll:
            flash("Không tìm thấy thông tin bảng lương.", "error")
            return redirect(url_for('history_salary'))

        payroll_data = {
            "payroll_id": payroll.payroll_id,
            "employee_id": payroll.employee_id,
            "name": f"{payroll.first_name} {payroll.last_name}",
            "department": payroll.department_name,
            "job_title": payroll.job_title,
            "pay_date": payroll.pay_date.strftime('%Y-%m-%d') if payroll.pay_date else "N/A",
            "base_salary": float(payroll.base_salary or 0),
            "bonus": float(payroll.bonus or 0),
            "deductions": float(payroll.deductions or 0),
            "net_salary": float(payroll.net_salary or 0)
        }
        session["atc"] = session.get("atc", "") + f", Xem chi tiết bảng lương ID {payroll_id}"
        return render_template("payroll_detail.html", payroll=payroll_data)

    except Exception as e:
        logger.error(f"Error in payroll_detail: {str(e)}")
        flash(f"Đã xảy ra lỗi khi truy xuất chi tiết bảng lương: {str(e)}", "error")
        return redirect(url_for('history_salary'))
# HR ROUTES

@app.route('/employee_HR')
@role_required('Admin','Hiring')
def employee_HR():
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
        session["atc"] = session.get("atc", "") + f", Xem danh sách nhân viên "

        return render_template('employee_HR.html', employees=employees_data)
    except Exception as e:
        logger.error(f"Error in /employees GET: {str(e)}")
        return jsonify({"error": str(e)}), 500



@app.route('/employees', methods=['POST'])
@role_required('Admin', 'Hiring')
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
@role_required('Admin', 'Hiring')
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
@role_required('Admin', 'Hiring')
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
@role_required('Admin', 'Hiring')
def recruitment_HR():
    session["atc"] = session.get("atc", "") + f", Xem danh sách tuyển dụng "

    return render_template('recruitment_HR.html')

# API: Lấy danh sách tất cả vị trí tuyển dụng
@app.route('/api/recruitments', methods=['GET'])
@role_required('Admin', 'Hiring')
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
@role_required('Admin', 'Hiring')
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
@role_required('Admin', 'Hiring')
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
@role_required('Admin', 'Hiring')
def delete_recruitment(id):
    global recruitments
    recruitment = next((r for r in recruitments if r['id'] == id), None)
    if recruitment:
        recruitments = [r for r in recruitments if r['id'] != id]
        save_recruitments(recruitments)
        return jsonify({"message": "Recruitment deleted"})
    return jsonify({"error": "Recruitment not found"}), 404   
    

@app.route('/reports_HR')
@role_required('Admin','Hiring')
def reports_HR():
    try:
        thirty_days_ago = datetime.now() - timedelta(days=30)
        total_employees = HumanEmployee.query.count()
        new_employees = HumanEmployee.query.filter(HumanEmployee.hire_date >= thirty_days_ago).count()
        resigned_employees = HumanEmployee.query.filter_by(status='Inactive').count()
        
        departments = HumanDepartment.query.all()
        departments_data = [{
            'department_id': dept.department_id,
            'department_name': dept.department_name,
            'employee_count': HumanEmployee.query.filter_by(department_id=dept.department_id).count()
        } for dept in departments]
        
        reports_data = [{
            'role': 'All Employees',
            'total': total_employees,
            'newEmployees': new_employees,
            'resignedEmployees': resigned_employees,
            'departments': departments_data
        }]
        return render_template("reports_HR.html", reports=reports_data)
    except NoReferencedColumnError as e:
        logger.error(f"Schema error in /reports_HR: {str(e)}")
        flash("Database schema error: Unable to load reports.", "error")
        return render_template("reports_HR.html", reports=[])
    except Exception as e:
        logger.error(f"Error in /reports_HR: {str(e)}")
        flash(f"Error loading reports: {str(e)}", "error")
        return render_template("reports_HR.html", reports=[])
            

# API ROUTES
@app.route('/api/employees', methods=['GET', 'POST'])
@role_required('Admin', 'Hiring')
def manage_employees():
    if request.method == 'GET':
        try:
            employees = HumanEmployee.query.all()
            employees_data = [{
                'employee_id': emp.employee_id,
                'first_name': emp.applicant.first_name if emp.applicant else None,
                'last_name': emp.applicant.last_name if emp.applicant else None,
                'full_name': f"{emp.applicant.last_name} {emp.applicant.first_name}" if emp.applicant else None,
                'email': emp.applicant.email if emp.applicant else None,
                'phone': emp.applicant.phone_number if emp.applicant else None,
                'hire_date': emp.hire_date.strftime('%Y-%m-%d') if emp.hire_date else None,
                'department_id': emp.department_id,
                'department_name': emp.department.department_name if emp.department else None,
                'job_id': emp.applicant.job_id if emp.applicant else None,
                'job_title': emp.applicant.job.job_title if emp.applicant and emp.applicant.job else None,
                'base_salary': float(emp.salary) if emp.salary else 0.0,
                'status': emp.status
            } for emp in employees]
            callback = request.args.get('callback')
            if callback:
                return f"{callback}({jsonify(employees_data).get_data(as_text=True)})"
            return jsonify(employees_data)
        except NoReferencedColumnError as e:
            logger.error(f"Schema error in /api/employees: {str(e)}")
            return jsonify([]), 200
        except Exception as e:
            logger.error(f"Error in /api/employees: {str(e)}")
            return jsonify({"error": str(e)}), 500

    elif request.method == 'POST':
        try:
            data = request.get_json()
            required_fields = ['first_name', 'last_name', 'email', 'hire_date', 'job_id', 'department_id', 'base_salary']
            for field in required_fields:
                if field not in data or not data[field]:
                    return jsonify({"error": f"Missing required field: {field}"}), 400
            
            existing_applicant = Applicant.query.filter_by(email=data['email']).first()
            if existing_applicant:
                return jsonify({"error": "Email already exists in the system"}), 409
                
            applicant = Applicant(
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email'],
                phone_number=data.get('phone', ''),
                application_date=datetime.strptime(data['hire_date'], '%Y-%m-%d'),
                status='Hired',
                job_id=data['job_id']
            )
            db.session.add(applicant)
            db.session.flush()

            human_employee = HumanEmployee(
                applicant_id=applicant.applicant_id,
                department_id=data['department_id'],
                hire_date=datetime.strptime(data['hire_date'], '%Y-%m-%d'),
                salary=data['base_salary'],
                status=data.get('status', 'Active')
            )
            db.session.add(human_employee)
            db.session.flush()

            payroll_employee = Employee(
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email'],
                phone=data.get('phone', ''),
                hire_date=datetime.strptime(data['hire_date'], '%Y-%m-%d'),
                department_id=data['department_id'],
                job_id=data['job_id'],
                salary=data['base_salary'],
                status=data.get('status', 'active').lower()
            )
            db.session.add(payroll_employee)
            db.session.flush()

            if 'bonus' in data or 'deductions' in data:
                human_payroll = HumanPayroll(
                    employee_id=human_employee.employee_id,
                    pay_date=datetime.now(),
                    base_salary=data['base_salary'],
                    bonus=data.get('bonus', 0),
                    deductions=data.get('deductions', 0)
                )
                db.session.add(human_payroll)

                payroll_record = Payroll(
                    employee_id=payroll_employee.employee_id,
                    pay_date=datetime.now(),
                    base_salary=data['base_salary'],
                    bonus=data.get('bonus', 0),
                    deductions=data.get('deductions', 0),
                    net_salary=float(data['base_salary']) + float(data.get('bonus', 0)) - float(data.get('deductions', 0))
                )
                db.session.add(payroll_record)
            
            db.session.commit()

            employee_data = {
                'employee_id': human_employee.employee_id,
                'first_name': applicant.first_name,
                'last_name': applicant.last_name,
                'full_name': f"{applicant.last_name} {applicant.first_name}",
                'email': applicant.email,
                'phone': applicant.phone_number,
                'hire_date': human_employee.hire_date.strftime('%Y-%m-%d'),
                'department_id': human_employee.department_id,
                'department_name': HumanDepartment.query.get(human_employee.department_id).department_name,
                'job_id': applicant.job_id,
                'job_title': HumanJob.query.get(applicant.job_id).job_title,
                'base_salary': float(human_employee.salary),
                'status': human_employee.status
            }
            return jsonify({"success": True, "message": "Employee added successfully", "data": employee_data}), 201
        except IntegrityError as e:
            logger.error(f"Integrity error in /api/employees POST: {str(e)}")
            db.session.rollback()
            return jsonify({"error": "Database integrity error: Possible duplicate or invalid foreign key."}), 400
        except NoReferencedColumnError as e:
            logger.error(f"Schema error in /api/employees POST: {str(e)}")
            db.session.rollback()
            return jsonify({"error": "Unable to add employee due to database schema issue."}), 500
        except Exception as e:
            logger.error(f"Error in /api/employees POST: {str(e)}")
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

@app.route('/api/employees/<employee_id>', methods=['GET', 'PUT', 'DELETE'])
@role_required('Admin', 'Hiring')
def manage_employee(employee_id):
    try:
        human_employee = HumanEmployee.query.filter_by(employee_id=employee_id).first()
        if not human_employee:
            return jsonify({"error": "Employee not found"}), 404

        if request.method == 'GET':
            applicant = human_employee.applicant
            if not applicant:
                return jsonify({"error": "Associated applicant data not found"}), 404
                
            employee_data = {
                'employee_id': human_employee.employee_id,
                'first_name': applicant.first_name,
                'last_name': applicant.last_name,
                'full_name': f"{applicant.last_name} {applicant.first_name}",
                'email': applicant.email,
                'phone': applicant.phone_number,
                'hire_date': human_employee.hire_date.strftime('%Y-%m-%d') if human_employee.hire_date else None,
                'department_id': human_employee.department_id,
                'department_name': human_employee.department.department_name if human_employee.department else None,
                'job_id': applicant.job_id,
                'job_title': applicant.job.job_title if applicant.job else None,
                'base_salary': float(human_employee.salary) if human_employee.salary else 0.0,
                'status': human_employee.status
            }
            return jsonify(employee_data)

        elif request.method == 'PUT':
            data = request.get_json()
            applicant = Applicant.query.filter_by(applicant_id=human_employee.applicant_id).first()
            if not applicant:
                return jsonify({"error": "Associated applicant data not found"}), 404
                
            if 'email' in data and data['email'] != applicant.email:
                existing_email = Applicant.query.filter_by(email=data['email']).first()
                if existing_email and existing_email.applicant_id != applicant.applicant_id:
                    return jsonify({"error": "Email already exists for another employee"}), 409
            
            for field in ['first_name', 'last_name', 'email', 'phone']:
                if field in data:
                    setattr(applicant, 'phone_number' if field == 'phone' else field, data[field])
                    
            if 'job_id' in data:
                applicant.job_id = data['job_id']
                
            if 'hire_date' in data:
                human_employee.hire_date = datetime.strptime(data['hire_date'], '%Y-%m-%d')
            if 'department_id' in data:
                human_employee.department_id = data['department_id']
            if 'base_salary' in data:
                human_employee.salary = data['base_salary']
            if 'status' in data:
                human_employee.status = data['status']
                
            payroll_employee = Employee.query.filter_by(email=applicant.email).first()
            if payroll_employee:
                payroll_employee.first_name = applicant.first_name
                payroll_employee.last_name = applicant.last_name
                payroll_employee.email = applicant.email
                payroll_employee.phone = applicant.phone_number
                payroll_employee.hire_date = human_employee.hire_date
                payroll_employee.department_id = human_employee.department_id
                payroll_employee.job_id = applicant.job_id
                payroll_employee.salary = human_employee.salary
                payroll_employee.status = human_employee.status.lower()

            human_payroll = HumanPayroll.query.filter_by(employee_id=employee_id).order_by(HumanPayroll.PayDate.desc()).first()
            if 'bonus' in data or 'deductions' in data:
                if not human_payroll:
                    human_payroll = HumanPayroll(
                        employee_id=employee_id,
                        pay_date=datetime.now(),
                        base_salary=human_employee.salary,
                        bonus=data.get('bonus', 0),
                        deductions=data.get('deductions', 0)
                    )
                    db.session.add(human_payroll)
                else:
                    if 'bonus' in data:
                        human_payroll.bonus = data['bonus']
                    if 'deductions' in data:
                        human_payroll.deductions = data['deductions']
                    if 'base_salary' in data:
                        human_payroll.base_salary = data['base_salary']

                if payroll_employee:
                    payroll_record = Payroll.query.filter_by(employee_id=payroll_employee.employee_id).order_by(Payroll.pay_date.desc()).first()
                    if not payroll_record:
                        payroll_record = Payroll(
                            employee_id=payroll_employee.employee_id,
                            pay_date=datetime.now(),
                            base_salary=human_employee.salary,
                            bonus=data.get('bonus', 0),
                            deductions=data.get('deductions', 0),
                            net_salary=float(human_employee.salary) + float(data.get('bonus', 0)) - float(data.get('deductions', 0))
                        )
                        db.session.add(payroll_record)
                    else:
                        if 'bonus' in data:
                            payroll_record.bonus = data['bonus']
                        if 'deductions' in data:
                            payroll_record.deductions = data['deductions']
                        if 'base_salary' in data:
                            payroll_record.base_salary = data['base_salary']
                        payroll_record.net_salary = float(payroll_record.base_salary) + float(payroll_record.bonus or 0) - float(payroll_record.deductions or 0)
                
            db.session.commit()

            employee_data = {
                'employee_id': human_employee.employee_id,
                'first_name': applicant.first_name,
                'last_name': applicant.last_name,
                'full_name': f"{applicant.last_name} {applicant.first_name}",
                'email': applicant.email,
                'phone': applicant.phone_number,
                'hire_date': human_employee.hire_date.strftime('%Y-%m-%d'),
                'department_id': human_employee.department_id,
                'department_name': human_employee.department.department_name if human_employee.department else None,
                'job_id': applicant.job_id,
                'job_title': applicant.job.job_title if applicant.job else None,
                'base_salary': float(human_employee.salary) if human_employee.salary else 0.0,
                'status': human_employee.status
            }
            return jsonify({"success": True, "message": "Employee updated successfully", "data": employee_data})

        elif request.method == 'DELETE':
            payrolls = HumanPayroll.query.filter_by(employee_id=employee_id).all()
            shareholder = Shareholder.query.filter_by(employee_id=employee_id).first()
            applicant = Applicant.query.filter_by(applicant_id=human_employee.applicant_id).first()

            for payroll in payrolls:
                db.session.delete(payroll)

            if shareholder:
                dividends = Dividend.query.filter_by(shareholder_id=shareholder.shareholder_id).all()
                for dividend in dividends:
                    db.session.delete(dividend)
                db.session.delete(shareholder)

            payroll_employee = Employee.query.filter_by(email=applicant.email).first()
            if payroll_employee:
                payroll_records = Payroll.query.filter_by(employee_id=payroll_employee.employee_id).all()
                for record in payroll_records:
                    db.session.delete(record)
                db.session.delete(payroll_employee)

            db.session.delete(human_employee)
            if applicant:
                db.session.delete(applicant)
                
            db.session.commit()
            return jsonify({"success": True, "message": "Employee deleted successfully"})

    except IntegrityError as e:
        logger.error(f"Integrity error in /api/employees/{employee_id}: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "Database integrity error: Possible duplicate or invalid foreign key."}), 400
    except NoReferencedColumnError as e:
        logger.error(f"Schema error in /api/employees/{employee_id}: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "Unable to manage employee due to database schema issue."}), 500
    except Exception as e:
        logger.error(f"Error in /api/employees/{employee_id}: {str(e)}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/employees/detail/<employee_id>', methods=['GET', 'PUT'])
@role_required('Admin', 'Hiring')
def manage_employee_detail(employee_id):
    try:
        human_employee = HumanEmployee.query.filter_by(employee_id=employee_id).first()
        if not human_employee:
            return jsonify({"error": "Employee not found"}), 404

        if request.method == 'GET':
            payroll = HumanPayroll.query.filter_by(employee_id=employee_id).order_by(HumanPayroll.PayDate.desc()).first()
            shareholder = Shareholder.query.filter_by(employee_id=employee_id).first()
            
            employee_data = {
                'employee_id': human_employee.employee_id,
                'first_name': human_employee.applicant.first_name if human_employee.applicant else None,
                'last_name': human_employee.applicant.last_name if human_employee.applicant else None,
                'full_name': f"{human_employee.applicant.last_name} {human_employee.applicant.first_name}" if human_employee.applicant else None,
                'email': human_employee.applicant.email if human_employee.applicant else None,
                'phone': human_employee.applicant.phone_number if human_employee.applicant else None,
                'hire_date': human_employee.hire_date.strftime('%Y-%m-%d') if human_employee.hire_date else None,
                'department_id': human_employee.department_id,
                'department_name': human_employee.department.department_name if human_employee.department else None,
                'job_id': human_employee.applicant.job_id if human_employee.applicant else None,
                'job_title': human_employee.applicant.job.job_title if human_employee.applicant and human_employee.applicant.job else None,
                'base_salary': float(human_employee.salary) if human_employee.salary else 0.0,
                'status': human_employee.status,
                'bonus': float(payroll.bonus) if payroll and payroll.bonus else 0,
                'deductions': float(payroll.deductions) if payroll and payroll.deductions else 0,
                'is_shareholder': shareholder is not None,
                'investment_amount': float(shareholder.investment_amount) if shareholder and shareholder.investment_amount else 0
            }
            return jsonify(employee_data)

        elif request.method == 'PUT':
            data = request.json
            applicant = Applicant.query.filter_by(applicant_id=human_employee.applicant_id).first()
            if not applicant:
                return jsonify({"error": "Associated applicant data not found"}), 404
                
            for field in ['first_name', 'last_name', 'email', 'phone']:
                if field in data:
                    setattr(applicant, 'phone_number' if field == 'phone' else field, data[field])
                    
            if 'job_id' in data:
                job = HumanJob.query.filter_by(job_id=data['job_id']).first()
                if not job:
                    return jsonify({"error": f"Job with ID {data['job_id']} not found"}), 404
                applicant.job_id = data['job_id']
            
            if 'hire_date' in data:
                human_employee.hire_date = datetime.strptime(data['hire_date'], '%Y-%m-%d')
                
            if 'department_id' in data:
                department = HumanDepartment.query.filter_by(department_id=data['department_id']).first()
                if not department:
                    return jsonify({"error": f"Department with ID {data['department_id']} not found"}), 404
                human_employee.department_id = data['department_id']
                
            if 'base_salary' in data:
                human_employee.salary = data['base_salary']
                
            if 'status' in data:
                human_employee.status = data['status']

            payroll_employee = Employee.query.filter_by(email=applicant.email).first()
            if payroll_employee:
                payroll_employee.first_name = applicant.first_name
                payroll_employee.last_name = applicant.last_name
                payroll_employee.email = applicant.email
                payroll_employee.phone = applicant.phone_number
                payroll_employee.hire_date = human_employee.hire_date
                payroll_employee.department_id = human_employee.department_id
                payroll_employee.job_id = applicant.job_id
                payroll_employee.salary = human_employee.salary
                payroll_employee.status = human_employee.status.lower()

            payroll = HumanPayroll.query.filter_by(employee_id=employee_id).order_by(HumanPayroll.PayDate.desc()).first()
            if not payroll and ('bonus' in data or 'deductions' in data):
                payroll = HumanPayroll(
                    employee_id=employee_id,
                    pay_date=datetime.now(),
                    base_salary=human_employee.salary,
                    bonus=data.get('bonus', 0),
                    deductions=data.get('deductions', 0)
                )
                db.session.add(payroll)
            elif payroll:
                if 'bonus' in data:
                    payroll.bonus = data['bonus']
                if 'deductions' in data:
                    payroll.deductions = data['deductions']
                if 'base_salary' in data:
                    payroll.base_salary = data['base_salary']

                if payroll_employee:
                    payroll_record = Payroll.query.filter_by(employee_id=payroll_employee.employee_id).order_by(Payroll.pay_date.desc()).first()
                    if not payroll_record:
                        payroll_record = Payroll(
                            employee_id=payroll_employee.employee_id,
                            pay_date=datetime.now(),
                            base_salary=human_employee.salary,
                            bonus=data.get('bonus', 0),
                            deductions=data.get('deductions', 0),
                            net_salary=float(human_employee.salary) + float(data.get('bonus', 0)) - float(data.get('deductions', 0))
                        )
                        db.session.add(payroll_record)
                    else:
                        if 'bonus' in data:
                            payroll_record.bonus = data['bonus']
                        if 'deductions' in data:
                            payroll_record.deductions = data['deductions']
                        if 'base_salary' in data:
                            payroll_record.base_salary = data['base_salary']
                        payroll_record.net_salary = float(payroll_record.base_salary) + float(payroll_record.bonus or 0) - float(payroll_record.deductions or 0)

            if 'is_shareholder' in data:
                shareholder = Shareholder.query.filter_by(employee_id=employee_id).first()
                
                if data['is_shareholder'] and not shareholder:
                    shareholder = Shareholder(
                        first_name=applicant.first_name,
                        last_name=applicant.last_name,
                        email=applicant.email,
                        phone_number=applicant.phone_number,
                        investment_amount=data.get('investment_amount', 0),
                        is_employee=True,
                        employee_id=employee_id
                    )
                    db.session.add(shareholder)
                elif not data['is_shareholder'] and shareholder:
                    dividends = Dividend.query.filter_by(shareholder_id=shareholder.shareholder_id).all()
                    for dividend in dividends:
                        db.session.delete(dividend)
                    db.session.delete(shareholder)
                elif shareholder and 'investment_amount' in data:
                    shareholder.investment_amount = data['investment_amount']

            db.session.commit()
            return jsonify({"success": True, "message": "Employee details updated successfully"})

    except IntegrityError as e:
        logger.error(f"Integrity error in /api/employees/detail/{employee_id}: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "Database integrity error: Possible duplicate or invalid foreign key."}), 400
    except NoReferencedColumnError as e:
        logger.error(f"Schema error in /api/employees/detail/{employee_id}: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "Unable to update employee details due to database schema issue."}), 500
    except Exception as e:
        logger.error(f"Error in /api/employees/detail/{employee_id}: {str(e)}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
### PHONG BAN CHUC VU ####################################################################  

# Route chính
@app.route('/department_position')
@role_required('Admin', 'Hiring')
def department_position():
    with app.app_context():
        departments = Department.query.all()
        jobs = Job.query.all()
    session["atc"] = session.get("atc", "") + f", Xem Phòng ban và chức vụ "

    return render_template('depart_pos.html', departments=departments, jobs=jobs)

# API: Thêm công việc
@app.route('/api/add_job', methods=['POST'])
@role_required('Admin', 'Hiring')
def add_job():
    job_title = request.form.get('job_title')
    if not job_title:
        return jsonify({'error': 'Tên công việc không được để trống'}), 400
    new_job = Job(job_title=job_title)
    try:
        db.session.add(new_job)
        db.session.commit()
        return jsonify({'job_id': new_job.job_id, 'job_title': new_job.job_title}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# API: Xóa công việc
@app.route('/api/delete_job/<int:job_id>', methods=['DELETE'])
@role_required('Admin', 'Hiring')
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    if Employee.query.filter_by(job_id=job_id).first():
        return jsonify({'success': False, 'error': 'Không thể xóa công việc vì có nhân viên đang sử dụng'}), 400
    try:
        db.session.delete(job)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# API: Thêm phòng ban
@app.route('/api/add_department', methods=['POST'])
@role_required('Admin', 'Hiring')
def add_department():
    department_name = request.form.get('department_name')
    if not department_name:
        return jsonify({'error': 'Tên phòng ban không được để trống'}), 400
    new_department = Department(department_name=department_name)
    try:
        db.session.add(new_department)
        db.session.commit()
        return jsonify({'department_id': new_department.department_id, 'department_name': new_department.department_name}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# API: Xóa phòng ban
@app.route('/api/delete_department/<int:department_id>', methods=['DELETE'])
@role_required('Admin', 'Hiring')
def delete_department(department_id):
    department = Department.query.get_or_404(department_id)
    if Employee.query.filter_by(department_id=department_id).first():
        return jsonify({'success': False, 'error': 'Không thể xóa phòng ban vì có nhân viên đang sử dụng'}), 400
    try:
        db.session.delete(department)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# API: Xem nhân viên theo công việc
@app.route('/api/employees_by_job/<int:job_id>')
@role_required('Admin', 'Hiring')
def employees_by_job(job_id):
    employees = Employee.query.filter_by(job_id=job_id).all()
    return jsonify([{
        'employee_id': emp.employee_id,
        'full_name': f"{emp.first_name} {emp.last_name}",
        'email': emp.email
    } for emp in employees])

# API: Xem nhân viên theo phòng ban
@app.route('/api/employees_by_department/<int:department_id>')
@role_required('Admin', 'Hiring')
def employees_by_department(department_id):
    employees = Employee.query.filter_by(department_id=department_id).all()
    return jsonify([{
        'employee_id': emp.employee_id,
        'full_name': f"{emp.first_name} {emp.last_name}",
        'email': emp.email
    } for emp in employees])

# Quyền #####################################################################
@app.route('/groups')
@role_required('Admin')
def display_groups():
    groups = Group.query.all()
    group_permissions = []
    
    for group in groups:
        permissions = Permission.query.filter_by(GroupID=group.GroupID, IsAllowed=True).join(
            FunctionModule
        ).join(
            Function
        ).join(
            Module
        ).all()
        
        functions_by_module = {}
        for perm in permissions:
            module_name = perm.FunctionModule.Module.ModuleName
            function_name = perm.FunctionModule.Function.FunctionName
            if module_name not in functions_by_module:
                functions_by_module[module_name] = []
            functions_by_module[module_name].append(function_name)
        
        app.logger.debug(f"Group: {group.GroupName}, Functions by Module: {functions_by_module}")
        
        group_permissions.append({
            'group': group,
            'functions_by_module': functions_by_module
        })
    
    app.logger.debug(f"Group Permissions: {group_permissions}")
    
    return render_template('groups.html', group_permissions=group_permissions)

@app.route('/update_permissions/<int:group_id>', methods=['GET', 'POST'])
@role_required('Admin')
def update_permissions(group_id):
    group = Group.query.get_or_404(group_id)
    
    if request.method == 'POST':
        # Lấy danh sách FunctionModuleID được chọn từ form
        selected_function_modules = request.form.getlist('function_modules')
        selected_function_modules = [int(fm_id) for fm_id in selected_function_modules]
        
        # Xóa tất cả quyền hiện tại của group
        Permission.query.filter_by(GroupID=group_id).delete()
        
        # Thêm quyền mới
        for fm_id in selected_function_modules:
            permission = Permission(
                GroupID=group_id,
                FunctionModuleID=fm_id,
                IsAllowed=True
            )
            db.session.add(permission)
        
        db.session.commit()
        return redirect(url_for('display_groups'))
    
    # Lấy tất cả FunctionModule và quyền hiện tại của group
    function_modules = FunctionModule.query.join(Function).join(Module).all()
    current_permissions = Permission.query.filter_by(GroupID=group_id, IsAllowed=True).all()
    current_fm_ids = {perm.FunctionModuleID for perm in current_permissions}
    
    return render_template('update_permissions.html', group=group, function_modules=function_modules, current_fm_ids=current_fm_ids)
  
# lich Su Hoat Dong ##########################################################################
   
# Đường dẫn tới file JSON
JSON_FILE = "data/activity_history.json"

# Hàm đọc dữ liệu từ file JSON
def r_activity_history():
    try:
        if os.path.exists(JSON_FILE):
            with open(JSON_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Error reading {JSON_FILE}: {e}")
        return []

# Hàm ghi dữ liệu vào file JSON
def save_activity_history(recruitments):
    try:
        with open(JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(recruitments, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error writing to {JSON_FILE}: {e}")

# Đọc dữ liệu ban đầu
#activity_history = activity_history()


if __name__ == '__main__':
    app.run(debug=True)
