import flet as ft
from flet import TextField, Checkbox, ElevatedButton, Text, Row, Column, ControlEvent, SnackBar, DataCell, DataRow, IconButton,DataTable,DataColumn,Page
import mysql.connector
import bcrypt

mydb = mysql.connector.connect(
   host="127.0.0.1",
    port=3306,
    user="root",
    password="rootroot",
    database="chat"
)
cursor = mydb.cursor()



def main(page: ft.Page) -> None:
    page.title = "Databáze login"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.window_width = 600
    page.window_height = 600
    page.window_resizable = True
    user_name = TextField(label="name")
    password = TextField(label="password")

    def addtodb(e):
        try:
            sql = "INSERT INTO user (user_name,password) VALUES(%s,%s)"
            val = (user_name.value, password.value)
            cursor.execute(sql,val)
            mydb.commit()
            print(cursor.rowcount,"YOUR RECORD INSERT !!")
            


            page.snack_bar = SnackBar(
                Text("Data success add", size=20),
                bgcolor="green"
            )
            page.snack_bar.open = True 
            page.update()

        except Exception as e:
            print(e)
            print("error")

    # nametxt.value = "aa"
    # user_nametxt.value = "a"
    page.update()

			

    #Setup
    text_username: TextField = TextField(label="Username", text_align=ft.TextAlign.LEFT, width=300)
    text_password: TextField = TextField(label="Pasword", text_align=ft.TextAlign.LEFT, width=300, password=True)

    button_submit: ElevatedButton = ElevatedButton(text="Sing up", width=200, disabled=True)
    button_sigin: ElevatedButton = ElevatedButton(text="Sing in", width=200)


    def hash_password(password, salt=None):
        # Hash a password using bcrypt
        if salt is None:
            salt = bcrypt.gensalt()
        else:
            salt = salt.encode('utf-8')

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password, salt

    #new
    def validate(e: ControlEvent) -> None:
        if all([text_username.value, text_password.value]):
            button_submit.disabled = False
        else:
            button_submit.disabled = True    

        page.update()

    def signin(e: ControlEvent) -> None:

        sql = "SELECT * FROM user WHERE user_name = %s OR email = %s LIMIT 1"
        cursor.execute(sql, (text_username.value,text_username.value))
        result = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        data = [dict(zip(columns, row)) for row in result]
        if not data:
            password, salt = hash_password(text_password.value)
            insert = "INSERT INTO user (user_name, password, salt) VALUES(%s,%s,%s)"
            val = (text_username.value, password, salt)
            cursor.execute(insert,val)
            mydb.commit()
            print(cursor.rowcount,"YOUR RECORD INSERT !!")
            submit(e)
        else:
            print("User already exists")
            page.clean()
            page.add(
                Row(
                    controls=[Text(value=f"User already exists: {text_username.value}", size=20)],
                    alignment=ft.MainAxisAlignment.CENTER
                )
            )


    def submit(e: ControlEvent) -> None:
        print("Username:", text_username.value)
        print("Password:", text_password.value)

        cursor.execute("SELECT * FROM user WHERE user_name = %s OR email = %s LIMIT 1", (text_username.value,text_username.value))
        result = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        data = [dict(zip(columns, row)) for row in result]

        print(data[0])
        if data:
            password, salt = hash_password(text_password.value, data[0]['salt'])
            print(password.decode("utf-8"))
            if data[0]['password'] == password.decode("utf-8"):
                page.clean()
                page.add(
                    Row(
                        controls=[Text(value=f"Funguje to: {text_username.value}", size=20)],
                        alignment=ft.MainAxisAlignment.CENTER
                    )
                )
            else:
                print("Wrong password")
        else:
            print("Not user found")
 
    text_username.on_change = validate
    text_password.on_change = validate
    button_submit.on_click = submit
    button_sigin.on_click = signin

    page.add(
        Row(
            controls=[
                Column(
                    [text_username,
                     text_password,
                     button_submit,
                     button_sigin]

                )
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )
    )

   


if __name__ == "__main__":
    ft.app(target=main)
