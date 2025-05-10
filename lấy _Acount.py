import mysql.connector
import bcrypt
import logging

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Thông tin kết nối MySQL
DB_PAYROLL = {'host': 'localhost', 'database': 'payroll', 'user': 'root', 'password': '123456123456'}
DB_USER = {'host': 'localhost', 'database': 'user_hrpay', 'user': 'root', 'password': '123456123456'}

accounts = [
    {
        'username': 'admin',
        'full_name': 'System Administrator',
        'email': 'admin@company.com',
        'password': 'admin123',
        'role': 'Admin'
    },
    {
        'username': 'hr',
        'full_name': 'HR Manager',
        'email': 'hr@company.com',
        'password': 'hr123',
        'role': 'HR'
    },
    {
        'username': 'accounting',
        'full_name': 'Accounting Manager',
        'email': 'accounting@company.com',
        'password': 'accounting123',
        'role': 'Accounting'
    },
    {
        'username': 'locked_user',
        'full_name': 'Locked User',
        'email': 'locked@company.com',
        'password': 'locked123',
        'role': 'Employee'
    }
]

try:
    # Kết nối MySQL
    conn_payroll = mysql.connector.connect(**DB_PAYROLL)
    conn_user = mysql.connector.connect(**DB_USER)

    cursor_payroll = conn_payroll.cursor(dictionary=True)
    cursor_user = conn_user.cursor()

    logging.info("✅ Connected to MySQL databases!")

    # Lấy danh sách nhân viên active từ payroll.employees
    cursor_payroll.execute("""
        SELECT employee_id, first_name, last_name, email
        FROM employees
        WHERE status = 'active'
    """)
    employees = cursor_payroll.fetchall()

    # Xử lý các tài khoản hệ thống và thông tin nhân viên
    for emp in employees:
        emp_id = emp['employee_id']
        fullname = f"{emp['first_name']} {emp['last_name']}"
        email = emp['email']
        username = f"{emp['first_name'].lower()}_{emp_id}"

        # Băm mật khẩu mặc định
        raw_password = "123456"
        passwordHash = bcrypt.hashpw(raw_password.encode(), bcrypt.gensalt()).decode()

        # Kiểm tra tài khoản đã tồn tại chưa
        cursor_user.execute("SELECT COUNT(*) FROM account WHERE username = %s", (username,))
        if cursor_user.fetchone()[0] == 0:
            cursor_user.execute("""
                INSERT INTO account (username, passwordHash, fullname, email, employee_id, role)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (username, passwordHash, fullname, email, emp_id, 'Employee'))  # Assigning default 'Employee' role
            logging.info(f"➕ Created account for {username}")
        else:
            logging.info(f"⚠️ Account already exists for {username}")

    # Xử lý các tài khoản hệ thống (admin, hr, accounting)
    for acc in accounts:
        username = acc['username']
        full_name = acc['full_name']
        email = acc['email']
        raw_password = acc['password']
        role = acc['role']
        password_hash = bcrypt.hashpw(raw_password.encode(), bcrypt.gensalt()).decode()

        # Kiểm tra trùng username
        cursor_user.execute("SELECT COUNT(*) FROM account WHERE username = %s", (username,))
        if cursor_user.fetchone()[0] == 0:
            cursor_user.execute("""
                INSERT INTO account (username, passwordHash, fullname, email, role)
                VALUES (%s, %s, %s, %s, %s)
            """, (username, password_hash, full_name, email, role))
            logging.info(f"✅ Added: {username}")
        else:
            logging.info(f"⚠️ Username exists: {username}")

    conn_user.commit()

except Exception as e:
    logging.error(f"❌ Error: {str(e)}")
    conn_user.rollback()

finally:
    cursor_payroll.close()
    cursor_user.close()
    conn_payroll.close()
    conn_user.close()
    logging.info("🎯 Process complete!")
