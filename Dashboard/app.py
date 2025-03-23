from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def login():
    return render_template('home.html')

@app.route("/register")
def register():
    return render_template('register.html')
@app.route("/home-nv")
def home_nv():
    return render_template("home_nv.html")
@app.route("/salary-nv")
def salary_nv():
    return render_template("salary_nv.html")

@app.route('/employees')
def employee_list():
    employees = [
        {"id": "EMP001", "name": "Nguyễn Văn A", "position": "Nhân viên IT", "department": "Công nghệ", "email": "a@example.com", "status": "Đang làm việc"},
        {"id": "EMP002", "name": "Trần Thị B", "position": "Kế toán", "department": "Tài chính", "email": "b@example.com", "status": "Đang làm việc"},
        {"id": "EMP003", "name": "Lê Văn C", "position": "Nhân sự", "department": "Hành chính", "email": "c@example.com", "status": "Nghỉ việc"}
    ]
    return render_template('employee_list_detail.html', employees=employees)

@app.route('/employees/<id>')
def employee_detail(id):
    employees = {
        "EMP001": {"id": "EMP001", "name": "Nguyễn Văn A", "gender": "Nam", "dob": "10/05/1990", "address": "123 Đường ABC, TP. HCM",
                    "position": "Nhân viên IT", "department": "Công nghệ", "hire_date": "01/01/2020", "work_shift": "Sáng", "contract_type": "Chính thức",
                    "salary": 15000000, "bonus": 2000000, "deductions": 500000, "net_salary": 16500000},
        "EMP002": {"id": "EMP002", "name": "Trần Thị B", "gender": "Nữ", "dob": "15/07/1995", "address": "456 Đường XYZ, TP. HCM",
                    "position": "Kế toán", "department": "Tài chính", "hire_date": "15/03/2021", "work_shift": "Chiều", "contract_type": "Chính thức",
                    "salary": 12000000, "bonus": 1500000, "deductions": 300000, "net_salary": 13200000},
        "EMP003": {"id": "EMP003", "name": "Lê Văn C", "gender": "Nam", "dob": "22/11/1988", "address": "789 Đường LMN, Hà Nội",
                    "position": "Nhân sự", "department": "Hành chính", "hire_date": "10/06/2018", "work_shift": "Sáng", "contract_type": "Hợp đồng",
                    "salary": 10000000, "bonus": 1000000, "deductions": 200000, "net_salary": 10800000}
    }
    employee = employees.get(id)
    if not employee:
        return "Nhân viên không tồn tại", 404
    return render_template('employee_detail.html', employee=employee)

if __name__ == '__main__':
    app.run(debug=True)

