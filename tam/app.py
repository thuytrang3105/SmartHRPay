from flask import Flask, render_template, request, redirect ,url_for

app = Flask(__name__)

# Dữ liệu giả lập
list_applicants = [
    {
        "id": 1, "FullName": "Nguyễn Văn A", "Email": "a@example.com", "PhoneNumber": "0123456789", 
        "ApplicationDate": "2024-03-01", "Status": "Pending", "JobID": 101
    },
    {
        "id": 2, "FullName": "Trần Thị B", "Email": "b@example.com", "PhoneNumber": "0987654321", 
        "ApplicationDate": "2024-02-20", "Status": "Hired", "JobID": 102
    }
]

list_shareholders = [
    {
        "id": 1, "FullName": "Lê Văn C", "Email": "c@example.com", "PhoneNumber": "0978123456", 
        "InvestmentAmount": 50000, "IsEmployee": True, "EmployeeID": 201
    },
    {
        "id": 2, "FullName": "Phạm Thị D", "Email": "d@example.com", "PhoneNumber": "0965123456", 
        "InvestmentAmount": 75000, "IsEmployee": False, "EmployeeID": None
    }
]

list_employees = [
    {
        "id": "EMP001", "name": "Nguyễn Văn A", "email": "nguyenvana@example.com",
        "gender": "Nam", "dob": "10/05/1990", "address": "123 Đường ABC, TP. HCM",
        "position": "Nhân viên IT", "department": "Công nghệ", "hire_date": "01/01/2020",
        "work_shift": "Sáng", "contract_type": "Chính thức", "salary": 15000000,
        "bonus": 2000000, "deductions": 500000, "net_salary": 16500000
    },
    {
        "id": "EMP002", "name": "Trần Thị B", "email": "tranthib@example.com",
        "gender": "Nữ", "dob": "15/07/1995", "address": "456 Đường XYZ, TP. HCM",
        "position": "Kế toán", "department": "Tài chính", "hire_date": "15/03/2021",
        "work_shift": "Chiều", "contract_type": "Chính thức", "salary": 12000000,
        "bonus": 1500000, "deductions": 300000, "net_salary": 13200000
    },
    {
        "id": "EMP003", "name": "Lê Văn C", "email": "levanc@example.com",
        "gender": "Nam", "dob": "22/11/1988", "address": "789 Đường LMN, Hà Nội",
        "position": "Nhân sự", "department": "Hành chính", "hire_date": "10/06/2018",
        "work_shift": "Sáng", "contract_type": "Hợp đồng", "salary": 10000000,
        "bonus": 1000000, "deductions": 200000, "net_salary": 10800000
    }
]



@app.route('/')
def home ():
    return render_template('home.html')

@app.route('/employees')
def employee_list():
    employees = list_employees
    return render_template('employee_list_detail.html', employees=employees)

@app.route('/employees/<id>')
def employee_detail(id):
    employee = next((e for e in list_employees if e["id"] == id), None)
    if not employee:
        return "Nhân viên không tồn tại", 404
    return render_template('employee_detail.html', employee=employee)

@app.route("/applicants")
def view_applicants():
    return render_template("applicant_list.html", applicants=list_applicants)

@app.route("/applicants/<int:id>")
def applicant_detail(id):
    applicant = next((a for a in list_applicants if a["id"] == id), None)
    return render_template("applicant_detail.html", applicant=applicant)

@app.route("/update_applicant_status/<int:id>", methods=["POST"])
def update_applicant_status(id):
    status = request.form.get("status")
    for applicant in list_applicants:
        if applicant["id"] == id:
            applicant["status"] = status
            break
    return redirect(url_for("applicant_detail", id=id))

@app.route("/shareholders")
def view_shareholders():
    return render_template("shareholder_list.html", shareholders=list_shareholders)

@app.route("/shareholders/<int:id>")
def shareholder_detail(id):
    shareholder = next((s for s in list_shareholders if s["id"] == id), None)
    return render_template("shareholder_detail.html", shareholder=shareholder)

@app.route("/update_shareholder_info/<int:id>", methods=["POST"])
def update_shareholder_info(id):
    investment_amount = request.form.get("investment_amount")
    for shareholder in list_shareholders:
        if shareholder["id"] == id:
            shareholder["investment_amount"] = investment_amount
            break
    return redirect(url_for("shareholder_detail", id=id))


if __name__ == '__main__':
    app.run(debug=True)
