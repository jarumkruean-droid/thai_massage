
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from pydantic import BaseModel
import mysql.connector
from mysql.connector import Error
from typing import List, Optional
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database Configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "192.168.100.22"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "database": os.getenv("DB_NAME", "donation"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "P@ssword"),
    "autocommit": False,
    "charset": "utf8mb4",
    "use_unicode": True,
}

# Pydantic Models
class Donate(BaseModel):
    id: Optional[int] = None
    name: str
    donation: int
    image: str
    details: str


class DonateResponse(BaseModel):
    id: int
    name: str
    donation: int
    image: str
    details: str


class Booking(BaseModel):
    service_id: int
    service_type: str
    therapist: str
    strength: str
    customer_name: Optional[str] = "ลูกค้า"
    customer_phone: Optional[str] = ""
    notes: Optional[str] = ""


class BookingResponse(BaseModel):
    id: int
    service_id: int
    service_name: str
    service_type: str
    therapist: str
    strength: str
    customer_name: str
    customer_phone: str
    notes: str
    created_at: datetime
    status: str


app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (for images)
if not os.path.exists("uploads"):
    os.makedirs("uploads")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# Database Connection Helper
def get_db_connection():
    """Create and return a MariaDB connection."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        logger.info("Successfully connected to database")
        return conn
    except Error as e:
        logger.error(f"Error connecting to MariaDB: {e}")
        raise HTTPException(
            status_code=500, detail=f"Database connection failed: {str(e)}"
        )


# Root endpoint
@app.get("/", tags=["health"])
async def root():
    return {"message": "Welcome to Donation API", "version": "1.0"}


def ensure_user_login_table(conn):
    """Ensure the user_login table exists for login.

    Also creates a default user for easy initial login if no users exist.
    """
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_login (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL
            ) ENGINE=InnoDB;
            """
        )
        conn.commit()
        logger.info("user_login table created or already exists")

        # If the table is empty, create a default user (admin / P@ssword)
        cursor.execute("SELECT COUNT(*) FROM user_login")
        count = cursor.fetchone()[0]
        if count == 0:
            cursor.execute(
                "INSERT INTO user_login (username, password) VALUES (%s, %s)",
                ("admin", "P@ssword"),
            )
            conn.commit()
            logger.info("Default admin user created")
        cursor.close()
    except Error as e:
        logger.error(f"Error in ensure_user_login_table: {e}")
        conn.rollback()
        raise


def ensure_demo_donation(conn):
    """Ensure there are demo donations in the data_donation table."""
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS data_donation (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                donation INT NOT NULL,
                image VARCHAR(1024) NOT NULL,
                details TEXT NOT NULL
            ) ENGINE=InnoDB;
            """
        )
        conn.commit()
        logger.info("data_donation table created or already exists")

        # Repair legacy column name if needed
        cursor.execute("SHOW COLUMNS FROM data_donation LIKE 'detail'")
        if cursor.fetchone():
            cursor.execute("ALTER TABLE data_donation CHANGE detail details TEXT")
            conn.commit()
            logger.info("Renamed legacy data_donation.detail column to details")

        cursor.execute("SELECT COUNT(*) FROM data_donation")
        count = cursor.fetchone()[0]
        if count == 0:
            demo_donations = [
                ("นวดเท้า", 500, "uploads/นวดเท้า.jpg", "บริการนวดเท้าเพื่อผ่อนคลายและกระตุ้นการไหลเวียนเลือด"),
                ("นวดตัว", 700, "uploads/นวดตัว.jpg", "บริการนวดตัวเพื่อคลายกล้ามเนื้อและลดความตึงเครียด"),
                ("นวดน้ำมัน", 900, "uploads/นวดน้ำมัน.jpg", "บริการนวดน้ำมันพร้อมน้ำมันหอมระเหยสำหรับผ่อนคลาย"),
            ]
            cursor.executemany(
                "INSERT INTO data_donation (name, donation, image, details) VALUES (%s, %s, %s, %s)",
                demo_donations,
            )
            conn.commit()
            logger.info("Demo donation data inserted")
        cursor.close()
    except Error as e:
        logger.error(f"Error in ensure_demo_donation: {e}")
        conn.rollback()
        raise


def ensure_massage_booking_table(conn):
    """Ensure the massage_bookings table exists for booking records."""
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS massage_bookings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                service_id INT NOT NULL,
                service_name VARCHAR(255) NOT NULL,
                service_type VARCHAR(100) NOT NULL,
                therapist VARCHAR(100) NOT NULL,
                strength VARCHAR(50) NOT NULL,
                customer_name VARCHAR(255) DEFAULT 'ลูกค้า',
                customer_phone VARCHAR(20) DEFAULT '',
                notes TEXT DEFAULT '',
                status ENUM('pending', 'confirmed', 'completed', 'cancelled') DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (service_id) REFERENCES data_donation(id)
            ) ENGINE=InnoDB;
            """
        )
        conn.commit()
        logger.info("massage_bookings table created or already exists")
        cursor.close()
    except Error as e:
        logger.error(f"Error in ensure_massage_booking_table: {e}")
        conn.rollback()
        raise


