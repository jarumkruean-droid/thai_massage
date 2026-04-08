import mysql.connector

try:
    print("Testing database connection...")
    conn = mysql.connector.connect(
        host='192.168.100.22',
        user='root',
        password='P@ssword',
        database='donation'
    )
    print("✓ Connection successful!")
    
    cursor = conn.cursor(dictionary=True)
    
    # Check user_login
    cursor.execute("SELECT * FROM user_login")
    users = cursor.fetchall()
    print(f"\nUser Login Table: {len(users)} records")
    for user in users:
        print(f"  - {user}")
    
    # Check data_donation
    cursor.execute("SELECT * FROM data_donation")
    donations = cursor.fetchall()
    print(f"\nData Donation Table: {len(donations)} records")
    for donation in donations:
        print(f"  - ID: {donation['id']}, Name: {donation['name']}, Donation: {donation['donation']}")
    
    cursor.close()
    conn.close()
    print("\n✓ All tests passed!")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
