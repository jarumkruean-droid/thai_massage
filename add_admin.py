import mysql.connector

conn = mysql.connector.connect(
    host='192.168.100.22',
    user='root',
    password='P@ssword',
    database='donation'
)

cursor = conn.cursor()

print("Adding default admin user...")
try:
    cursor.execute(
        "INSERT INTO user_login (username, password) VALUES (%s, %s)",
        ("admin", "P@ssword")
    )
    conn.commit()
    print("✓ Admin user added successfully")
except mysql.connector.Error as e:
    if "Duplicate entry" in str(e):
        print("✓ Admin user already exists")
    else:
        print(f"✗ Error: {e}")
        conn.rollback()

cursor.close()
conn.close()