@app.on_event("startup")
async def startup_initialize():
    """Initialize database tables on application startup."""
    try:
        conn = get_db_connection()
        ensure_user_login_table(conn)
        ensure_demo_donation(conn)
        ensure_massage_booking_table(conn)
        conn.close()
        logger.info("Database initialization completed successfully")
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
        raise


@app.post("/user_login")
async def user_login(request: Request):
    """Authenticate user with username and password."""
    try:
        data = await request.json()
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            logger.warning("Login attempt with missing credentials")
            return JSONResponse(
                content={"success": False, "error": "Username and password required"},
                status_code=400,
            )

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT password FROM user_login WHERE username = %s",
            (username,),
        )
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if not row:
            logger.warning(f"Login failed: user not found - {username}")
            return JSONResponse(
                content={"success": False, "error": "Invalid credentials"},
                status_code=401,
            )

        stored_password = row[0]
        if stored_password != password:
            logger.warning(f"Login failed: invalid password for user - {username}")
            return JSONResponse(
                content={"success": False, "error": "Invalid credentials"},
                status_code=401,
            )

        logger.info(f"Successful login for user: {username}")
        return JSONResponse(content={"success": True})

    except Exception as e:
        logger.error(f"Login exception: {e}")
        return JSONResponse(
            content={"success": False, "error": str(e)}, status_code=500
        )


# GET all donates
@app.get("/Donate", response_model=List[DonateResponse])
@app.get("/donations", response_model=List[DonateResponse])
async def get_all_donate():
    """Retrieve all donate from the database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, name, donation, image, details FROM data_donation"
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        logger.info(f"Retrieved {len(rows)} donations")
        return rows
    except Error as e:
        logger.error(f"Database error in get_all_donate: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in get_all_donate: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving donations: {str(e)}")


# GET Donate by ID
@app.get("/Donate/{donate_id}", response_model=DonateResponse)
async def get_donate_by_id(donate_id: int):
    """Retrieve a specific donate by ID."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, name, donation, image, details FROM data_donation WHERE id = %s",
            (donate_id,),
        )
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if not row:
            logger.warning(f"Donation with id {donate_id} not found")
            raise HTTPException(
                status_code=404, detail=f"Donate with id {donate_id} not found"
            )
        return row
    except HTTPException:
        raise
    except Error as e:
        logger.error(f"Database error in get_donate_by_id: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in get_donate_by_id: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving donation: {str(e)}")


