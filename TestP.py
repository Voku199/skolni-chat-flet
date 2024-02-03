import flet as ft
from flet import TextField, Checkbox, ElevatedButton, Text, Row, Column, ControlEvent, SnackBar, DataCell, DataRow, IconButton,DataTable,DataColumn,Page
import mysql.connector


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
    page.window_width = 600
    page.window_height = 600
    page.window_resizable = True
    user_name = TextField(label="name")
    password = TextField(label="password")


   
		
    
    
        #Ok
    def deletebtn(e):
        pass

    def editbtn(e):
        pass   
    
    
    def load_data():
        login_name = "voku"
     

        page.update()  

    #Ok
    load_data()             

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
    chechbox_signup: Checkbox = Checkbox(label="Stuff", value= False)
    button_submit: ElevatedButton = ElevatedButton(text="Sing up", width=200, disabled=True)

    #new
    def validate(e: ControlEvent) -> None:
        if all([text_username.value, text_password.value, chechbox_signup.value]):
            button_submit.disabled = False
        else:
            button_submit.disabled = True    

        page.update()

    def submit(e: ControlEvent) -> None:
        print("Username:", text_username.value)
        print("Password:", text_password.value)

        cursor.execute("SELECT * FROM user WHERE user_name = %s OR email = %s LIMIT 1", (text_username.value,text_username.value))
        result = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        data = [dict(zip(columns, row)) for row in result]

        print(data)
        if data:
            if data[0].password == text_password.value:
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
            print("Wrong not user found")
 
    chechbox_signup.on_change = validate
    text_username.on_change = validate
    text_password.on_change = validate
    button_submit.on_click = submit

    page.add(
        Row(
            controls=[
                Column(
                    [text_username,
                     text_password,
                     chechbox_signup,
                     button_submit]
            
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )
    )

   


if __name__ == "__main__":
    ft.app(target=main)
