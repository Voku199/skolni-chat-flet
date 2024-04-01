import flet as ft
from flet import Text, TextField, ElevatedButton, Switch, colors, Dropdown
import os
import mysql.connector
import bcrypt
import webbrowser
import socket
from utils import hash_password

mydb = mysql.connector.connect(
    host=os.environ["DB_HOST"],
    port=os.environ["DB_PORT"],
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASS"],
    database=os.environ["DB_NAME"]
)
cursor = mydb.cursor()


def build(self):
        return ft.Row(self.buttons, spacing=5)


class Nastavení(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.light_mode_switch = Switch(label="Tmavý režim", value=True, on_change=self.light_mode_changed)
        self.reset_password_button = ElevatedButton(text="Resetovat heslo", on_click=self.reset_password_click)
        self.chat_background = ft.colors.WHITE  # Defaultní barva pozadí chatu
        

    def build(self):
        return ft.Column(
            [
                ft.Text("Nastavení", weight=ft.FontWeight.BOLD, size=35),
                ft.Text("Vyberte režim světla:", size=20),
                self.light_mode_switch,
                self.reset_password_button,
                ft.Text("Nad dalším nastavením se pracuje! Jestli máte nějaké nápady co přidat do nastavení, ptejte se!", max_lines=20),
                
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            scroll=ft.ScrollMode.HIDDEN,
            spacing=7,
            expand=True,
            width=self.page.width-10
        )

    def light_mode_changed(self, e):
        if self.light_mode_switch.value:
            self.page.theme_mode = ft.ThemeMode.DARK
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT

    def reset_password_click(self, e):
        page = self.page
        page.clean()
        page.add(ResetHesla(page))
        page.add(ElevatedButton(text="Zpět k chatu", on_click=self.return_to_chat_click))

    def return_to_chat_click(self, e):
        # Zde přesměrujte uživatele na zadaný odkaz
        webbrowser.open("https://voku-skolni-chat.fly.dev/")

class ResetHesla(ft.UserControl):
    def __init__(self, page):

        tridy = []
        for i in range(9):
            tridy.append(ft.dropdown.Option(f"{i+1}.A"))
            tridy.append(ft.dropdown.Option(f"{i+1}.B"))
        super().__init__()
        self.user_name = TextField(label="Zadej uživatelské jméno:")
        self.trida = Dropdown(label="Třída", options=tridy)
        self.email = TextField(label="Zadej email : ")
        self.password = TextField(label="Zadej heslo:", password=True)
        self.password_confirm = TextField(label="Opakuj znovu heslo:", password=True)
        self.submit = ElevatedButton(text="Resetovat heslo", on_click=self.submit_click)
        self.error_message = Text("", color=ft.colors.RED, size=12)

        self.user_name.value = page.session.get("user_name")
        self.trida.value = page.session.get("user_class")
        self.email.value = page.session.get("user_email")


    def build(self):


        return ft.Column(
            [
                ft.Text("Resetování hesla", weight=ft.FontWeight.BOLD, size=35),
                self.user_name,
                self.trida,
                self.email,
                self.password,
                self.password_confirm,
                self.submit,
                self.error_message
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            scroll=ft.ScrollMode.HIDDEN,
            spacing=15,
            expand=True
        )

    def submit_click(self, e):
        if not self.user_name.value or not self.email.value or not self.password.value or not self.password_confirm.value:
            self.error_message.value = "Prosím, vyplňte všechna pole."
            self.error_message.update()
            print("Test3")
            return
    
        if self.password.value != self.password_confirm.value:
            self.error_message.value = "Hesla se neshodují."
            self.error_message.update()
            print ("Test2")
            return
        
      

        password, salt = hash_password(self.password_confirm.value)  # Upraveno na destrukci seznamu s jednou hodnotou
        print("Test4")

        user_id = self.page.session.get("user_id")
        print(user_id)

        try: 
            cursor.execute("UPDATE user SET class = %s, email = %s, password = %s, salt = %s WHERE id = %s", 
                           (self.trida.value, self.email.value, password, salt, user_id))
            mydb.commit()
        except e:
            print(e)
        
        
        result = cursor.rowcount
        print("Test1")

        if result:
            self.error_message.value = "Heslo změněno."
            self.error_message.update()
            print("Bylo")
        else:
            self.error_message.value = "Nastala chyba."
            self.error_message.update()
            print("Nebylo")


if __name__ == "__main__":
    def main(page: ft.Page):
        page.window_always_on_top = True
        page.add(Nastavení())
    ft.app(main, view=ft.WEB_BROWSER)