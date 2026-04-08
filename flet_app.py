import os
import flet as ft
import requests
import mysql.connector
from dotenv import load_dotenv
from mysql.connector import Error
from urllib.parse import quote

load_dotenv()

API_HOST = os.getenv("API_HOST", "192.168.100.12")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_BASE = f"http://{API_HOST}:{API_PORT}"
API_URL = f"{API_BASE}/Donate"
BOOKING_API_URL = f"{API_BASE}/bookings"
API_UPLOADS_BASE = f"{API_BASE}/uploads/"
USE_API = os.getenv("USE_API", "true").strip().lower() in ("1", "true", "yes")

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "192.168.100.22"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "database": os.getenv("DB_NAME", "donation"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "P@ssword"),
}

DEFAULT_SERVICES = [
    {
        "id": 1,
        "name": "นวดเท้า",
        "donation": 500,
        "image": "uploads/นวดเท้า.jpg",
        "details": "บริการนวดเท้าเพื่อผ่อนคลายและกระตุ้นการไหลเวียนเลือด",
    },
    {
        "id": 2,
        "name": "นวดตัว",
        "donation": 700,
        "image": "uploads/นวดตัว.jpg",
        "details": "บริการนวดตัวเพื่อคลายกล้ามเนื้อและลดความตึงเครียด",
    },
    {
        "id": 3,
        "name": "นวดน้ำมัน",
        "donation": 900,
        "image": "uploads/นวดน้ำมัน.jpg",
        "details": "บริการนวดน้ำมันพร้อมน้ำมันหอมระเหยสำหรับผ่อนคลาย",
    },
]

