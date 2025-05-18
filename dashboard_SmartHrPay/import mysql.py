import mysql.connector

# Function to connect to MySQL database
def create_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',  # Change this to your MySQL username
        password='123456123456',  # Change this to your MySQL password
        database='user_hrpay'  # Database name
    )

# Function to export data as SQL INSERT statements for a given table
def export_table_to_sql(cursor, table_name, file):
    # Fetch all the rows from the table
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()

    # Get the column names from the table
    column_names = [desc[0] for desc in cursor.description]

    # Loop through the rows and create INSERT INTO statements
    for row in rows:
        # Create the INSERT INTO statement
        values = ', '.join([f"'{str(value)}'" if value is not None else 'NULL' for value in row])
        insert_statement = f"INSERT INTO {table_name} ({', '.join(column_names)}) VALUES ({values});\n"
        file.write(insert_statement)

# Main function to run the export process
def export_data():
    try:
        # Create a connection to MySQL
        conn = create_connection()
        cursor = conn.cursor()

        # Mở file để ghi dữ liệu SQL với mã hóa UTF-8
        with open("user_hrpay_export.sql", "w", encoding="utf-8") as file:
            file.write("USE user_hrpay;\n\n")  # Sử dụng cơ sở dữ liệu

            # Xuất bảng Account
            export_table_to_sql(cursor, 'Account', file)

            # Xuất bảng Group
            export_table_to_sql(cursor, '`Group`', file)

            # Xuất bảng Account_Group
            export_table_to_sql(cursor, 'Account_Group', file)

            # Xuất bảng Module
            export_table_to_sql(cursor, 'Module', file)

            # Xuất bảng Function
            export_table_to_sql(cursor, '`Function`', file)

            # Xuất bảng Function_Module
            export_table_to_sql(cursor, 'Function_Module', file)

            # Xuất bảng Permission
            export_table_to_sql(cursor, 'Permission', file)


        print("Data exported successfully to 'user_hrpay_export.sql'")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        # Close the cursor and connection
        cursor.close()
        conn.close()

if __name__ == "__main__":
    export_data()
