import requests
import json

API_URL = "http://0.0.0.0:8000"

print("=" * 50)
print("Testing Donation API")
print("=" * 50)

# Test 1: Health check
print("\n1. Health Check (GET /):")
try:
    response = requests.get(f"{API_URL}/")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 2: Get all donations
print("\n2. Get All Donations (GET /Donate):")
try:
    response = requests.get(f"{API_URL}/Donate")
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Records: {len(data)}")
    for item in data[:2]:
        print(f"   - {item}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 3: Create new donation
print("\n3. Create New Donation (POST /Donates):")
new_donation = {
    "name": "โครงการช่วยเหลือผู้ยากไร้",
    "donation": 5000,
    "image": "https://i.imgur.com/test.png",
    "details": "ช่วยเหลือผู้ยากไร้ในต่างจังหวัด"
}
try:
    response = requests.post(f"{API_URL}/Donates", json=new_donation)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 4: Get donation by ID
print("\n4. Get Donation by ID (GET /Donate/1):")
try:
    response = requests.get(f"{API_URL}/Donate/1")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 5: Update donation
print("\n5. Update Donation (PUT /Donate/1):")
update_data = {
    "name": "บริจาคให้หมาน้อย - Updated",
    "donation": 150,
    "image": "https://i.imgur.com/updated.png",
    "details": "บริจาคให้หมาน้อย (แก้ไขแล้ว)"
}
try:
    response = requests.put(f"{API_URL}/Donate/1", json=update_data)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 6: Delete donation
print("\n6. Delete Donation (DELETE /Donate/999):")
try:
    response = requests.delete(f"{API_URL}/Donate/999")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 7: Login
print("\n7. User Login (POST /user_login):")
login_data = {
    "username": "admin",
    "password": "P@ssword"
}
try:
    response = requests.post(f"{API_URL}/user_login", json=login_data)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "=" * 50)
print("Testing Complete")
print("=" * 50)