def main(page: ft.Page):
    page.title = "นวดแผนไทย"
    page.bgcolor = "white"
    page.scroll = "auto"
    page.window_width = 390
    page.window_height = 844

    # Login state
    if not hasattr(page, 'is_logged_in'):
        page.is_logged_in = False

    # If not logged in, show login page
    if not page.is_logged_in:
        import login_page
        login_page.main(page)
        return

    # State
    page.selected_service = None
    page.booking_data = {
        "service_type": None,
        "therapist": None,
        "strength": None,
    }
    page.selected_category = "ทั้งหมด"  # Default selected category
    page.current_tab = "home"  # Current active tab

    def navigate_to(page_fn, *args, **kwargs):
        page.clean()
        page_fn(*args, **kwargs)

    def resolve_image_url(image_value: str) -> str:
        if not image_value:
            return ""
        image_value = str(image_value)
        
        # If already a full URL, return as-is
        if image_value.startswith("http://") or image_value.startswith("https://"):
            return image_value
        
        # For local uploads, construct API URL for backend to serve
        # Backend API serves files via /uploads endpoint using FastAPI StaticFiles
        if image_value.startswith("/uploads") or image_value.startswith("uploads/"):
            clean_path = image_value.lstrip("/")
            return f"{API_BASE}/{clean_path}"
        
        # For raw filenames, prepend uploads path
        return f"{API_BASE}/uploads/{image_value}"

    def load_services_from_db():
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, name, donation, image, details FROM data_donation")
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            print(f"Loaded {len(rows)} services from DB")
            return rows
        except Exception as ex:
            print(f"Error loading services from DB: {ex}")
            return []

    def select_category(category):
        page.selected_category = category
        navigate_to(main_page)

    def select_tab(tab_name):
        page.current_tab = tab_name
        if tab_name == "home":
            navigate_to(main_page)
        elif tab_name == "bookings":
            navigate_to(bookings_page)
        elif tab_name == "notifications":
            navigate_to(notifications_page)
        elif tab_name == "profile":
            navigate_to(profile_page)

    # --- Bookings Page ---
    def bookings_page():
        page.current_tab = "bookings"
        # Top bar
        top_bar = ft.Row([
            ft.Text("การจองของฉัน", size=18, weight="bold", color="#144883", expand=True),
        ], alignment="start")

        def fetch_bookings_from_db():
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor(dictionary=True)
                cursor.execute(
                    """SELECT id, service_id, service_name, service_type, therapist, strength,
                              customer_name, customer_phone, notes, created_at, status
                       FROM massage_bookings ORDER BY created_at DESC"""
                )
                rows = cursor.fetchall()
                cursor.close()
                conn.close()
                print(f"Loaded {len(rows)} bookings from DB")
                return rows
            except Error as ex:
                print(f"Error loading bookings from DB: {ex}")
                return []

        def fetch_bookings():
            try:
                res = requests.get(BOOKING_API_URL, timeout=10)
                res.raise_for_status()
                bookings = res.json()
                if bookings:
                    return bookings
                print("API returned no bookings, falling back to DB")
            except Exception as ex:
                print(f"Error loading bookings from API: {ex}")

            return fetch_bookings_from_db()

        bookings_data = fetch_bookings()

        if bookings_data:
            bookings_list = ft.Column([
                ft.Container(
                    ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.STAR, color="#144883", size=20),
                            ft.Text("รายการการจองของคุณ", size=16, weight="bold", color="#144883"),
                        ], spacing=8),
                        ft.Divider(color="#E0E0E0", thickness=1),
                        *[
                            ft.Container(
                                ft.Column([
                                    ft.Text(booking.get("service_name", "บริการนวด"), size=16, weight="bold", color="#2B4D4D"),
                                    ft.Text(f"ประเภท: {booking.get('service_type', '-')}", size=14, color="#6B7A7A"),
                                    ft.Text(f"พนักงาน: {booking.get('therapist', '-')}", size=14, color="#6B7A7A"),
                                    ft.Text(f"ความแรง: {booking.get('strength', '-')}", size=14, color="#6B7A7A"),
                                    ft.Text(f"วันที่: {booking.get('created_at', '-')}", size=12, color="#B0C4E0"),
                                    ft.Text(f"สถานะ: {booking.get('status', 'pending')}", size=12, color="#144883", weight="bold"),
                                ], spacing=4),
                                padding=ft.Padding(left=16, right=16, top=12, bottom=12),
                                bgcolor="white",
                                border_radius=12,
                                shadow=ft.BoxShadow(blur_radius=6, color="#E0E0E0", offset=ft.Offset(0, 2)),
                                margin=ft.Margin(bottom=12),
                            ) for booking in bookings_data
                        ]
                    ], spacing=12),
                    padding=ft.Padding(left=16, right=16, top=16, bottom=16),
                    bgcolor="white",
                    border_radius=16,
                )
            ], spacing=12)
        else:
            bookings_list = ft.Container(
                ft.Column([
                    ft.Icon(ft.Icons.BOOKMARK_BORDER, size=64, color="#B6CACA"),
                    ft.Text("ยังไม่มีประวัติการจอง", size=16, color="#6B7A7A", text_align="center"),
                    ft.Text("การจองของคุณจะแสดงที่นี่", size=14, color="#B0C4E0", text_align="center"),
                ], alignment="center", horizontal_alignment="center", spacing=16),
                expand=True,
            )

        # Bottom nav
        bottom_nav = create_bottom_nav()

        page.add(
            ft.Container(
                ft.Column([
                    top_bar,
                    bookings_list,
                ], spacing=0, expand=True),
                padding=ft.Padding(left=16, right=16, top=16, bottom=100),
                bgcolor="#F4FAFB"
            )
        )
        page.add(bottom_nav)
        page.update()

    # --- Notifications Page ---
    def notifications_page():
        # Top bar
        top_bar = ft.Row([
            ft.Text("แจ้งเตือน", size=18, weight="bold", color="#144883", expand=True),
        ], alignment="start")

        # Placeholder for notifications
        notifications_list = ft.Container(
            ft.Column([
                ft.Icon(ft.Icons.NOTIFICATIONS_NONE, size=64, color="#B6CACA"),
                ft.Text("ไม่มีแจ้งเตือนใหม่", size=16, color="#6B7A7A", text_align="center"),
                ft.Text("แจ้งเตือนจะแสดงที่นี่", size=14, color="#B0C4E0", text_align="center"),
            ], alignment="center", horizontal_alignment="center", spacing=16),
            expand=True,
        )

        # Bottom nav
        bottom_nav = create_bottom_nav()

        page.add(
            ft.Container(
                ft.Column([
                    top_bar,
                    notifications_list,
                ], spacing=0, expand=True),
                padding=ft.Padding(left=16, right=16, top=16, bottom=100),
                bgcolor="#F4FAFB"
            )
        )
        page.add(bottom_nav)
        page.update()

    def logout():
        page.is_logged_in = False
        import login_page
        login_page.main(page)

    # --- Profile Page ---
    def profile_page():
        # Top bar
        top_bar = ft.Row([
            ft.Text("โปรไฟล์", size=18, weight="bold", color="#144883", expand=True),
        ], alignment="start")

        # Profile content
        profile_content = ft.Container(
            ft.Column([
                ft.Container(
                    ft.Column([
                        ft.Icon(ft.Icons.PERSON, size=80, color="#144883"),
                        ft.Text("ลูกค้า", size=20, weight="bold", color="#2B4D4D"),
                        ft.Text("สมาชิก", size=14, color="#6B7A7A"),
                    ], alignment="center", spacing=12),
                    bgcolor="white",
                    border_radius=16,
                    padding=ft.Padding(left=24, right=24, top=24, bottom=24),
                    shadow=ft.BoxShadow(blur_radius=8, color="#E0E0E0", offset=ft.Offset(0, 2)),
                ),
                ft.Container(height=24),
                ft.Container(
                    ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.PHONE, color="#144883", size=24),
                            ft.Text("เบอร์โทรศัพท์", size=14, color="#2B4D4D", expand=True),
                            ft.Text("-", size=14, color="#6B7A7A"),
                        ], spacing=12, alignment="start"),
                        ft.Divider(color="#E0E0E0", height=1),
                        ft.Row([
                            ft.Icon(ft.Icons.EMAIL, color="#144883", size=24),
                            ft.Text("อีเมล", size=14, color="#2B4D4D", expand=True),
                            ft.Text("-", size=14, color="#6B7A7A"),
                        ], spacing=12, alignment="start"),
                        ft.Divider(color="#E0E0E0", height=1),
                        ft.Row([
                            ft.Icon(ft.Icons.CALENDAR_TODAY, color="#144883", size=24),
                            ft.Text("วันที่สมัคร", size=14, color="#2B4D4D", expand=True),
                            ft.Text("-", size=14, color="#6B7A7A"),
                        ], spacing=12, alignment="start"),
                    ], spacing=16),
                    bgcolor="white",
                    border_radius=12,
                    padding=ft.Padding(left=16, right=16, top=16, bottom=16),
                ),
                ft.Container(height=24),
                ft.Container(
                    ft.FilledButton(
                        "ออกจากระบบ",
                        bgcolor="#E53935",
                        color="white",
                        width=320,
                        height=50,
                        on_click=lambda e: logout()
                    ),
                    margin=ft.Margin(left=0, right=0, top=16, bottom=0)
                ),
            ], spacing=0),
            expand=True,
        )

        # Bottom nav
        bottom_nav = create_bottom_nav()

        page.add(
            ft.Container(
                ft.Column([
                    top_bar,
                    profile_content,
                ], spacing=0, expand=True),
                padding=ft.Padding(left=16, right=16, top=16, bottom=100),
                bgcolor="#F4FAFB"
            )
        )
        page.add(bottom_nav)
        page.update()

    def create_bottom_nav():
        return ft.Container(
            ft.Row([
                ft.Container(
                    ft.Column([
                        ft.Icon(ft.Icons.HOME, color="#144883" if page.current_tab == "home" else "#B6CACA", size=24),
                        ft.Text("หน้าแรก", size=10, color="#144883" if page.current_tab == "home" else "#B6CACA"),
                    ], alignment="center", horizontal_alignment="center"),
                    on_click=lambda e: select_tab("home"),
                    padding=ft.Padding(left=12, right=12, top=8, bottom=8),
                ),
                ft.Container(
                    ft.Column([
                        ft.Icon(ft.Icons.BOOKMARK, color="#144883" if page.current_tab == "bookings" else "#B6CACA", size=24),
                        ft.Text("บันทึก", size=10, color="#144883" if page.current_tab == "bookings" else "#B6CACA"),
                    ], alignment="center", horizontal_alignment="center"),
                    on_click=lambda e: select_tab("bookings"),
                    padding=ft.Padding(left=12, right=12, top=8, bottom=8),
                ),
                ft.Container(
                    ft.Column([
                        ft.Icon(ft.Icons.NOTIFICATIONS, color="#144883" if page.current_tab == "notifications" else "#B6CACA", size=24),
                        ft.Text("แจ้งเตือน", size=10, color="#144883" if page.current_tab == "notifications" else "#B6CACA"),
                    ], alignment="center", horizontal_alignment="center"),
                    on_click=lambda e: select_tab("notifications"),
                    padding=ft.Padding(left=12, right=12, top=8, bottom=8),
                ),
                ft.Container(
                    ft.Column([
                        ft.Icon(ft.Icons.PERSON, color="#144883" if page.current_tab == "profile" else "#B6CACA", size=24),
                        ft.Text("โปรไฟล์", size=10, color="#144883" if page.current_tab == "profile" else "#B6CACA"),
                    ], alignment="center", horizontal_alignment="center"),
                    on_click=lambda e: select_tab("profile"),
                    padding=ft.Padding(left=12, right=12, top=8, bottom=8),
                ),
            ], alignment="spaceAround", expand=True),
            bgcolor="white",
            padding=ft.Padding(left=0, right=0, top=12, bottom=16),
            border_radius=20,
            margin=ft.Margin(left=0, right=0, top=16, bottom=0),
            shadow=ft.BoxShadow(blur_radius=8, color="#E0E0E0", offset=ft.Offset(0, -2)),
        )

    # --- Main Page ---
    def main_page():
        page.current_tab = "home"

        # Greeting
        greeting = ft.Column([
            ft.Text("ยินดีต้อนรับ!", size=24, weight="bold", color="#144883"),
            ft.Text("ระบบจองนวดแผนไทยออนไลน์", size=14, color="#6B7A7A"),
            ft.Text("สัมผัสประสบการณ์นวดแผนไทยแท้ที่ดีที่สุด", size=12, color="#B0C4E0"),
        ], spacing=2, alignment="start")

        # Search bar
        search_bar = ft.Container(
            ft.TextField(
                hint_text="ค้นหาบริการนวด...",
                border_radius=12,
                filled=True,
                fill_color="white",
                prefix_icon=ft.Icons.SEARCH_ROUNDED,
                content_padding=ft.Padding(left=12, right=12, top=8, bottom=8),
                height=48,
                border_color="#E0E0E0",
                focused_border_color="#144883",
            ),
            margin=ft.Margin(left=0, right=0, top=12, bottom=8),
            shadow=ft.BoxShadow(blur_radius=4, color="#E0E0E0", offset=ft.Offset(0, 2)),
        )

        # Services categories
        services = [
            ("ทั้งหมด", ft.Icons.SPA),
            ("นวดเท้า", ft.Icons.DIRECTIONS_WALK),
            ("นวดตัว", ft.Icons.ACCESSIBILITY_NEW),
            ("นวดน้ำมัน", ft.Icons.WATER_DROP),
        ]
        cat_row = ft.Row([
            ft.Container(
                ft.Column([
                    ft.Icon(icon, color="#144883" if page.selected_category == label else "#B6CACA", size=28),
                    ft.Text(label, size=12, color="#144883" if page.selected_category == label else "#B6CACA", 
                           weight="bold" if page.selected_category == label else None),
                ], alignment="center"),
                bgcolor="#E6F2F2" if page.selected_category == label else "#F4FAFB",
                border=ft.Border.all(2, "#144883") if page.selected_category == label else None,
                border_radius=12,
                padding=ft.Padding(left=12, right=12, top=8, bottom=8),
                margin=ft.Margin(left=0, right=8, top=0, bottom=0),
                on_click=lambda e, lbl=label: select_category(lbl),
            ) for label, icon in services
        ], scroll="auto", alignment="start")

        # Services list (horizontal scroll)
        def fetch_services():
            if USE_API:
                try:
                    res = requests.get(API_URL, timeout=10)
                    res.raise_for_status()
                    services = res.json()
                    if services:
                        return services
                    print("API returned no services, falling back to DB")
                except Exception as ex:
                    print(f"API unavailable, falling back to DB: {ex}")
            else:
                print("USE_API is false, loading services from DB")

            services = load_services_from_db()
            if services:
                return services
            print("Falling back to default service list")
            return DEFAULT_SERVICES

        services_data = fetch_services()

        # Filter services based on selected category
        if page.selected_category == "ทั้งหมด":
            filtered_services = services_data
        elif page.selected_category == "นวดเท้า":
            filtered_services = [s for s in services_data if "เท้า" in s.get("name", "").lower() or "foot" in s.get("name", "").lower()]
        elif page.selected_category == "นวดตัว":
            filtered_services = [s for s in services_data if "ตัว" in s.get("name", "").lower() or "body" in s.get("name", "").lower()]
        elif page.selected_category == "นวดน้ำมัน":
            filtered_services = [s for s in services_data if "น้ำมัน" in s.get("name", "").lower() or "oil" in s.get("name", "").lower()]
        else:
            filtered_services = services_data

        def service_card(service):
            image_url = resolve_image_url(service.get("image", ""))
            image_widget = ft.Image(
                src=image_url,
                width=200,
                height=100,
                border_radius=12,
                fit="cover",
                error_content=ft.Container(
                    ft.Column([
                        ft.Icon(ft.Icons.SPA, color="#144883", size=40),
                    ], alignment="center", horizontal_alignment="center"),
                    width=200,
                    height=100,
                    bgcolor="#E6F2F2",
                    border_radius=12,
                ),
            )
            return ft.Container(
                width=220,
                bgcolor="white",
                border_radius=16,
                padding=8,
                margin=ft.Margin(left=0, right=12, top=0, bottom=0),
                shadow=ft.BoxShadow(blur_radius=8, color="#E0E0E0", offset=ft.Offset(0, 2)),
                content=ft.Column([
                    image_widget,
                    ft.Text(service.get("name", "บริการนวด"), size=16, weight="bold", color="#2B4D4D", max_lines=1, overflow="ellipsis"),
                    ft.Text(f"฿{service.get('donation', 0)}", size=14, color="#144883", weight="bold"),
                    ft.Text(service.get("details", service.get("detail", "")), size=12, color="#6B7A7A", max_lines=2, overflow="ellipsis"),
                ], spacing=4),
                on_click=lambda e, s=service: navigate_to(detail_page, s)
            )

        services_list = ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.SPA, color="#144883", size=24),
                ft.Text("บริการนวดแผนไทย", size=18, weight="bold", color="#2B4D4D"),
                ft.Text(f"({len(filtered_services)} รายการ)", size=12, color="#144883"),
            ], alignment="spaceBetween"),
            ft.Row([
                *(service_card(s) for s in filtered_services[:6])
            ], scroll="auto", alignment="start") if filtered_services else ft.Container(
                ft.Column([
                    ft.Icon(ft.Icons.SEARCH_OFF, size=48, color="#B6CACA"),
                    ft.Text("ไม่พบบริการในหมวดหมู่นี้", size=14, color="#6B7A7A", text_align="center"),
                ], alignment="center", spacing=12),
                height=120,
            )
        ], spacing=8)

        # Bottom nav
        bottom_nav = ft.Container(
            ft.Row([
                ft.Container(
                    ft.Column([
                        ft.Icon(ft.Icons.HOME, color="#144883", size=24),
                        ft.Text("หน้าแรก", size=10, color="#144883"),
                    ], alignment="center", horizontal_alignment="center"),
                    padding=ft.Padding(left=12, right=12, top=8, bottom=8),
                    on_click=lambda e: select_tab("home"),
                ),
                ft.Container(
                    ft.Column([
                        ft.Icon(ft.Icons.BOOKMARK_BORDER, color="#B6CACA", size=24),
                        ft.Text("บันทึก", size=10, color="#B6CACA"),
                    ], alignment="center", horizontal_alignment="center"),
                    padding=ft.Padding(left=12, right=12, top=8, bottom=8),
                    on_click=lambda e: select_tab("bookings"),
                ),
                ft.Container(
                    ft.Column([
                        ft.Icon(ft.Icons.NOTIFICATIONS_NONE, color="#B6CACA", size=24),
                        ft.Text("แจ้งเตือน", size=10, color="#B6CACA"),
                    ], alignment="center", horizontal_alignment="center"),
                    padding=ft.Padding(left=12, right=12, top=8, bottom=8),
                    on_click=lambda e: select_tab("notifications"),
                ),
                ft.Container(
                    ft.Column([
                        ft.Icon(ft.Icons.PERSON_OUTLINE, color="#B6CACA", size=24),
                        ft.Text("โปรไฟล์", size=10, color="#B6CACA"),
                    ], alignment="center", horizontal_alignment="center"),
                    padding=ft.Padding(left=12, right=12, top=8, bottom=8),
                    on_click=lambda e: select_tab("profile"),
                ),
            ], alignment="spaceAround", expand=True),
            bgcolor="white",
            padding=ft.Padding(left=0, right=0, top=12, bottom=16),
            border_radius=20,
            margin=ft.Margin(left=0, right=0, top=16, bottom=0),
            shadow=ft.BoxShadow(blur_radius=8, color="#E0E0E0", offset=ft.Offset(0, -2)),
        )

        page.add(
            ft.Container(
                ft.Column([
                    greeting,
                    search_bar,
                    ft.Container(
                        ft.Text("ประเภทการนวด", size=14, color="#144883", weight="bold"),
                        margin=ft.Margin(left=0, right=0, top=8, bottom=8)
                    ),
                    cat_row,
                    services_list,
                ], spacing=6, expand=True),
                padding=ft.Padding(left=16, right=16, top=16, bottom=100),
                bgcolor="#F4FAFB"
            )
        )
        page.add(bottom_nav)
        page.update()

    # --- Detail Page ---
    def detail_page(service):
        page.selected_service = service
        # Top bar
        top_bar = ft.Row([
            ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda e: navigate_to(main_page)),
            ft.Text("", expand=True),
            ft.IconButton(icon=ft.Icons.FAVORITE_BORDER),
        ], alignment="spaceBetween")

        # Service image and info
        service_img = ft.Container(
            ft.Image(
                src=resolve_image_url(service.get("image", "")),
                width=320,
                height=200,
                border_radius=16,
                fit="cover",
                error_content=ft.Container(
                    ft.Column([
                        ft.Icon(ft.Icons.SPA, color="#144883", size=80),
                    ], alignment="center", horizontal_alignment="center"),
                    width=320,
                    height=200,
                    bgcolor="#E6F2F2",
                    border_radius=16,
                ),
            ),
            margin=ft.Margin(left=0, right=0, top=0, bottom=16),
            shadow=ft.BoxShadow(blur_radius=8, color="#E0E0E0", offset=ft.Offset(0, 2)),
        )
        title = ft.Text(service.get("name", "บริการนวด"), size=22, weight="bold", color="#144883")
        price_row = ft.Row([
            ft.Icon(ft.Icons.ATTACH_MONEY, color="#144883", size=24),
            ft.Text(f"{service.get('donation', 0)} บาท", size=20, color="#144883", weight="bold"),
        ], alignment="start", spacing=8)
        description = ft.Text(
            service.get("details", service.get("detail", "")),
            size=13, color="#6B7A7A",
            text_align="left"
        )

        book_btn = ft.Container(
            ft.FilledButton(
                "จองการนวด",
                bgcolor="#144883",
                color="white",
                width=320,
                height=50,
                on_click=lambda e: navigate_to(booking_page, service)
            ),
            margin=ft.Margin(left=0, right=0, top=16, bottom=0)
        )

        page.add(
            ft.Container(
                ft.Column([
                    top_bar,
                    ft.Container(
                        ft.Column([
                            service_img,
                            title,
                            price_row,
                            ft.Divider(height=1, color="#E6F2F2"),
                            ft.Text("รายละเอียดบริการ", size=14, weight="bold", color="#1A7F7F", margin=ft.Margin(left=0, right=0, top=16, bottom=8)),
                            description,
                            ft.Container(height=24),
                            book_btn,
                        ], spacing=4),
                        expand=True
                    ),
                ], spacing=0, expand=True),
                padding=ft.Padding(left=16, right=16, top=16, bottom=16),
                bgcolor="#F4FAFB"
            )
        )
        page.update()

    # --- Booking Page ---
    def booking_page(service):
        page.selected_service = service
        page.booking_data = {
            "service": service,
            "service_type": page.booking_data.get("service_type"),
            "therapist": page.booking_data.get("therapist"),
            "strength": page.booking_data.get("strength"),
        }
        page.selected_type = page.booking_data.get("service_type")
        page.selected_therapist = page.booking_data.get("therapist")
        page.selected_strength = page.booking_data.get("strength")

        def clear_booking_selection():
            page.selected_type = None
            page.selected_therapist = None
            page.selected_strength = None
            page.booking_data["service_type"] = None
            page.booking_data["therapist"] = None
            page.booking_data["strength"] = None

        def back_to_detail(e):
            clear_booking_selection()
            navigate_to(detail_page, service)

        # Top bar
        top_bar = ft.Row([
            ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=back_to_detail),
            ft.Text("รักษาการจอง", size=18, weight="bold", color="#144883", expand=True),
        ], alignment="start")

        # Service Type Selection
        service_types = ["นวดเท้า", "นวดตัว", "นวดน้ำมัน"]
        service_type_buttons = ft.Row(scroll="auto", alignment="start", spacing=0)
        service_type_selected_text = ft.Text(
            f"คุณเลือก: {page.selected_type if page.selected_type else 'ยังไม่ได้เลือก'}",
            size=14,
            color="#2B4D4D",
            margin=ft.Margin(left=0, right=0, top=8, bottom=0),
        )

        def update_service_type_buttons():
            for child in service_type_buttons.controls:
                button = child.content
                if button.content == page.selected_type:
                    button.bgcolor = "#0F3A66"
                    button.color = "white"
                else:
                    button.bgcolor = "#E6F2F2"
                    button.color = "#144883"
                button.update()
            service_type_selected_text.value = f"คุณเลือก: {page.selected_type if page.selected_type else 'ยังไม่ได้เลือก'}"
            service_type_selected_text.update()

        def select_service_type(service_type):
            page.selected_type = service_type
            page.booking_data["service_type"] = service_type
            update_service_type_buttons()

        for service_type in service_types:
            service_type_buttons.controls.append(
                ft.Container(
                    ft.FilledButton(
                        service_type,
                        bgcolor="#0F3A66" if page.selected_type == service_type else "#E6F2F2",
                        color="white" if page.selected_type == service_type else "#144883",
                        height=50,
                        width=100,
                        on_click=lambda e, st=service_type: select_service_type(st),
                    ),
                    margin=ft.Margin(left=0, right=8, top=0, bottom=0),
                )
            )

        # Therapist Selection
        therapists = ["ไหม", "ปัญญา", "บุญญา", "สุภา"]
        therapist_buttons = ft.Row(scroll="auto", alignment="start", spacing=0)
        therapist_selected_text = ft.Text(
            f"คุณเลือก: {page.selected_therapist if page.selected_therapist else 'ยังไม่ได้เลือก'}",
            size=14,
            color="#2B4D4D",
            margin=ft.Margin(left=0, right=0, top=8, bottom=0),
        )

        def update_therapist_buttons():
            for child in therapist_buttons.controls:
                button = child.content
                if button.content == page.selected_therapist:
                    button.bgcolor = "#0F3A66"
                    button.color = "white"
                else:
                    button.bgcolor = "#E6F2F2"
                    button.color = "#144883"
                button.update()
            therapist_selected_text.value = f"คุณเลือก: {page.selected_therapist if page.selected_therapist else 'ยังไม่ได้เลือก'}"
            therapist_selected_text.update()

        def select_therapist(therapist):
            page.selected_therapist = therapist
            page.booking_data["therapist"] = therapist
            update_therapist_buttons()

        for therapist in therapists:
            therapist_buttons.controls.append(
                ft.Container(
                    ft.FilledButton(
                        therapist,
                        bgcolor="#0F3A66" if page.selected_therapist == therapist else "#E6F2F2",
                        color="white" if page.selected_therapist == therapist else "#144883",
                        height=50,
                        width=100,
                        on_click=lambda e, t=therapist: select_therapist(t),
                    ),
                    margin=ft.Margin(left=0, right=8, top=0, bottom=0),
                )
            )

        # Strength Level Selection
        strengths = ["อ่อน", "ปานกลาง", "แรง", "แรงมาก"]
        strength_buttons = ft.Row(scroll="auto", alignment="start", spacing=0)
        strength_selected_text = ft.Text(
            f"คุณเลือก: {page.selected_strength if page.selected_strength else 'ยังไม่ได้เลือก'}",
            size=14,
            color="#2B4D4D",
            margin=ft.Margin(left=0, right=0, top=8, bottom=0),
        )

        def update_strength_buttons():
            for child in strength_buttons.controls:
                button = child.content
                if button.content == page.selected_strength:
                    button.bgcolor = "#0F3A66"
                    button.color = "white"
                else:
                    button.bgcolor = "#E6F2F2"
                    button.color = "#144883"
                button.update()
            strength_selected_text.value = f"คุณเลือก: {page.selected_strength if page.selected_strength else 'ยังไม่ได้เลือก'}"
            strength_selected_text.update()

        def select_strength(strength):
            page.selected_strength = strength
            page.booking_data["strength"] = strength
            update_strength_buttons()

        for strength in strengths:
            strength_buttons.controls.append(
                ft.Container(
                    ft.FilledButton(
                        strength,
                        bgcolor="#0F3A66" if page.selected_strength == strength else "#E6F2F2",
                        color="white" if page.selected_strength == strength else "#144883",
                        height=60,
                        width=80,
                        on_click=lambda e, s=strength: select_strength(s),
                    ),
                    margin=ft.Margin(left=0, right=8, top=0, bottom=0),
                )
            )

        def confirm_booking(e):
            missing = []
            if not page.selected_type:
                missing.append("ประเภทการนวด")
            if not page.selected_therapist:
                missing.append("พนักงาน")
            if not page.selected_strength:
                missing.append("ระดับความแรง")

            if missing:
                page.snack_bar = ft.SnackBar(
                    ft.Text(f"กรุณาเลือก {' ,'.join(missing)}", color="white"),
                    bgcolor="#E53935"
                )
                page.snack_bar.open = True
                page.update()
                return
            navigate_to(confirmation_page)

        confirm_btn = ft.Container(
            ft.FilledButton(
                "ยืนยันการจอง",
                bgcolor="#144883",
                color="white",
                width=320,
                height=50,
                on_click=confirm_booking,
            ),
            margin=ft.Margin(left=0, right=0, top=16, bottom=0),
        )

        page.add(
            ft.Container(
                ft.Column([
                    top_bar,
                    ft.Container(
                        ft.Column([
                                    ft.Text("เลือกประเภทการนวด", size=16, weight="bold", color="#144883", margin=ft.Margin(left=0, right=0, top=16, bottom=8)),
                            service_type_buttons,
                            service_type_selected_text,
                            ft.Text("เลือกพนักงาน", size=16, weight="bold", color="#144883", margin=ft.Margin(left=0, right=0, top=16, bottom=8)),
                            therapist_buttons,
                            therapist_selected_text,
                            ft.Text("ระดับความแรง", size=16, weight="bold", color="#144883", margin=ft.Margin(left=0, right=0, top=16, bottom=8)),
                            strength_buttons,
                            strength_selected_text,
                            confirm_btn,
                        ], spacing=4),
                        expand=True,
                    ),
                ], spacing=0, expand=True),
                padding=ft.Padding(left=16, right=16, top=16, bottom=16),
                bgcolor="#F4FAFB",
            )
        )
        page.update()

    # --- Confirmation Page ---
    def confirmation_page():
        booking = page.booking_data
        service = booking.get("service", {})

        # Top bar
        top_bar = ft.Row([
            ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda e: navigate_to(booking_page, service)),
            ft.Text("ยืนยันการจอง", size=18, weight="bold", color="#144883", expand=True),
        ], alignment="start")

        # Summary
        summary = ft.Column([
            ft.Container(
                ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.HOTEL_CLASS, color="#144883", size=20),
                        ft.Text("บริการ:", weight="bold", color="#144883", size=14),
                        ft.Text(service.get("name", "N/A"), color="#2B4D4D", size=14, weight="bold", expand=True)
                    ], spacing=12, alignment="start"),
                    ft.Divider(color="#E0E0E0", height=1),
                    ft.Row([
                        ft.Icon(ft.Icons.SPA, color="#144883", size=20),
                        ft.Text("ประเภท:", weight="bold", color="#144883", size=14),
                        ft.Text(booking.get("service_type", "N/A"), color="#2B4D4D", size=14, weight="bold", expand=True)
                    ], spacing=12, alignment="start"),
                    ft.Divider(color="#E0E0E0", height=1),
                    ft.Row([
                        ft.Icon(ft.Icons.PERSON, color="#144883", size=20),
                        ft.Text("พนักงาน:", weight="bold", color="#144883", size=14),
                        ft.Text(booking.get("therapist", "N/A"), color="#2B4D4D", size=14, weight="bold", expand=True)
                    ], spacing=12, alignment="start"),
                    ft.Divider(color="#E0E0E0", height=1),
                    ft.Row([
                        ft.Icon(ft.Icons.FAVORITE, color="#144883", size=20),
                        ft.Text("ความแรง:", weight="bold", color="#144883", size=14),
                        ft.Text(booking.get("strength", "N/A"), color="#2B4D4D", size=14, weight="bold", expand=True)
                    ], spacing=12, alignment="start"),
                    ft.Divider(color="#E0E0E0", height=1),
                    ft.Row([
                        ft.Icon(ft.Icons.ATTACH_MONEY, color="#144883", size=20),
                        ft.Text("ราคา:", weight="bold", color="#144883", size=14),
                        ft.Text(f"฿{service.get('donation', 0)}", color="#144883", size=16, weight="bold", expand=True)
                    ], spacing=12, alignment="start"),
                ], spacing=12),
                bgcolor="white",
                padding=ft.Padding(left=16, right=16, top=16, bottom=16),
                border_radius=12,
                shadow=ft.BoxShadow(blur_radius=4, color="#E0E0E0", offset=ft.Offset(0, 2)),
            )
        ])

        # Confirm Button
        confirm_final_btn = ft.Container(
            ft.FilledButton(
                "ยืนยันและจอง",
                bgcolor="#144883",
                color="white",
                width=320,
                height=50,
                on_click=lambda e: save_booking()
            ),
            margin=ft.Margin(left=0, right=0, top=16, bottom=0)
        )

        def save_booking_to_db(booking_data: dict) -> bool:
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO massage_bookings
                       (service_id, service_name, service_type, therapist, strength,
                        customer_name, customer_phone, notes, status)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'pending')""",
                    (booking_data["service_id"], booking_data["service_name"],
                     booking_data["service_type"], booking_data["therapist"],
                     booking_data["strength"], booking_data["customer_name"],
                     booking_data["customer_phone"], booking_data["notes"]),
                )
                conn.commit()
                cursor.close()
                conn.close()
                print(f"Booking saved to DB")
                return True
            except Error as ex:
                print(f"Database booking error: {ex}")
                return False

        def save_booking():
            try:
                booking_data = {
                    "service_id": service.get("id"),
                    "service_name": service.get("name"),
                    "service_type": booking.get("service_type"),
                    "therapist": booking.get("therapist"),
                    "strength": booking.get("strength"),
                    "customer_name": "ลูกค้า",
                    "customer_phone": "",
                    "notes": ""
                }
                print(f"Sending booking request to {BOOKING_API_URL} with data: {booking_data}")
                success = False
                try:
                    response = requests.post(BOOKING_API_URL, json=booking_data, timeout=10)
                    print(f"Response status: {response.status_code}, OK: {response.ok}")
                    if not response.ok:
                        save_booking_to_db(booking_data)
                    success = True
                except Exception as api_ex:
                    print(f"API error, saving to DB: {api_ex}")
                    success = save_booking_to_db(booking_data)

                if success:
                    page.snack_bar = ft.SnackBar(
                        ft.Text("การจองสำเร็จ!", color="white"),
                        bgcolor="#4CAF50"
                    )
                    page.snack_bar.open = True
                    page.update()
                    page.booking_data = {
                        "service_type": None,
                        "therapist": None,
                        "strength": None,
                    }
                    page.current_tab = "home"
                    navigate_to(main_page)
                else:
                    page.snack_bar = ft.SnackBar(
                        ft.Text("ไม่สามารถบันทึกการจอง ลองใหม่อีกครั้ง", color="white"),
                        bgcolor="#E53935"
                    )
                    page.snack_bar.open = True
                    page.update()
            except Exception as ex:
                print(f"Exception in save_booking: {str(ex)}")
                page.snack_bar = ft.SnackBar(
                    ft.Text(f"เกิดข้อผิดพลาด: {str(ex)[:50]}", color="white"),
                    bgcolor="#E53935"
                )
                page.snack_bar.open = True
                page.update()

        page.add(
            ft.Container(
                ft.Column([
                    top_bar,
                    ft.Text("รายละเอียดการจอง", size=16, weight="bold", color="#144883", margin=ft.Margin(left=0, right=0, top=16, bottom=8)),
                    summary,
                    confirm_final_btn,
                ], spacing=12, expand=True),
                padding=ft.Padding(left=16, right=16, top=16, bottom=16),
                bgcolor="#F4FAFB"
            )
        )
        page.update()

    # --- Success Page ---
    def success_page():
        page.clean()
        page.title = "การจองสำเร็จ"

        def back_to_main(e):
            page.current_tab = "home"
            navigate_to(main_page)

        page.add(
            ft.Container(
                ft.Column([
                    ft.Container(height=60),
                    ft.Container(
                        ft.Icon(ft.Icons.CHECK_CIRCLE, size=80, color="#144883"),
                        padding=ft.Padding(left=0, right=0, top=16, bottom=16),
                    ),
                    ft.Text("การจองสำเร็จ!", size=26, weight="bold", color="#144883", text_align="center"),
                    ft.Text("ขอบคุณที่จองการนวดแผนไทยกับเรา", size=14, color="#6B7A7A", text_align="center"),
                    ft.Container(height=20),
                    ft.Container(
                        ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.INFO, color="#144883", size=20),
                                ft.Text("การจองของคุณอยู่ระหว่างการยืนยัน", size=13, color="#144883", weight="500", expand=True),
                            ], spacing=12),
                            ft.Text("คุณจะได้รับการติดต่อกลับในอีก 15 นาที", size=12, color="#6B7A7A"),
                        ], spacing=8),
                        bgcolor="white",
                        border_radius=12,
                        padding=ft.Padding(left=16, right=16, top=12, bottom=12),
                        shadow=ft.BoxShadow(blur_radius=4, color="#E0E0E0", offset=ft.Offset(0, 2)),
                    ),
                    ft.Container(height=40),
                    ft.FilledButton(
                        "กลับไปหน้าหลัก",
                        bgcolor="#144883",
                        color="white",
                        width=280,
                        height=50,
                        on_click=back_to_main
                    ),
                ], alignment="center", horizontal_alignment="center", expand=True, spacing=0),
                padding=ft.Padding(left=16, right=16, top=16, bottom=16),
                bgcolor="#F4FAFB"
            )
        )
        page.update()

    # Start at main page
    main_page()