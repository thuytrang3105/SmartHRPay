from flask import Flask, render_template, request, jsonify, redirect , url_for 
from module  import db, UserAccount ,Employee, Department, Job, Payroll , HumanEmployee, HumanPayroll, HumanDepartment, HumanJob, Shareholder
import random

app = Flask(__name__)

# Cấu hình database (đảm bảo đã cấu hình đúng trong ứng dụng Flask của bạn)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://@HUMAN_SERVER/HUMAN_2025?driver=ODBC+Driver+17+for+SQL+Server'
app.config['SQLALCHEMY_BINDS'] = {
    'user': 'mysql+pymysql://root:123456123456@localhost/user',  # MySQL schema user
    'payroll': 'mysql+pymysql://root:123456123456@localhost/payroll',  # MySQL schema payroll
    'human': 'mssql+pyodbc://@HUMAN_SERVER/HUMAN_2025?driver=ODBC+Driver+17+for+SQL+Server'  # SQL Server database human
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Khởi tạo db với ứng dụng Flask
db.init_app(app)

@app.route("/")
def home ():
    return render_template('home.html')

######################################################################################################################

@app.route("/salary-nv")
def salary_nv():
    return render_template("salary_nv.html")

def get_salary_data(month, year):
    # Giả lập dữ liệu lương, có thể thay bằng truy vấn DB thực tế
    # Ví dụ: trả về dữ liệu khác nhau dựa trên tháng/năm
    if month == "3" and year == "2025":
        return {
            "base_salary": "12,000,000 VND",
            "bonus": "3,000,000 VND",
            "present": "23",
            "absent": "1",
            "leave": "0",
            "deductions": "400,000 VND",
            "net_salary": "14,600,000 VND"
        }
    return {
        "base_salary": "10,000,000 VND",
        "bonus": "2,000,000 VND",
        "present": "22",
        "absent": "2",
        "leave": "1",
        "deductions": "500,000 VND",
        "net_salary": "11,500,000 VND"
    }

@app.route('/home-nv', methods=['GET', 'POST'])
def home_nv():
    # Dữ liệu thông tin cá nhân của nhân viên (giả lập)
    employee = {
        "employee_id": "12345",
        "last_name": "Nguyễn",
        "first_name": "Văn A",
        "email": "vana@example.com",
        "phone": "0987654321",
        "start_date": "01/01/2022",
        "department_name": "IT",
        "job_title": "Developer",
        "status": "Đang làm việc"
    }

    # Dữ liệu thông báo cho nhân viên (giả lập)
    notifications = [
        {
            "title": "Thông báo lương tháng 3/2025",
            "content": "Bảng lương tháng 3 đã được phát hành. Vui lòng kiểm tra và xác nhận.",
            "timestamp": "28/03/2025 10:15"
        },
        {
            "title": "Thông báo cập nhật chính sách lương",
            "content": "Chính sách lương mới sẽ được áp dụng từ tháng 4/2025. Chi tiết vui lòng xem tại đây.",
            "timestamp": "15/03/2025 14:30"
        }
    ]

    # Dữ liệu lương ban đầu (mặc định)
    salary = get_salary_data("1", "2020")
    selected_month = "1"
    selected_year = "2020"

    if request.method == 'POST':
        selected_month = request.form.get('month')
        selected_year = request.form.get('year')
        salary = get_salary_data(selected_month, selected_year)

    return render_template("home_nv.html", employee=employee, notifications=notifications, salary=salary, selected_month=selected_month, selected_year=selected_year)

# API để lấy dữ liệu lương theo tháng/năm
@app.route('/api/salary', methods=['GET'])
def api_salary():
    month = request.args.get('month')
    year = request.args.get('year')
    salary_data = get_salary_data(month, year)
    return jsonify(salary_data)

#############################################################################################################
templates = [
    "department_AC.html", "employee_detail.html", "employee_list_detail.html",
    "history_AC.html", "home_AC.html", "home_HR.html", "home_nv.html",
    "home.html", "login.html", "logout_AC.html", "manager_employee.html",
    "notifications_AC.html", "payroll_AC.html", "register.html", "salary_nv.html"
]

# Tạo route động để render template theo tên file
@app.route('/<page>')
def show_page(page):
    template_name = f"{page}.html"
    if template_name in templates:
        return render_template(template_name)
    return "Page not found", 404

@app.route('/accountant')
def home_AC():
    return render_template('home_AC.html')

@app.route('/payroll_AC')
def payroll():
    with app.app_context():
        # Truy vấn dữ liệu từ các bảng liên quan
        payroll_query = db.session.query(
            Employee.employee_id.label('id'),
            db.func.concat(Employee.first_name, ' ', Employee.last_name).label('name'),
            Department.department_name.label('department'),
            Job.job_title.label('position'),
            Payroll.base_salary,
            Payroll.bonus,
            Payroll.deductions
        ).join(
            Department, Employee.department_id == Department.department_id
        ).join(
            Job, Employee.job_id == Job.job_id
        ).join(
            Payroll, Employee.employee_id == Payroll.employee_id
        ).all()

        # Chuyển đổi dữ liệu từ truy vấn thành danh sách dictionary
        payroll_data = [
            {
                "id": row.id,
                "id_dp": f"NV{str(row.id).zfill(3)}",  # Định dạng ID thành NV001, NV002,...
                "name": row.name,
                "department": row.department,
                "position": row.position,
                "base_salary": float(row.base_salary or 0),
                "bonus": float(row.bonus or 0),
                "deduction": float(row.deductions or 0)
            }
            for row in payroll_query
        ]

        # Tính tổng lương (net_salary)
        for employee in payroll_data:
            employee["total_salary"] = employee["base_salary"] + employee["bonus"] - employee["deduction"]
            
        # Lấy danh sách phòng ban từ database
        departments = Department.query.all()
        department_list = [dept.department_name for dept in departments]

        # Lấy danh sách chức vụ từ database
        jobs = Job.query.all()
        position_list = [job.job_title for job in jobs]

        # Nhận giá trị lọc từ request
        selected_department = request.args.get("department", "").lower()
        selected_position = request.args.get("position", "").lower()

        # Lọc dữ liệu
        filtered_data = [
            emp for emp in payroll_data
            if (not selected_department or emp["department"].lower() == selected_department)
            and (not selected_position or emp["position"].lower() == selected_position)
        ]

    return render_template (
        'payroll_AC.html',
        payroll_data=filtered_data, #truyền data
        selected_department=selected_department, #phòng ban được lọc
        selected_position=selected_position, #chức vụ được lọc 
        departments=department_list,  # Truyền danh sách phòng ban
        positions=position_list      # Truyền danh sách chức vụ
    )
    
# Route để xem chi tiết nhân viên
@app.route('/payroll_detail/<int:employee_id>')
def payroll_detail(employee_id):
    with app.app_context():
        # Truy vấn thông tin chi tiết của nhân viên
        employee_detail = db.session.query(
            Employee.employee_id.label('id'),
            db.func.concat(Employee.first_name, ' ', Employee.last_name).label('name'),
            Employee.email,
            Employee.phone,
            Employee.hire_date,
            Employee.status,
            Department.department_name.label('department'),
            Job.job_title.label('position'),
            Payroll.base_salary,
            Payroll.bonus,
            Payroll.deductions,
            Payroll.pay_date
        ).join(
            Department, Employee.department_id == Department.department_id
        ).join(
            Job, Employee.job_id == Job.job_id
        ).join(
            Payroll, Employee.employee_id == Payroll.employee_id
        ).filter(
            Employee.employee_id == employee_id
        ).first()

        if not employee_detail:
            return "Nhân viên không tồn tại", 404

        # Chuyển đổi dữ liệu chi tiết
        detail_data = {
            "id": f"NV{str(employee_detail.id).zfill(3)}",
            "name": employee_detail.name,
            "email": employee_detail.email,
            "phone": employee_detail.phone,
            "hire_date": employee_detail.hire_date,
            "status": employee_detail.status,
            "department": employee_detail.department,
            "position": employee_detail.position,
            "base_salary": float(employee_detail.base_salary or 0),
            "bonus": float(employee_detail.bonus or 0),
            "deduction": float(employee_detail.deductions or 0),
            "total_salary": float(employee_detail.base_salary or 0) + float(employee_detail.bonus or 0) - float(employee_detail.deductions or 0),
            "pay_date": employee_detail.pay_date
        }

    return render_template('payroll_detail.html', employee=detail_data)

# Route để lấy thông tin chi tiết nhân viên (dùng cho nút Sửa)
@app.route('/get_employee/<int:employee_id>', methods=['GET'])
def get_employee(employee_id):
    with app.app_context():
        # Truy vấn thông tin chi tiết nhân viên từ database payroll
        employee = db.session.query(
            Employee.employee_id,
            db.func.concat(Employee.first_name, ' ', Employee.last_name).label('name'),
            Department.department_name.label('department'),
            Job.job_title.label('position'),
            Payroll.base_salary,
            Payroll.bonus,
            Payroll.deductions,
            Payroll.note
        ).join(
            Department, Employee.department_id == Department.department_id
        ).join(
            Job, Employee.job_id == Job.job_id
        ).join(
            Payroll, Employee.employee_id == Payroll.employee_id
        ).filter(
            Employee.employee_id == employee_id
        ).first()

        if not employee:
            return jsonify({'error': 'Nhân viên không tồn tại'}), 404

        employee_data = {
            'employee_id': employee.employee_id,
            'id_dp': f"NV{str(employee.employee_id).zfill(3)}",
            'name': employee.name,
            'department': employee.department,
            'position': employee.position,
            'base_salary': float(employee.base_salary or 0),
            'bonus': float(employee.bonus or 0),
            'deduction': float(employee.deductions or 0),
            'note': employee.note or '',
            'total_salary': float(employee.base_salary or 0) + float(employee.bonus or 0) - float(employee.deductions or 0)
        }

        return jsonify(employee_data)

# Route để cập nhật thông tin nhân viên
@app.route('/update_employee/<int:employee_id>', methods=['POST'])
def update_employee(employee_id):
    with app.app_context():
        data = request.form

        # Lấy thông tin từ form
        name = data.get('name')
        department_name = data.get('department')
        position_name = data.get('position')
        base_salary = float(data.get('base_salary', 0))
        bonus = float(data.get('bonus', 0))
        deduction = float(data.get('deduction', 0))
        note = data.get('note', '')

        # Tách first_name và last_name từ name
        name_parts = name.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        # Lấy department_id và job_id từ tên phòng ban và chức vụ
        department = Department.query.filter_by(department_name=department_name).first()
        job = Job.query.filter_by(job_title=position_name).first()

        if not department or not job:
            return jsonify({'error': 'Phòng ban hoặc chức vụ không tồn tại'}), 400

        # Cập nhật trong database payroll
        employee = Employee.query.filter_by(employee_id=employee_id).first()
        if employee:
            employee.first_name = first_name
            employee.last_name = last_name
            employee.department_id = department.department_id
            employee.job_id = job.job_id
            employee.salary = base_salary  # Cập nhật salary trong bảng Employee

        payroll = Payroll.query.filter_by(employee_id=employee_id).first()
        if payroll:
            payroll.base_salary = base_salary
            payroll.bonus = bonus
            payroll.deductions = deduction
            payroll.net_salary = base_salary + bonus - deduction
            payroll.note = note

        # Cập nhật trong database human
        with db.session.bind('human') as human_session:
            # Cập nhật bảng HumanEmployee
            human_employee = human_session.query(HumanEmployee).filter_by(employee_id=employee_id).first()
            if human_employee:
                human_department = human_session.query(HumanDepartment).filter_by(department_name=department_name).first()
                human_job = human_session.query(HumanJob).filter_by(job_title=position_name).first()
                if human_department and human_job:
                    human_employee.department_id = human_department.department_id
                    human_employee.salary = base_salary
                    human_employee.status = employee.status  # Đồng bộ trạng thái

            # Cập nhật bảng HumanPayroll
            human_payroll = human_session.query(HumanPayroll).filter_by(EmployeeID=employee_id).first()
            if human_payroll:
                human_payroll.BaseSalary = base_salary
                human_payroll.Bonus = bonus
                human_payroll.Deductions = deduction

            # Cập nhật bảng Shareholders (nếu nhân viên là cổ đông)
            shareholder = human_session.query(Shareholder).filter_by(employee_id=employee_id).first()
            if shareholder:
                shareholder.first_name = first_name
                shareholder.last_name = last_name

            human_session.commit()

        # Cập nhật trong database user
        with db.session.bind('user') as user_session:
            user_account = user_session.query(UserAccount).filter_by(employee_id=employee_id).first()
            if user_account:
                user_account.employee_name = f"{first_name} {last_name}"
                user_session.commit()

        # Commit thay đổi trong database payroll
        db.session.commit()

        return jsonify({'message': 'Cập nhật nhân viên thành công'})

@app.route('/department_report_AC')
def department_report():
    # Dữ liệu giả lập (có thể lấy từ database)
    data = {
        "departments": ["CNTT", "Nhân sự", "Kinh doanh", "Marketing"],
        "salaries": [576000000, 195000000, 720000000, 399000000],
        "summary": {
            "total_employees": 120,
            "total_salary": 1890000000,
            "total_bonus": 245000000,
            "total_deductions": 156000000
        },
        "details": [
            {"department": "Công nghệ thông tin", "employees": 32, "total_salary": 576000000, "avg_salary": 18000000},
            {"department": "Nhân sự", "employees": 15, "total_salary": 195000000, "avg_salary": 13000000},
            {"department": "Kinh doanh", "employees": 45, "total_salary": 720000000, "avg_salary": 16000000},
            {"department": "Marketing", "employees": 28, "total_salary": 399000000, "avg_salary": 14250000},
        ]
    }

    return render_template('department_AC.html', data=data)


@app.route('/history_payroll_AC')
def history_payroll():
    payroll_data =[
        {"id": 1, "name": "Nguyễn Văn A", "department": "IT", "position": "Manager", "month": "1", "base_salary": 15000000, "bonus": 2000000, "deduction": 500000, "total_salary": 16500000},
        {"id": 2, "name": "Trần Thị B", "department": "HR", "position": "Senior", "month": "2", "base_salary": 12000000, "bonus": 1000000, "deduction": 300000, "total_salary": 12700000},
        {"id": 3, "name": "Lê Văn C", "department": "Sales", "position": "Junior", "month": "1", "base_salary": 10000000, "bonus": 1500000, "deduction": 400000, "total_salary": 11100000},
        {"id": 4, "name": "Phạm Thị D", "department": "Marketing", "position": "Team Lead", "month": "3", "base_salary": 13000000, "bonus": 1800000, "deduction": 600000, "total_salary": 14200000},
        {"id": 5, "name": "Hoàng Văn E", "department": "IT", "position": "Senior", "month": "2", "base_salary": 14000000, "bonus": 2500000, "deduction": 700000, "total_salary": 15800000},
        {"id": 6, "name": "Đỗ Thị F", "department": "HR", "position": "Junior", "month": "1", "base_salary": 9000000, "bonus": 800000, "deduction": 200000, "total_salary": 9600000},
        {"id": 7, "name": "Vũ Minh G", "department": "Sales", "position": "Manager", "month": "3", "base_salary": 18000000, "bonus": 3000000, "deduction": 1000000, "total_salary": 20000000},
        {"id": 8, "name": "Bùi Thanh H", "department": "Marketing", "position": "Senior", "month": "2", "base_salary": 12500000, "bonus": 2200000, "deduction": 500000, "total_salary": 14200000},
        {"id": 9, "name": "Ngô Văn I", "department": "IT", "position": "Junior", "month": "1", "base_salary": 10500000, "bonus": 1200000, "deduction": 400000, "total_salary": 11300000},
        {"id": 10, "name": "Lương Thị J", "department": "HR", "position": "Team Lead", "month": "3", "base_salary": 16000000, "bonus": 2800000, "deduction": 800000, "total_salary": 18000000},
    ]

    # Nhận dữ liệu từ request (chỉ lọc theo tháng)
    selected_month = request.args.get("month", "")

    # Lọc dữ liệu chỉ theo tháng
    filtered_data = [emp for emp in payroll_data if not selected_month or emp["month"] == selected_month]

    return render_template("history_AC.html", payroll_data=filtered_data, selected_month=selected_month)

@app.route("/notifications_AC")
def get_notifications():
    notifications = [
    {
        "title": "Thông báo lương tháng 3/2025",
        "status": "sent",
        "recipients": "Tất cả nhân viên (120)",
        "content": "Bảng lương tháng 3 đã được phát hành. Vui lòng kiểm tra và xác nhận.",
        "timestamp": "28/03/2025 10:15"
    },
    {
        "title": "Thông báo cập nhật chính sách lương",
        "status": "sent",
        "recipients": "Phòng IT, Phòng Marketing (60)",
        "content": "Chính sách lương mới sẽ được áp dụng từ tháng 4/2025. Chi tiết vui lòng xem tại đây.",
        "timestamp": "15/03/2025 14:30"
    },
    {
        "title": "Thông báo điều chỉnh lương cho nhân viên kinh doanh",
        "status": "draft",
        "recipients": "Phòng Kinh doanh (45)",
        "content": "Điều chỉnh chế độ thưởng doanh số cho nhân viên kinh doanh từ tháng 4/2025.",
        "timestamp": "20/03/2025 09:45"
    }]
    return render_template("notifications_AC.html",notifications=notifications)


##################################################################################################################
# Dữ liệu mẫu (có thể thay bằng database thực tế)
jobs = [
    {"job_id": "CV001", "job_title": "Nhân viên"},
    {"job_id": "CV002", "job_title": "Quản lý"}
]

departments = [
    {"department_id": "PB001", "department_name": "IT"},
    {"department_id": "PB002", "department_name": "HR"}
]

# Dữ liệu nhân viên (được lưu trong Python thay vì localStorage)
employees = [
    {
        "employee_id": "NV001",
        "first_name": "Văn B",
        "last_name": "Nguyễn",
        "full_name": "Nguyễn Văn B",
        "email": "nvb@example.com",
        "phone": "0123456789",
        "hire_date": "2023-01-15",
        "department_id": "PB001",
        "department_name": "IT",
        "job_id": "CV001",
        "job_title": "Development Web",
        "base_salary": 10000000,
        "status": "Đang làm việc",
    },
    {
        "employee_id": "NV002",
        "first_name": "Thị C",
        "last_name": "Trần",
        "full_name": "Trần Thị C",
        "email": "ttc@example.com",
        "phone": "0987654321",
        "hire_date": "2022-06-20",
        "department_id": "PB002",
        "department_name": "HR",
        "job_id": "CV002",
        "job_title": "Quản lý",
        "base_salary": 15000000,
        "status": "Đang làm việc",
    },
    {
        "employee_id": "NV003",
        "first_name": "Hồng D",
        "last_name": "Lê",
        "full_name": "Lê Hồng D",
        "email": "lhd@example.com",
        "phone": "0912345678",
        "hire_date": "2021-09-10",
        "department_id": "PB001",
        "department_name": "IT",
        "job_id": "CV003",
        "job_title": "Tester",
        "base_salary": 12000000,
        "status": "Đang làm việc",
    },
    {
        "employee_id": "NV004",
        "first_name": "Minh E",
        "last_name": "Phạm",
        "full_name": "Phạm Minh E",
        "email": "pme@example.com",
        "phone": "0932145678",
        "hire_date": "2023-03-25",
        "department_id": "PB003",
        "department_name": "Marketing",
        "job_id": "CV004",
        "job_title": "Content Creator",
        "base_salary": 9000000,
        "status": "Nghỉ việc",
    },
]
reports = [
        {"role": "Nhân viên", "total": 50, "newEmployees": 10, "resignedEmployees": 2, "departments": "Kinh doanh"},
        {"role": "Quản lý", "total": 15, "newEmployees": 3, "resignedEmployees": 1, "departments": "Nhân sự"},
        {"role": "Giám đốc", "total": 5, "newEmployees": 1, "resignedEmployees": 0, "departments": "Ban điều hành"},
    ]
# Tuyến render template
@app.route('/employee_HR')
def employee_HR():
    return render_template('employee_HR.html', employees=employees)

#home hiring
@app.route('/hiring')
def home_HR():
    return render_template('home_HR.html')

# Tuyến API để trả về dữ liệu JSON
@app.route('/api/employees', methods=['GET'])
def get_employees():
    callback = request.args.get('callback')
    if callback:
        # Trả về dữ liệu theo định dạng JSONP
        return f"{callback}({jsonify(employees).get_data(as_text=True)})"
    return jsonify(employees)

@app.route('/api/employees/<employee_id>', methods=['GET'])
def get_employee(employee_id):
    employee = next((emp for emp in employees if emp['employee_id'] == employee_id), None)
    if employee:
        return jsonify(employee)
    return jsonify({"error": "Nhân viên không tồn tại"}),
# API để thêm nhân viên
@app.route('/api/employees', methods=['POST'])
def add_employee():
    data = request.get_json()
    new_employee = {
        "employee_id": "NV" + str(random.randint(100, 999)),
        "first_name": data['first_name'],
        "last_name": data['last_name'],
        "email": data['email'],
        "phone": data['phone'],
        "hire_date": data['hire_date'],
        "department_name": data['department_name'],
        "job_title": data['job_title'],
        "base_salary": data['base_salary'],
        "status": data['status']
    }
    employees.append(new_employee)
    return jsonify(new_employee)

# API để cập nhật nhân viên
@app.route('/api/employees/<employee_id>', methods=['PUT'])
def update_employee(employee_id):
    data = request.get_json()
    for employee in employees:
        if employee['employee_id'] == employee_id:
            employee.update({
                "first_name": data['first_name'],
                "last_name": data['last_name'],
                "email": data['email'],
                "phone": data['phone'],
                "hire_date": data['hire_date'],
                "department_name": data['department_name'],
                "job_title": data['job_title'],
                "base_salary": data['base_salary'],
                "status": data['status']
            })
            return jsonify(employee)
    return jsonify({"error": "Employee not found"}), 404

# API để xóa nhân viên
@app.route('/api/employees/<employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    global employees
    employees = [emp for emp in employees if emp['employee_id'] != employee_id]
    return jsonify({"success": True})

# Route để render trang VC va PB
@app.route('/depart_pos')
def depart_pos():
    return render_template('depart_pos.html', jobs=jobs, departments=departments)

# API để lấy danh sách nhân viên theo job_id
@app.route('/api/employees_by_job/<job_id>')
def employees_by_job(job_id):
    filtered_employees = [emp for emp in employees if emp['job_id'] == job_id]
    return jsonify(filtered_employees)

# API để lấy danh sách nhân viên theo department_id
@app.route('/api/employees_by_department/<department_id>')
def employees_by_department(department_id):
    filtered_employees = [emp for emp in employees if emp['department_id'] == department_id]
    return jsonify(filtered_employees)

# API để thêm chức vụ
@app.route('/api/add_job', methods=['POST'])
def add_job():
    job_title = request.form.get('job_title')
    job_id = "CV" + str(random.randint(100, 999))
    new_job = {"job_id": job_id, "job_title": job_title}
    jobs.append(new_job)
    return jsonify(new_job)

# API để thêm phòng ban
@app.route('/api/add_department', methods=['POST'])
def add_department():
    department_name = request.form.get('department_name')
    department_id = "PB" + str(random.randint(100, 999))
    new_department = {"department_id": department_id, "department_name": department_name}
    departments.append(new_department)
    return jsonify(new_department)

# API để xóa chức vụ
@app.route('/api/delete_job/<job_id>', methods=['DELETE'])
def delete_job(job_id):
    global jobs
    jobs = [pos for pos in jobs if pos['job_id'] != job_id]
    return jsonify({"success": True})

# API để xóa phòng ban
@app.route('/api/delete_department/<department_id>', methods=['DELETE'])
def delete_department(department_id):
    global departments
    departments = [dept for dept in departments if dept['department_id'] != department_id]
    return jsonify({"success": True})
# API để chạt báo cáo
@app.route('/reports_HR')
def reports_HR():
    return render_template("reports_HR.html",reports=reports)

 ############################################################################################################################################


@app.route('/home_AD')
def dashboard_AD():
    data = {
        "totalEmployees": 152,
        "newEmployees": 12,
        "resignedEmployees": 3,
        "departments": 8,
        "deptDistribution": {
            "IT": 40,
            "HR": 30,
            "Marketing": 25,
            "Operations": 35,
            "Finance": 22,
        },
        "growthData": [120, 125, 130, 140, 152]  # Dữ liệu tăng trưởng qua các tháng
    }
    return render_template('dashboard_AD.html', data=data)
    

@app.route('/activity-log_AD')
def activity_log_AD():
    activity_logs = [
        {"time": "23/03/2025 10:30", "user": "Nguyễn Văn A", "role": "Admin", "action": "Đăng nhập"},
        {"time": "22/03/2025 15:20", "user": "Trần Thị B", "role": "Accountant", "action": "Cập nhật lương"},
        {"time": "21/03/2025 09:10", "user": "Lê Văn C", "role": "Admin", "action": "Xóa tài khoản"},
    ]

    return render_template('activity_log_AD.html', activity_logs=activity_logs)


@app.route('/notifications_AD')
def notifications_AD():
    notifications = [
    {
        "title": "Thông báo lương tháng 3/2025",
        "status": "sent",
        "recipients": "Tất cả nhân viên (120)",
        "content": "Bảng lương tháng 3 đã được phát hành. Vui lòng kiểm tra và xác nhận.",
        "timestamp": "28/03/2025 10:15"
    },
    {
        "title": "Thông báo cập nhật chính sách lương",
        "status": "sent",
        "recipients": "Phòng IT, Phòng Marketing (60)",
        "content": "Chính sách lương mới sẽ được áp dụng từ tháng 4/2025. Chi tiết vui lòng xem tại đây.",
        "timestamp": "15/03/2025 14:30"
    },
    {
        "title": "Thông báo điều chỉnh lương cho nhân viên kinh doanh",
        "status": "draft",
        "recipients": "Phòng Kinh doanh (45)",
        "content": "Điều chỉnh chế độ thưởng doanh số cho nhân viên kinh doanh từ tháng 4/2025.",
        "timestamp": "20/03/2025 09:45"
    }]
    return render_template("notifications_AD.html",notifications=notifications)


@app.route('/update-user-role')
def update_user_role():
    return render_template('update_user_role.html')

#Trang hiển thị phân quyền người dùng 
@app.route('/user-roles')
def user_roles():
    # Lấy tất cả dữ liệu từ bảng UserAccount trong database 'user'
    users = UserAccount.query.all()
    
    # Chuyển đổi dữ liệu thành định dạng phù hợp để hiển thị
    user_list = [
        {
            "user_id": user.account_id,
            "username": user.username,
            "role": user.role_name,
            "employee_name": user.employee_name  # Thêm tên nhân viên nếu cần
        }
        for user in users
    ]
    
    # Trả về template với dữ liệu thực tế
    return render_template('user_roles_AD.html', users=user_list)


# Route render trang báo cáo và truyền dữ liệu vào template
@app.route('/reports_AD')
def reports_AD():
    # Dữ liệu mẫu cho báo cáo nhân sự
    reports_data = [
        {"role": "Nhân viên", "total": 50, "newEmployees": 10, "resignedEmployees": 2, "departments": "Kinh doanh"},
        {"role": "Quản lý", "total": 15, "newEmployees": 3, "resignedEmployees": 1, "departments": "Nhân sự"},
        {"role": "Giám đốc", "total": 5, "newEmployees": 1, "resignedEmployees": 0, "departments": "Ban điều hành"},
    ]

    return render_template('reports_AD.html', reports=reports_data)

@app.route('/shareholder')
def shareholder():
    # Dữ liệu giả 
    shareholders = [
        {"id": 1, "FullName": "Nguyễn Văn A", "Email": "a@gmail.com", "PhoneNumber": "0987654321", "InvestmentAmount": 50000000},
        {"id": 2, "FullName": "Trần Thị B", "Email": "b@gmail.com", "PhoneNumber": "0976543210", "InvestmentAmount": 75000000},
        {"id": 3, "FullName": "Lê Văn C", "Email": "c@gmail.com", "PhoneNumber": "0965432109", "InvestmentAmount": 100000000},
    ]
    
    return render_template('shareholder_list.html', shareholders=shareholders)


@app.route('/shareholder/<int:id>')
def shareholder_detail(id):
    shareholders = [
        {"id": 1, "FullName": "Nguyễn Văn A", "Email": "a@gmail.com", "PhoneNumber": "0987654321", "InvestmentAmount": 50000000, "IsEmployee": "Có", "EmployeeID": 101},
        {"id": 2, "FullName": "Trần Thị B", "Email": "b@gmail.com", "PhoneNumber": "0976543210", "InvestmentAmount": 75000000, "IsEmployee": "Không", "EmployeeID": None},
        {"id": 3, "FullName": "Lê Văn C", "Email": "c@gmail.com", "PhoneNumber": "0965432109", "InvestmentAmount": 100000000, "IsEmployee": "Có", "EmployeeID": 103},
    ]
    # Tìm cổ đông có ID tương ứng
    shareholder = next((s for s in shareholders if s["id"] == id), None)

    if shareholder:
        return render_template('shareholder_detail.html', shareholder=shareholder)
    else:
        return "Không tìm thấy cổ đông!", 404
    
##########################################################################################################################################
@app.route("/logout")
def logout():
    # Xóa dữ liệu phiên đăng nhập (nếu có)
    #session.pop("user", None)
    return redirect(url_for('home'))
    
if __name__ == '__main__':
    app.run(debug=True)