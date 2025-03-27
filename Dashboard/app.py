from flask import Flask, render_template, request, jsonify, redirect , url_for 
from flask_sqlalchemy import SQLAlchemy
import random
import config
import datetime
app = Flask(__name__)

app.config["SQLALCHEMY_BINDS"] = {
"default": config.SQL_SERVER_CONN, # Thêm dòng này để tránh lỗi
"mysql": config.MYSQL_CONN
}
db = SQLAlchemy(app)
class LuongNhanVien(db.Model):
    __tablename__ = "LuongNhanVien"
    __bind_key__ = "mysql"
    MaLuong = db.Column(db.Integer, primary_key=True, autoincrement=True)
    MaNV = db.Column(db.Integer, db.ForeignKey("HoSoNhanVien.MaNV"))
    ThangNam = db.Column(db.Date)
    LuongCoBan = db.Column(db.Float)
    PhuCap = db.Column(db.Float)
    Thuong = db.Column(db.Float)
    KhauTru = db.Column(db.Float)
    LuongThucNhan = db.Column(db.Float)

@app.route("/")
def home ():
    return render_template('home.html')

######################################################################################################################


def get_salary_data(month, year):
    # Giả lập dữ liệu lương, có thể thay bằng truy vấn DB thực tế
    # Ví dụ: trả về dữ liệu khác nhau dựa trên tháng/năm
    if month == "3" and year == "2025":
        return {
            "base_salary": "12,000,000 VND",
            "bonus": "3,000,000 VND",
            "date": "23",
            "deductions": "400,000 VND",
            "net_salary": "14,600,000 VND"
        }
    return {
        "base_salary": "10,000,000 VND",
        "bonus": "2,000,000 VND",
        "date": "22",
        "deductions": "500,000 VND",
        "net_salary": "11,500,000 VND"
    }

def get_attendance_data(month, year):
    # Simulate attendance data based on month and year
    attendance_data = {
        "3/2025": [
            {"date": "01/03/2025", "status": "Có mặt"},
            {"date": "02/03/2025", "status": "Có mặt"},
            {"date": "03/03/2025", "status": "Vắng"},
            {"date": "04/03/2025", "status": "Nghỉ phép"},
            {"date": "05/03/2025", "status": "Có mặt"}
        ],
        "1/2020": [
            {"date": "01/01/2020", "status": "Có mặt"},
            {"date": "02/01/2020", "status": "Có mặt"},
            {"date": "03/01/2020", "status": "Vắng"},
            {"date": "04/01/2020", "status": "Nghỉ phép"}
        ],
        "8/2020": [
            {"date": "26/08/2020", "status": "Có mặt"},
            {"date": "27/08/2020", "status": "Có mặt"},
            {"date": "28/08/2020", "status": "Vắng"},
            {"date": "29/08/2020", "status": "Nghỉ"}
        ]
    }
    
    # Convert month and year to a key format
    key = f"{month}/{year}"
    
    # Return data for the specific month/year, or an empty list if not found
    return attendance_data.get(key, [])

