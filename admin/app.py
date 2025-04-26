
from flask import Flask, render_template,jsonify 

app = Flask(__name__)
conn_str = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=localhost;"
    "Database=HUMAN_2025;"
    "Trusted_Connection=yes;"
)

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
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    # Tổng số nhân viên
    cursor.execute("SELECT COUNT(*) FROM Employees")
    totalEmployees = cursor.fetchone()[0]

    # Nhân viên mới trong tháng gần nhất
    cursor.execute("SELECT COUNT(*) FROM Employees WHERE MONTH(HireDate) = MONTH(GETDATE()) AND YEAR(HireDate) = YEAR(GETDATE())")
    newEmployees = cursor.fetchone()[0]

    # Nhân viên nghỉ việc (giả định status = 'Inactive')
    cursor.execute("SELECT COUNT(*) FROM Employees WHERE Status = 'Inactive'")
    resignedEmployees = cursor.fetchone()[0]

    # Số lượng phòng ban
    cursor.execute("SELECT COUNT(*) FROM Departments")
    departments = cursor.fetchone()[0]

    # Phân phối nhân viên theo phòng ban
    cursor.execute("""
        SELECT D.DepartmentName, COUNT(*) AS EmployeeCount
        FROM Employees E
        JOIN Departments D ON E.DepartmentID = D.DepartmentID
        GROUP BY D.DepartmentName
    """)
    deptDistribution = {row[0]: row[1] for row in cursor.fetchall()}

    # Dữ liệu tăng trưởng (ví dụ: tổng số nhân viên qua 5 tháng gần nhất)
    cursor.execute("""
        SELECT TOP 5 FORMAT(HireDate, 'yyyy-MM') AS MonthLabel, COUNT(*) AS Hired
        FROM Employees
        GROUP BY FORMAT(HireDate, 'yyyy-MM')
        ORDER BY MonthLabel
    """)
    growthData = [row[1] for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    data = {
        "totalEmployees": totalEmployees,
        "newEmployees": newEmployees,
        "resignedEmployees": resignedEmployees,
        "departments": departments,
        "deptDistribution": deptDistribution,
        "growthData": growthData
    }

    return render_template('dashboard_AD.html', data=data)
    
#Lịch sử hoạt động admin
@app.route('/activity_log_AD')
def activity_log_AD():
   with open('data/activity_logs.json', encoding='utf-8') as f:
        activity_logs = json.load(f)
    return render_template('activity_log_AD.html', activity_logs=activity_logs)

@app.route('/logout')
def Logout():
    return render_template('logout.html')
#Thông báo 
@app.route('/notifications_AD')
def notifications_AD():
    try:
        with open('data/notifications.json', encoding='utf-8') as f:
            notifications = json.load(f)
     except FileNotFoundError:
        notifications = []  # Trường hợp không có file thì gửi danh sách trống
         
    return render_template("notifications_AD.html",notifications=notifications)

#Hiển Thị Giao Diện Cập Nhật Quyền Người Dùng
@app.route('/update_user_role')
def update_user_role():
    return render_template('update_user_role.html')
    
# API: Cập nhật quyền người dùng
@app.route('/update_user_role/<int:user_id>', methods=['POST'])
def update_user_role(user_id):
    data = request.get_json()
    if not data or 'role' not in data:
        return jsonify({'message': 'Thiếu thông tin quyền mới'}), 400

    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify({'message': 'Không tìm thấy người dùng'}), 404

    user.role = data['role']
    db.session.commit()

    return jsonify({'message': f'Đã cập nhật quyền thành công cho {user.username}'}), 200

# API: Trả danh sách người dùng
@app.route('/user_roles')
def user_roles():
    users = User.query.all()
    data = [
        {'user_id': u.user_id, 'username': u.username, 'role': u.role}
        for u in users
    ]
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
    
#Trang hiển thị phân quyền người dùng 
@app.route('/user_roles')
def user_roles():
    
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
