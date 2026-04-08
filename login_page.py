import os
import flet as ft
import mysql.connector
from dotenv import load_dotenv
from mysql.connector import Error

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "192.168.100.22"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "database": os.getenv("DB_NAME", "donation"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "P@ssword"),
}


def main(page: ft.Page):
    page.title = "Login"
    page.bgcolor = "#144883"
    page.scroll = "auto"

    username_field = ft.TextField(
        label="Username",
        color="#144883",
        bgcolor="white",
        border_radius=8,
        border_color="#E0E0E0",
        focused_border_color="#1A7F7F",
        focused_bgcolor="#F5FAFB",
        label_style=ft.TextStyle(color="#999999", size=13),
        text_style=ft.TextStyle(color="#144883", size=14),
        content_padding=ft.Padding(left=16, right=16, top=14, bottom=14),
        height=50,
        width=350,
    )
    password_field = ft.TextField(
        label="Password",
        password=True,
        color="#144883",
        bgcolor="white",
        border_radius=8,
        border_color="#E0E0E0",
        focused_border_color="#1A7F7F",
        focused_bgcolor="#F5FAFB",
        label_style=ft.TextStyle(color="#999999", size=13),
        text_style=ft.TextStyle(color="#144883", size=14),
        content_padding=ft.Padding(left=16, right=16, top=14, bottom=14),
        height=50,
        width=350,
    )
    alert_text = ft.Text("", color="#E53935", visible=False, size=14, weight="bold")
    snack_bar = ft.SnackBar(content=ft.Text(""))

    def authenticate_user(username: str, password: str) -> bool:
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT password FROM user_login WHERE username = %s",
                (username,),
            )
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            if row and row[0] == password:
                return True
            return False
        except Error as ex:
            print(f"Database login error: {ex}")
            return False

    def login_action(e):
        username = username_field.value or ""
        password = password_field.value or ""
        
        if not username or not password:
            snack_bar.content = ft.Text("กรุณากรอกชื่อผู้ใช้และรหัสผ่าน", color="white")
            snack_bar.bgcolor = "#E53935"
            page.snack_bar = snack_bar
            snack_bar.open = True
            page.update()
            return

        if authenticate_user(username, password):
            snack_bar.content = ft.Text("เข้าสู่ระบบสำเร็จ!", color="white")
            snack_bar.bgcolor = "#4CAF50"
            page.snack_bar = snack_bar
            snack_bar.open = True
            page.update()
            # Set login state and navigate to main app
            page.is_logged_in = True
            page.clean()
            import flet_app
            flet_app.main(page)
            return

        snack_bar.content = ft.Text("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง", color="white")
        snack_bar.bgcolor = "#E53935"
        page.snack_bar = snack_bar
        snack_bar.open = True
        username_field.value = ""
        password_field.value = ""
        page.update()

    page.clean()
    page.add(
        ft.Container(
            bgcolor="#144883",
            expand=True,
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Container(height=40),  # Top spacing
                            ft.Text(
                                "Welcome Back!",
                                size=32,
                                weight="bold",
                                color="white",
                                text_align="center",
                            ),
                            ft.Text(
                                "Sign in to your account",
                                size=16,
                                color="#B0C4E0",
                                text_align="center",
                            ),
                            ft.Container(height=40),  # Spacing
                            ft.Text("Username", size=14, color="white", weight="w500"),
                            username_field,
                            ft.Container(height=20),
                            ft.Text("Password", size=14, color="white", weight="w500"),
                            password_field,
                            ft.Container(height=30),
                            ft.FilledButton(
                                "Login",
                                on_click=login_action,
                                bgcolor="#1A7F7F",
                                color="white",
                                width=350,
                                height=50,
                            ),
                        ],
                        width=400,
                        horizontal_alignment="center",
                        alignment="start",
                    )
                ],
                expand=True,
                alignment="center",
                vertical_alignment="center",
            ),
        )
    )
    page.update()

if __name__ == "__main__":
    ft.run(main)
