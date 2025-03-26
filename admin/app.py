
from flask import Flask, render_template,jsonify 

app = Flask(__name__)

@app.route('/')
def Admin():
    return render_template('home_AD.html')
@app.route('/HR')
def home_HR ():
    return render_template('home_HR.html')
@app.route('/AC')
def home_AC ():
    return render_template('home_AC.html')

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

@app.route('/logout')
def Logout():
    return render_template('logout.html')

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

if __name__ == '__main__':
    app.run(debug=True)
