import mysql.connector

conn = mysql.connector.connect(
    host='192.168.100.22',
    user='root',
    password='P@ssword',
    database='donation'
)

cursor = conn.cursor()

print("Checking data_donation table structure...")
cursor.execute("DESCRIBE data_donation")
columns = cursor.fetchall()
print("Current columns:")
for col in columns:
    print(f"  - {col}")

# Check if detail column exists
has_detail = any(col[0] == 'detail' for col in columns)

if not has_detail:
    print("\n❌ Column 'detail' is missing!")
    print("Adding 'detail' column...")
    try:
        cursor.execute("ALTER TABLE data_donation ADD COLUMN detail TEXT")
        conn.commit()
        print("✓ Column 'detail' added successfully")
    except Exception as e:
        print(f"Error adding column: {e}")
        conn.rollback()
else:
    print("✓ Column 'detail' already exists")

cursor.close()
conn.close()
