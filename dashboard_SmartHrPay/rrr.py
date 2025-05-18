import mysql.connector
import bcrypt
import logging

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Thông tin kết nối MySQL
DB_PAYROLL = {'host': 'localhost', 'database': 'payroll', 'user': 'root', 'password': '220204'}
DB_USER = {'host': 'localhost', 'database': 'user_hrpay', 'user': 'root', 'password': '220204'}

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
                INSERT INTO account (username, passwordHash, fullname, email, employee_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (username, passwordHash, fullname, email, emp_id))
            logging.info(f"➕ Created account for {username}")
        else:
            logging.info(f"⚠️ Account already exists for {username}")

        conn_user.commit()

except Exception as e:
    logging.error(f"❌ Error: {str(e)}")
    conn_user.rollback()

finally:
    # Đóng kết nối
    for cursor, conn in [(cursor_payroll, conn_payroll), (cursor_user, conn_user)]:
        try:
            cursor.close()
            conn.close()
        except:
            pass
    logging.info("🎉 Account creation complete!")
