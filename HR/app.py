from flask import Flask, render_template, jsonify, request
import random
import json

app = Flask(__name__)

# Dữ liệu mẫu (có thể thay bằng database thực tế)
# Cập nhật danh sách jobs
jobs = [
    {"job_id": "CV001", "job_title": "Nhân viên"},
    {"job_id": "CV002", "job_title": "Quản lý"},
    {"job_id": "CV003", "job_title": "Tester"},
    {"job_id": "CV004", "job_title": "Content Creator"},
]

# Cập nhật danh sách departments
departments = [
    {"department_id": "PB001", "department_name": "IT"},
    {"department_id": "PB002", "department_name": "HR"},
    {"department_id": "PB003", "department_name": "Marketing"},
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

# Dữ liệu mẫu tuyển dụng
recruitments = [
    {
        "id": 1,
        "title": "Kỹ sư phần mềm",
        "department": "Phòng Công nghệ",
        "posted_date": "2025/02/04",
        "status": "Đang tuyển",
        "description": "Phát triển và bảo trì các ứng dụng web sử dụng JavaScript, Python và các công nghệ hiện đại.",
        "requirements": [
            "Tối thiểu 2 năm kinh nghiệm lập trình",
            "Thành thạo JavaScript, Python",
            "Kinh nghiệm với các framework như React, Flask",
            "Có khả năng làm việc nhóm tốt"
        ],
        "applicants": [
            {"name": "Nguyễn Văn A", "email": "nguyenvana@example.com"},
            {"name": "Trần Thị B", "email": "tranthib@example.com"}
        ]
    },
    {
        "id": 2,
        "title": "Nhân viên marketing",
        "department": "Phòng Marketing",
        "posted_date": "2025/04/10",
        "status": "Đang tuyển",
        "description": "Lập kế hoạch và thực hiện các chiến dịch marketing online để tăng nhận diện thương hiệu.",
        "requirements": [
            "Tốt nghiệp đại học chuyên ngành Marketing",
            "Hiểu biết về Digital Marketing",
            "Kỹ năng viết nội dung tốt",
            "Có kinh nghiệm quản lý mạng xã hội"
        ],
        "applicants": []
    }
]

reports = [
    {"role": "Nhân viên", "total": 50, "newEmployees": 10, "resignedEmployees": 2, "departments": "Kinh doanh"},
    {"role": "Quản lý", "total": 15, "newEmployees": 3, "resignedEmployees": 1, "departments": "Nhân sự"},
    {"role": "Giám đốc", "total": 5, "newEmployees": 1, "resignedEmployees": 0, "departments": "Ban điều hành"},
]

# Tạo file JSON mẫu nếu chưa tồn tại
def create_json_files():
    try:
        with open('employees.json', 'w', encoding='utf-8') as file:
            json.dump(employees, file, ensure_ascii=False, indent=2)
        
        # Tạo file chi tiết nhân viên nếu chưa tồn tại
        employee_details = [
            {
                "employee_id": "NV001",
                "gender": "Nam",
                "dob": "1990-05-15",
                "address": "123 Đường ABC, Quận 1, TP HCM",
                "work_shift": "Giờ hành chính",
                "contract_type": "Hợp đồng dài hạn",
                "bonus": 1000000,
                "deductions": 200000
            },
            {
                "employee_id": "NV002",
                "gender": "Nữ",
                "dob": "1992-08-20",
                "address": "456 Đường XYZ, Quận 2, TP HCM",
                "work_shift": "Giờ hành chính",
                "contract_type": "Hợp đồng dài hạn",
                "bonus": 1500000,
                "deductions": 300000
            }
        ]
        
        with open('employee_details.json', 'w', encoding='utf-8') as file:
            json.dump(employee_details, file, ensure_ascii=False, indent=2)
            
    except Exception as e:
        print(f"Error creating JSON files: {str(e)}")

###################################### HOME HIRING ########################################
@app.route('/hiring')
def hiring():
    return render_template('home_HR.html')

@app.route('/employee_HR')
def employee_HR():
    return render_template('employee_HR.html', employees=employees)

# Tuyến API để trả về dữ liệu JSON
@app.route('/api/employees', methods=['GET'])
def get_employees():
    try:
        callback = request.args.get('callback')
        if callback:
            # Trả về dữ liệu theo định dạng JSONP
            return f"{callback}({jsonify(employees).get_data(as_text=True)})"
        return jsonify(employees)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/employees/<employee_id>', methods=['GET'])
def get_employee(employee_id):
    try:
        employee = next((emp for emp in employees if emp['employee_id'] == employee_id), None)
        if employee:
            return jsonify(employee)
        return jsonify({"error": "Nhân viên không tồn tại"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API để thêm nhân viên
@app.route('/api/employees', methods=['POST'])
def add_employee():
    try:
        data = request.get_json()
        new_employee = {
            "employee_id": "NV" + str(random.randint(100, 999)),
            "first_name": data['first_name'],
            "last_name": data['last_name'],
            "full_name": data['last_name'] + " " + data['first_name'],
            "email": data['email'],
            "phone": data['phone'],
            "hire_date": data['hire_date'],
            "department_id": data.get('department_id', ''),
            "department_name": data['department_name'],
            "job_id": data.get('job_id', ''),
            "job_title": data['job_title'],
            "base_salary": data['base_salary'],
            "status": data['status']
        }
        employees.append(new_employee)
        
        # Cập nhật file JSON
        try:
            with open('employees.json', 'w', encoding='utf-8') as file:
                json.dump(employees, file, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Warning: Could not update employees.json: {str(e)}")
            
        return jsonify(new_employee)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API để cập nhật nhân viên
@app.route('/api/employees/<employee_id>', methods=['PUT'])
def update_employee(employee_id):
    try:
        data = request.get_json()
        for employee in employees:
            if employee['employee_id'] == employee_id:
                employee.update({
                    "first_name": data['first_name'],
                    "last_name": data['last_name'],
                    "full_name": data['last_name'] + " " + data['first_name'],
                    "email": data['email'],
                    "phone": data['phone'],
                    "hire_date": data['hire_date'],
                    "department_name": data['department_name'],
                    "job_title": data['job_title'],
                    "base_salary": data['base_salary'],
                    "status": data['status']
                })
                
                # Cập nhật file JSON
                try:
                    with open('employees.json', 'w', encoding='utf-8') as file:
                        json.dump(employees, file, ensure_ascii=False, indent=2)
                except Exception as e:
                    print(f"Warning: Could not update employees.json: {str(e)}")
                    
                return jsonify(employee)
        return jsonify({"error": "Employee not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API để xóa nhân viên
@app.route('/api/employees/<employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    try:
        global employees
        employees = [emp for emp in employees if emp['employee_id'] != employee_id]
        
        # Cập nhật file JSON
        try:
            with open('employees.json', 'w', encoding='utf-8') as file:
                json.dump(employees, file, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Warning: Could not update employees.json: {str(e)}")
            
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API route để lấy chi tiết đầy đủ của một nhân viên
@app.route('/api/employees/detail/<employee_id>', methods=['GET'])
def get_employee_detail(employee_id):
    try:
        employee = next((emp for emp in employees if emp['employee_id'] == employee_id), None)
        
        if not employee:
            return jsonify({"error": "Không tìm thấy nhân viên"}), 404
            
        # Sau đó lấy thêm chi tiết (từ file nếu có hoặc tạo dữ liệu mẫu)
        try:
            with open('employee_details.json', 'r', encoding='utf-8') as detail_file:
                details = json.load(detail_file)
                employee_detail = next((detail for detail in details if detail['employee_id'] == employee_id), {})
        except Exception:
            employee_detail = {}
        
        # Kết hợp thông tin
        full_employee = {**employee, **employee_detail}
        if 'gender' not in full_employee:
            full_employee['gender'] = None
        if 'dob' not in full_employee:
            full_employee['dob'] = None
        if 'address' not in full_employee:
            full_employee['address'] = None
        if 'work_shift' not in full_employee:
            full_employee['work_shift'] = 'Giờ hành chính'
        if 'contract_type' not in full_employee:
            full_employee['contract_type'] = 'Hợp đồng dài hạn'
        if 'bonus' not in full_employee:
            full_employee['bonus'] = 0
        if 'deductions' not in full_employee:
            full_employee['deductions'] = 0
        
        return jsonify(full_employee)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API route để cập nhật chi tiết nhân viên
@app.route('/api/employees/detail/<employee_id>', methods=['PUT'])
def update_employee_detail(employee_id):
    try:
        data = request.json
        
        # Cập nhật thông tin cơ bản
        employee_index = next((i for i, emp in enumerate(employees) if emp['employee_id'] == employee_id), None)
        if employee_index is None:
            return jsonify({"error": "Không tìm thấy nhân viên"}), 404
            
        # Cập nhật các thông tin cơ bản
        basic_fields = ['first_name', 'last_name', 'email', 'phone', 
                       'hire_date', 'department_name', 'job_title', 
                       'base_salary', 'status']
        
        for field in basic_fields:
            if field in data:
                employees[employee_index][field] = data[field]
        
        if 'first_name' in data and 'last_name' in data:
            employees[employee_index]['full_name'] = data['last_name'] + " " + data['first_name']
                
        # Lưu thông tin cơ bản
        try:
            with open('employees.json', 'w', encoding='utf-8') as file:
                json.dump(employees, file, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Warning: Could not update employees.json: {str(e)}")
            
        # Cập nhật chi tiết nhân viên
        try:
            with open('employee_details.json', 'r', encoding='utf-8') as file:
                details = json.load(file)
                
            detail_index = next((i for i, d in enumerate(details) if d['employee_id'] == employee_id), None)
            
            detail_fields = ['gender', 'dob', 'address', 'work_shift', 
                           'contract_type', 'bonus', 'deductions']
            
            detail_data = {
                'employee_id': employee_id
            }
            
            for field in detail_fields:
                if field in data:
                    detail_data[field] = data[field]
            
            if detail_index is not None:
                # Cập nhật chi tiết hiện có
                for field, value in detail_data.items():
                    details[detail_index][field] = value
            else:
                # Thêm chi tiết mới
                details.append(detail_data)
                
            # Lưu thông tin chi tiết
            with open('employee_details.json', 'w', encoding='utf-8') as file:
                json.dump(details, file, ensure_ascii=False, indent=2)
                
        except FileNotFoundError:
            # Tạo file chi tiết nếu chưa tồn tại
            details = [detail_data]
            with open('employee_details.json', 'w', encoding='utf-8') as file:
                json.dump(details, file, ensure_ascii=False, indent=2)
        
        return jsonify({"success": True, "message": "Đã cập nhật thông tin nhân viên"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API route hiển thị trang chi tiết nhân viên (nếu cần)
@app.route('/employee_detail/<employee_id>')
def employee_detail(employee_id):
    return render_template('employee_detail.html', employee_id=employee_id)

####################################### ROUTE ĐỂ RENDER TRANG CV VÀ PB ######################################
@app.route('/depart_pos')
def depart_pos():
    return render_template('depart_pos.html', jobs=jobs, departments=departments)

# API để lấy danh sách nhân viên theo job_id
@app.route('/api/employees_by_job/<job_id>')
def employees_by_job(job_id):
    try:
        filtered_employees = [emp for emp in employees if emp['job_id'] == job_id]
        return jsonify(filtered_employees), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API để lấy danh sách nhân viên theo department_id
@app.route('/api/employees_by_department/<department_id>')
def employees_by_department(department_id):
    try:
        filtered_employees = [emp for emp in employees if emp['department_id'] == department_id]
        return jsonify(filtered_employees), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API để thêm chức vụ
@app.route('/api/add_job', methods=['POST'])
def add_job():
    try:
        job_title = request.form.get('job_title')
        job_id = "CV" + str(random.randint(100, 999))
        new_job = {"job_id": job_id, "job_title": job_title}
        jobs.append(new_job)
        return jsonify(new_job), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API để cập nhật chức vụ
@app.route('/api/update_job/<job_id>', methods=['POST'])
def update_job(job_id):
    try:
        job_title = request.form.get('job_title')
        for job in jobs:
            if job['job_id'] == job_id:
                job['job_title'] = job_title
                return jsonify(job), 200
        return jsonify({"error": "Job not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API để xóa chức vụ
@app.route('/api/delete_job/<job_id>', methods=['DELETE'])
def delete_job(job_id):
    try:
        global jobs
        original_length = len(jobs)
        jobs = [job for job in jobs if job['job_id'] != job_id]
        if len(jobs) == original_length:
            return jsonify({"success": False, "message": "Job not found"}), 404
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API để thêm phòng ban
@app.route('/api/add_department', methods=['POST'])
def add_department():
    try:
        department_name = request.form.get('department_name')
        department_id = "PB" + str(random.randint(100, 999))
        new_department = {"department_id": department_id, "department_name": department_name}
        departments.append(new_department)
        return jsonify(new_department), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API để cập nhật phòng ban
@app.route('/api/update_department/<department_id>', methods=['POST'])
def update_department(department_id):
    try:
        department_name = request.form.get('department_name')
        for dept in departments:
            if dept['department_id'] == department_id:
                dept['department_name'] = department_name
                return jsonify(dept), 200
        return jsonify({"error": "Department not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API để xóa phòng ban
@app.route('/api/delete_department/<department_id>', methods=['DELETE'])
def delete_department(department_id):
    try:
        global departments
        original_length = len(departments)
        departments = [dept for dept in departments if dept['department_id'] != department_id]
        if len(departments) == original_length:
            return jsonify({"success": False, "message": "Department not found"}), 404
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

######################################## RENDER QUẢN LÍ TUYỂN DỤNG ########################################
# Lấy tất cả vị trí tuyển dụng
@app.route('/api/recruitments', methods=['GET'])
def get_all_recruitments():
    return jsonify(recruitments)

# Lấy chi tiết một vị trí tuyển dụng
@app.route('/api/recruitments/<int:recruitment_id>', methods=['GET'])
def get_recruitment(recruitment_id):
    recruitment = next((r for r in recruitments if r["id"] == recruitment_id), None)
    if recruitment:
        return jsonify(recruitment)
    return jsonify({"error": "Không tìm thấy vị trí tuyển dụng"}), 404

# Cập nhật vị trí tuyển dụng
@app.route('/api/recruitments/<int:recruitment_id>', methods=['PUT'])
def update_recruitment(recruitment_id):
    data = request.json
    recruitment = next((r for r in recruitments if r["id"] == recruitment_id), None)
    
    if recruitment:
        recruitment.update(data)
        return jsonify(recruitment)
    return jsonify({"error": "Không tìm thấy vị trí tuyển dụng"}), 404

# Xóa vị trí tuyển dụng
@app.route('/api/recruitments/<int:recruitment_id>', methods=['DELETE'])
def delete_recruitment(recruitment_id):
    global recruitments
    recruitment = next((r for r in recruitments if r["id"] == recruitment_id), None)
    
    if recruitment:
        recruitments = [r for r in recruitments if r["id"] != recruitment_id]
        return jsonify({"message": f"Đã xoá vị trí '{recruitment['title']}'"})
    return jsonify({"error": "Không tìm thấy vị trí tuyển dụng"}), 404

# Thêm vị trí tuyển dụng mới
@app.route('/api/recruitments', methods=['POST'])
def add_recruitment():
    data = request.json
    new_id = max(r["id"] for r in recruitments) + 1 if recruitments else 1
    data["id"] = new_id
    data.setdefault("applicants", [])
    recruitments.append(data)
    return jsonify(data), 201

# Trang hiển thị danh sách vị trí tuyển dụng
@app.route('/recruitment_HR')
def recruitment_HR():
    return render_template('recruitment_HR.html')

######################################## RENDER BÁO CÁO NHÂN SỰ #######################################
@app.route('/reports_HR')
def reports_HR():
    return render_template("reports_HR.html", reports=reports)

####################################### LOG OUT #######################################
@app.route('/logout_hr')
def logout_hr():
    return render_template('home_HR.html')

if __name__ == '__main__':
    # Tạo file JSON mẫu khi khởi động ứng dụng
    create_json_files()
    app.run(debug=True)