# Donate API - FastAPI with MariaDB/MySQL

FastAPI application สำหรับจัดการ donations (เพิ่ม ลบ แก้ไข ดูข้อมูล)

## ขั้นตอนการติดตั้ง

### 1. ตั้งค่า Environment Variables
คัดลอก `.env.example` เป็น `.env` และแก้ไขค่าตามต้องการ:

```bash
cp .env.example .env
```

จากนั้นแก้ไขในไฟล์ `.env`:
```
DB_HOST=192.168.100.22
DB_PORT=3306
DB_NAME=donation
DB_USER=root
DB_PASSWORD=P@ssword
```

### 2. ติดตั้ง Dependencies
```bash
pip install -r requirements.txt
```

### 3. รันแอปพลิเคชัน
```bash
python donate_api.py
```

หรือ ใช้ uvicorn:
```bash
uvicorn donate_api:app --host 127.0.0.1 --port 8000 --reload
```

## API Endpoints

### ตรวจสอบ Health
- **GET** `/` - Welcome message

### User Login
- **POST** `/user_login` - เข้าสู่ระบบ
  ```json
  {
    "username": "admin",
    "password": "P@ssword"
  }
  ```

### Donation (เพิ่ม ลบ แก้ไข ดู)

#### ดูข้อมูลทั้งหมด
- **GET** `/Donate` - ดูข้อมูล donations ทั้งหมด

#### ดูข้อมูลตาม ID
- **GET** `/Donate/{donate_id}` - ดูข้อมูล donation ตาม ID
  ```
  /Donate/1
  ```

#### เพิ่มข้อมูล
- **POST** `/Donates` - เพิ่ม donation ใหม่
  ```json
  {
    "name": "โครงการใหม่",
    "donation": 5000,
    "image": "https://example.com/image.png",
    "detail": "รายละเอียดโครงการ"
  }
  ```

#### แก้ไขข้อมูล
- **PUT** `/Donate/{donate_id}` - แก้ไข donation ตาม ID
  ```json
  {
    "name": "โครงการแก้ไข",
    "donation": 6000,
    "image": "https://example.com/image.png",
    "detail": "รายละเอียดโครงการแก้ไข"
  }
  ```

#### ลบข้อมูล
- **DELETE** `/Donate/{donate_id}` - ลบ donation ตาม ID
  ```
  /Donate/1
  ```

## Database Schema

### user_login table
```sql
CREATE TABLE user_login (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);
```

### data_donation table
```sql
CREATE TABLE data_donation (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    donation INT NOT NULL,
    image VARCHAR(1024) NOT NULL,
    detail TEXT NOT NULL
);
```

## Default Credentials
- Username: `admin`
- Password: `P@ssword`

## Features
✅ เชื่อมต่อ MariaDB/MySQL  
✅ CRUD Operations (Create, Read, Update, Delete)  
✅ Error Handling และ Logging  
✅ Environment Variables Configuration  
✅ Response Models (Pydantic)  
✅ Database Initialization on Startup  
✅ Default Demo Data  

## Troubleshooting

### Connection Failed
- ตรวจสอบ IP Address ของ Database Server
- ตรวจสอบ Port (default: 3306)
- ตรวจสอบ Username และ Password
- ตรวจสอบว่า MariaDB/MySQL Server กำลังทำงาน

### Database Not Created
- แอปพลิเคชันจะ auto create database, table และ demo data เมื่อเริ่มต้นครั้งแรก
- ตรวจสอบ log messages ในหน้าต่าง console

## Logs
ทั้งหมด logs จะปรากฏในหน้าต่าง console เพื่อ debugging
