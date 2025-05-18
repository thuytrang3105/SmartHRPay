import mysql.connector
import bcrypt
import logging

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Thông tin kết nối CSDL
DB_USER = {'host': 'localhost', 'database': 'user_hrpay', 'user': 'root', 'password': '220204'}

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
conn = None
cursor = None

try:
    conn = mysql.connector.connect(**DB_USER)
    cursor = conn.cursor()

    for acc in accounts:
        username = acc['username']
        full_name = acc['full_name']
        email = acc['email']
        raw_password = acc['password']
        role = acc['role']
        password_hash = bcrypt.hashpw(raw_password.encode(), bcrypt.gensalt()).decode()

        # Kiểm tra trùng username
        cursor.execute("SELECT COUNT(*) FROM account WHERE Username = %s", (username,))
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO account (Username, PasswordHash, FullName, Email, Role)
                VALUES (%s, %s, %s, %s, %s)
            """, (username, password_hash, full_name, email, role))
            logging.info(f"✅ Added: {username}")
        else:
            logging.info(f"⚠️ Username exists: {username}")

    conn.commit()

except Exception as e:
    logging.error(f"❌ Error: {str(e)}")
    conn.rollback()

finally:
    cursor.close()
    conn.close()
    logging.info("🎯 Insert done!")