@app.route('/api/attendance', methods=['GET'])
def fetch_attendance_data():
    month = request.args.get('month', '1')
    year = request.args.get('year', '2020')
    
    try:
        attendance_data = get_attendance_data(month, year)
        return jsonify(attendance_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
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
        "status": "Có mặt"
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
    
    selected_month = "1"
    selected_year = "2020"
    attendance = get_attendance_data("selected_month", "selected_year")

    return render_template("home_nv.html", employee=employee, notifications=notifications, salary=salary,attendance=attendance, selected_month=selected_month, selected_year=selected_year)

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
    # Danh sách nhân viên với nhiều dữ liệu hơn
    payroll_data = [
        ({"payroll_id":"B001"},{"employee_id": "NV001", "employee_name": "Nguyễn Văn B", "department_name": "Công nghệ thông tin", "job_title": "senior", "base_salary": 15000000, "bonus": 2000000, "deduction": 1500000},),
        ({"payroll_id":"B002"},{"employee_id": "NV002", "employee_name": "Trần Thị C", "department_name": "Nhân sự", "job_title": "manager", "base_salary": 12000000, "bonus": 1500000, "deduction": 800000},),
        ({"payroll_id":"B003"},{"employee_id": "NV003", "employee_name": "Lê Văn D", "department_name": "Kinh doanh", "job_title": "team_lead", "base_salary": 14000000, "bonus": 3000000, "deduction": 1200000},),
        ({"payroll_id":"B004"},{"employee_id": "NV004", "employee_name": "Phạm Thị E", "department_name": "Marketing", "job_title": "junior", "base_salary": 13000000, "bonus": 1800000, "deduction": 1000000},),
        ({"payroll_id":"B005"},{"employee_id": "NV005", "employee_name": "Hoàng Minh G", "department_name": "Công nghệ thông tin", "job_title": "team_lead", "base_salary": 17000000, "bonus": 2500000, "deduction": 1400000},),
        ({"payroll_id":"B006"},{"employee_id": "NV006", "employee_name": "Đặng Thị H", "department_name": "Nhân sự", "job_title": "junior", "base_salary": 11000000, "bonus": 1000000, "deduction": 500000},),
        ({"payroll_id":"B007"},{"employee_id": "NV007", "employee_name": "Ngô Văn K", "department_name": "Kinh doanh", "job_title": "manager", "base_salary": 20000000, "bonus": 5000000, "deduction": 2000000},),
        ({"payroll_id":"B008"},{"employee_id": "NV008", "employee_name": "Phan Văn M", "department_name": "Marketing", "job_title": "senior", "base_salary": 15500000, "bonus": 2200000, "deduction": 1100000},),
        ({"payroll_id":"B009"},{"employee_id": "NV009", "employee_name": "Lương Thị O", "department_name": "Công nghệ thông tin", "job_title": "junior", "base_salary": 14000000, "bonus": 1800000, "deduction": 900000},),
        ({"payroll_id":"B010"},{"employee_id": "NV010", "employee_name": "Bùi Văn P", "department_name": "Nhân sự", "job_title": "team_lead", "base_salary": 13500000, "bonus": 1700000, "deduction": 1000000},),
    ]
    
    # Tính tổng lương
    for payroll, employee in payroll_data:
        employee["total_salary"] = employee["base_salary"] + employee["bonus"] - employee["deduction"]

    # Nhận giá trị lọc từ request
    selected_department = request.args.get("department", "").lower()
    selected_position = request.args.get("position", "").lower()

    # Lọc dữ liệu
    filtered_data = [
        emp for emp in payroll_data
        if (not selected_department or emp["department"].lower() == selected_department)
        and (not selected_position or emp["position"].lower() == selected_position)
    ]

    return render_template(
        'payroll_AC.html', 
        payroll_data=filtered_data, 
        selected_department=selected_department, 
        selected_position=selected_position
    )

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
@app.route('/attendance_AC')
def attendance_AC():
    # Dữ liệu mẫu
    attendances = [
        {"attendance_id": "CC001", "employee_id": "NV001", "employee_name": "Nguyễn Văn A", "date": "2025-03-27", "status": "Có mặt"},
        {"attendance_id": "CC002", "employee_id": "NV002", "employee_name": "Nguyễn Văn B", "date": "2025-03-27", "status": "Vắng"},
        {"attendance_id": "CC003", "employee_id": "NV003", "employee_name": "Nguyễn Văn C", "date": "2025-03-27", "status": "Nghỉ"}
    ]
    
    current_date = datetime.datetime.now().strftime('%Y-%m-%d')
    

    return render_template(
        'attendance_AC.html',
        attendances=attendances,
        current_date=current_date,
        current_year=datetime.datetime.now().year
    )

@app.route('/api/attendance_detail')
def attendance_detail():
    employee_id = request.args.get('employee_id')
    month = request.args.get('month')
    year = request.args.get('year')
    sample_details = {
        "NV001": [
            {"date": f"{year}-{month.zfill(2)}-01", "status": "Có mặt"},
            {"date": f"{year}-{month.zfill(2)}-02", "status": "Có mặt"},
            {"date": f"{year}-{month.zfill(2)}-03", "status": "Nghỉ"}
        ],
        "NV002": [
            {"date": f"{year}-{month.zfill(2)}-01", "status": "Vắng"},
            {"date": f"{year}-{month.zfill(2)}-02", "status": "Có mặt"},
            {"date": f"{year}-{month.zfill(2)}-03", "status": "Vắng"}
        ],
        "NV003": [
            {"date": f"{year}-{month.zfill(2)}-01", "status": "Nghỉ"},
            {"date": f"{year}-{month.zfill(2)}-02", "status": "Nghỉ"},
            {"date": f"{year}-{month.zfill(2)}-03", "status": "Có mặt"}
        ]
    }
    return jsonify(sample_details.get(employee_id, []))
    

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


@app.route('/dashboard_AD')
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
    # Dữ liệu giả (mock data)
    users = [
        {"user_id": 1, "username": "Nguyễn Văn A", "role": "Admin"},
        {"user_id": 2, "username": "Trần Thị B", "role": "Nhân viên"},
        {"user_id": 3, "username": "Lê Văn C", "role": "Quản lý"},
    ]
    
    return render_template('user_roles_AD.html', users=users) 


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