from flask import Flask, render_template, jsonify, request
import random

app = Flask(__name__)

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
def employee_hr():
    return render_template('employee_HR.html', employees=employees)

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
if __name__ == '__main__':
    app.run(debug=True)
    