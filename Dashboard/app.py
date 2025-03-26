from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route("/")
def login():
    return render_template('home.html')

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

if __name__ == '__main__':
    app.run(debug=True)