# POST - Create a new donate
@app.post("/Donates", response_model=DonateResponse, status_code=201)
@app.post("/donations", response_model=DonateResponse, status_code=201)
async def create_donate(donate: Donate):
    """Create a new donate in the database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO data_donation (name, donation, image, details) "
            "VALUES (%s, %s, %s, %s)",
            (donate.name, donate.donation, donate.image, donate.details),
        )
        conn.commit()
        donate_id = cursor.lastrowid
        cursor.close()
        conn.close()
        logger.info(f"Created new donation with id: {donate_id}")
        return {
            "id": donate_id,
            "name": donate.name,
            "donation": donate.donation,
            "image": donate.image,
            "details": donate.details,
        }
    except Error as e:
        logger.error(f"Database error in create_donate: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in create_donate: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating donation: {str(e)}")


# PUT - Update a donate
@app.put("/Donate/{donate_id}", response_model=DonateResponse)
@app.put("/donations/{donate_id}", response_model=DonateResponse)
async def update_donate(donate_id: int, donate: Donate):
    """Update an existing donate."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM data_donation WHERE id = %s", (donate_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            logger.warning(f"Attempted to update non-existent donation: {donate_id}")
            raise HTTPException(
                status_code=404, detail=f"Donate with id {donate_id} not found"
            )

        cursor.execute(
            "UPDATE data_donation SET name = %s, donation = %s, image = %s, details = %s "
            "WHERE id = %s",
            (donate.name, donate.donation, donate.image, donate.details, donate_id),
        )
        conn.commit()
        cursor.close()
        conn.close()
        logger.info(f"Updated donation with id: {donate_id}")
        return {
            "id": donate_id,
            "name": donate.name,
            "donation": donate.donation,
            "image": donate.image,
            "details": donate.details,
        }
    except HTTPException:
        raise
    except Error as e:
        logger.error(f"Database error in update_donate: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in update_donate: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating donation: {str(e)}")


# DELETE - Delete a donate
@app.delete("/Donate/{donate_id}")
@app.delete("/donations/{donate_id}")
async def delete_donate(donate_id: int):
    """Delete a donate from the database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM data_donation WHERE id = %s", (donate_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            logger.warning(f"Attempted to delete non-existent donation: {donate_id}")
            raise HTTPException(
                status_code=404, detail=f"Donate with id {donate_id} not found"
            )

        cursor.execute("DELETE FROM data_donation WHERE id = %s", (donate_id,))
        conn.commit()
        cursor.close()
        conn.close()
        logger.info(f"Deleted donation with id: {donate_id}")
        return {"message": f"Donate with id {donate_id} deleted successfully"}
    except HTTPException:
        raise
    except Error as e:
        logger.error(f"Database error in delete_donate: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in delete_donate: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting donation: {str(e)}")


# POST - Create a new massage booking
@app.post("/bookings", response_model=BookingResponse, status_code=201)
async def create_booking(booking: Booking):
    """Create a new massage booking in the database."""
    logger.info(f"Received create_booking request: {booking}")
    try:
        # First get the service name
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        logger.info(f"Retrieving service name for id {booking.service_id}")
        cursor.execute(
            "SELECT name FROM data_donation WHERE id = %s",
            (booking.service_id,),
        )
        service_row = cursor.fetchone()
        if not service_row:
            cursor.close()
            conn.close()
            raise HTTPException(
                status_code=404, detail=f"Service with id {booking.service_id} not found"
            )
        service_name = service_row["name"]

        # Insert the booking
        logger.info(f"Inserting booking for service {service_name} with service_id={booking.service_id}")
        cursor.execute(
            """INSERT INTO massage_bookings
               (service_id, service_name, service_type, therapist, strength,
                customer_name, customer_phone, notes, status)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'pending')""",
            (booking.service_id, service_name, booking.service_type, booking.therapist,
             booking.strength, booking.customer_name, booking.customer_phone, booking.notes),
        )
        conn.commit()
        booking_id = cursor.lastrowid
        logger.info(f"Inserted booking id {booking_id}")

        # Get the created booking
        logger.info(f"Retrieving created booking id {booking_id}")
        cursor.execute(
            """SELECT id, service_id, service_name, service_type, therapist, strength,
                      customer_name, customer_phone, notes, status,
                      created_at
               FROM massage_bookings WHERE id = %s""",
            (booking_id,),
        )
        booking_row = cursor.fetchone()
        cursor.close()
        conn.close()

        logger.info(f"Created new booking with id: {booking_id}")
        return booking_row
    except HTTPException:
        raise
    except Error as e:
        logger.error(f"Database error in create_booking: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in create_booking: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating booking: {str(e)}")


# GET - Retrieve all massage bookings
@app.get("/bookings", response_model=List[BookingResponse])
async def get_all_bookings():
    """Retrieve all massage bookings from the database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """SELECT id, service_id, service_name, service_type, therapist, strength,
                      customer_name, customer_phone, notes, status,
                      created_at
               FROM massage_bookings
               ORDER BY created_at DESC"""
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        logger.info(f"Retrieved {len(rows)} bookings")
        return rows
    except Error as e:
        logger.error(f"Database error in get_all_bookings: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in get_all_bookings: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving bookings: {str(e)}")


# PUT - Update a booking
@app.put("/bookings/{booking_id}", response_model=BookingResponse)
async def update_booking(booking_id: int, booking: Booking):
    """Update an existing massage booking."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id FROM massage_bookings WHERE id = %s", (booking_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            logger.warning(f"Attempted to update non-existent booking: {booking_id}")
            raise HTTPException(status_code=404, detail=f"Booking with id {booking_id} not found")

        cursor.execute(
            "UPDATE massage_bookings SET service_id = %s, service_type = %s, therapist = %s, strength = %s, customer_name = %s, customer_phone = %s, notes = %s WHERE id = %s",
            (
                booking.service_id,
                booking.service_type,
                booking.therapist,
                booking.strength,
                booking.customer_name,
                booking.customer_phone,
                booking.notes,
                booking_id,
            ),
        )
        conn.commit()
        cursor.execute(
            """SELECT id, service_id, service_name, service_type, therapist, strength,
                      customer_name, customer_phone, notes, status,
                      created_at
               FROM massage_bookings WHERE id = %s""",
            (booking_id,),
        )
        updated = cursor.fetchone()
        cursor.close()
        conn.close()
        logger.info(f"Updated booking with id: {booking_id}")
        return updated
    except HTTPException:
        raise
    except Error as e:
        logger.error(f"Database error in update_booking: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in update_booking: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating booking: {str(e)}")


# DELETE - Delete a booking
@app.delete("/bookings/{booking_id}")
async def delete_booking(booking_id: int):
    """Delete a massage booking from the database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM massage_bookings WHERE id = %s", (booking_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            logger.warning(f"Attempted to delete non-existent booking: {booking_id}")
            raise HTTPException(status_code=404, detail=f"Booking with id {booking_id} not found")

        cursor.execute("DELETE FROM massage_bookings WHERE id = %s", (booking_id,))
        conn.commit()
        cursor.close()
        conn.close()
        logger.info(f"Deleted booking with id: {booking_id}")
        return {"message": f"Booking with id {booking_id} deleted successfully"}
    except HTTPException:
        raise
    except Error as e:
        logger.error(f"Database error in delete_booking: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in delete_booking: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting booking: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
