import flet as ft
from flet import TextField, ElevatedButton, Text, Row, Column, ControlEvent, Page
import mysql.connector
import bcrypt

mydb = mysql.connector.connect(
    host="127.0.0.1",
    port=3306,
    user="root",
    password="root",
    database="chat"
)
cursor = mydb.cursor()


def main(page: ft.Page) -> None:
    page.title = "Databáze login"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.window_resizable = True

    user_name = TextField(label="Jméno (Napiš pravý jméno)")
    password = TextField(label="Heslo")
    button_submit = ElevatedButton(text="Registrovat účet.", width=200, disabled=True)

    def add_to_db(e):
        try:
            sql = "INSERT INTO user (user_name,password) VALUES(%s,%s)"
            hashed_password, _ = hash_password(password.value)
            val = (user_name.value, hashed_password)
            cursor.execute(sql, val)
            mydb.commit()
            print(cursor.rowcount, "YOUR RECORD INSERTED !!")
            show_success_message()
        except Exception as e:
            print(e)
            show_error_message("Hmmm Nějaký error se našel. Kontaktuj mě.")

    def show_success_message():
        page.clean()
        page.add(
            Row(
                controls=[Text(value="Účet byl zaregistrován!", size=20)],
                alignment=ft.MainAxisAlignment.CENTER
            )
        )

    def show_error_message(message):
        page.clean()
        page.add(
            Row(
                controls=[Text(value=message, size=20)],
                alignment=ft.MainAxisAlignment.CENTER
            )
        )

    def hash_password(password, salt=None):
        # Hash a password using bcrypt
        if salt is None:
            salt = bcrypt.gensalt()
        else:
            salt = salt.encode('utf-8')
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password, salt

    def validate(e: ControlEvent) -> None:
        if all([user_name.value, password.value]):
            button_submit.disabled = False
        else:
            button_submit.disabled = True
        page.update()

    user_name.on_change = validate
    password.on_change = validate
    button_submit.on_click = add_to_db



    page.add(
        Row(
            controls=[
                Column(
                    [user_name,
                     password,
                     button_submit]
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )
    )


if __name__ == "__main__":
    ft.app(main, view=ft.WEB_BROWSER)