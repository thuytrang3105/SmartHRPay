
from flask import Flask, render_template ,request, session

app = Flask(__name__)


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
def home_accountant():
    return render_template('home_AC.html')

@app.route('/payroll_AC')
def payroll():
    # Danh sách nhân viên với nhiều dữ liệu hơn
    payroll_data = [
        {"id": "NV001", "name": "Nguyễn Văn B", "department": "Công nghệ thông tin", "position": "senior", "base_salary": 15000000, "bonus": 2000000, "deduction": 1500000},
        {"id": "NV002", "name": "Trần Thị C", "department": "Nhân sự", "position": "manager", "base_salary": 12000000, "bonus": 1500000, "deduction": 800000},
        {"id": "NV003", "name": "Lê Văn D", "department": "Kinh doanh", "position": "team_lead", "base_salary": 14000000, "bonus": 3000000, "deduction": 1200000},
        {"id": "NV004", "name": "Phạm Thị E", "department": "Marketing", "position": "junior", "base_salary": 13000000, "bonus": 1800000, "deduction": 1000000},
        {"id": "NV005", "name": "Hoàng Minh G", "department": "Công nghệ thông tin", "position": "team_lead", "base_salary": 17000000, "bonus": 2500000, "deduction": 1400000},
        {"id": "NV006", "name": "Đặng Thị H", "department": "Nhân sự", "position": "junior", "base_salary": 11000000, "bonus": 1000000, "deduction": 500000},
        {"id": "NV007", "name": "Ngô Văn K", "department": "Kinh doanh", "position": "manager", "base_salary": 20000000, "bonus": 5000000, "deduction": 2000000},
        {"id": "NV008", "name": "Phan Văn M", "department": "Marketing", "position": "senior", "base_salary": 15500000, "bonus": 2200000, "deduction": 1100000},
        {"id": "NV009", "name": "Lương Thị O", "department": "Công nghệ thông tin", "position": "junior", "base_salary": 14000000, "bonus": 1800000, "deduction": 900000},
        {"id": "NV010", "name": "Bùi Văn P", "department": "Nhân sự", "position": "team_lead", "base_salary": 13500000, "bonus": 1700000, "deduction": 1000000},
    ]
    
    # Tính tổng lương
    for employee in payroll_data:
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

@app.route("/logout")
def logout():
    # Xóa dữ liệu phiên đăng nhập (nếu có)
    #session.pop("user", None)
    return render_template("logout_AC.html")

if __name__ == '__main__':
    app.run(debug=True)

