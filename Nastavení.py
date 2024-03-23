import flet as ft
from flet import Text, TextField, ElevatedButton, Switch, colors
import os
import mysql.connector
import bcrypt
import webbrowser
import socket
import re

mydb = mysql.connector.connect(
    host=os.environ["DB_HOST"],
    port=os.environ["DB_PORT"],
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASS"],
    database=os.environ["DB_NAME"]
)
cursor = mydb.cursor()

class ColorPalette(ft.UserControl):
    def __init__(self, on_select=None):
        super().__init__()
        self.on_select = on_select
        self.colors = [
            ft.colors.RED,
            ft.colors.PINK,
            ft.colors.PURPLE,
            ft.colors.DEEP_PURPLE,
            ft.colors.INDIGO,
            ft.colors.BLUE,
            ft.colors.LIGHT_BLUE,
            ft.colors.CYAN,
            ft.colors.TEAL,
            ft.colors.GREEN,
            ft.colors.LIGHT_GREEN,
            ft.colors.LIME,
            ft.colors.YELLOW,
            ft.colors.AMBER,
            ft.colors.ORANGE,
            ft.colors.DEEP_ORANGE,
            ft.colors.BROWN,
            ft.colors.GREY,
            ft.colors.BLUE_GREY,
            ft.colors.WHITE,
            ft.colors.BLACK,
        ]
        self.buttons = []
        for color in self.colors:
            button = ft.ElevatedButton(
                text="",
                bgcolor=color,
                on_click=self.on_color_select
            )
            self.buttons.append(button)

    def build(self):
        return ft.Row(self.buttons, spacing=5)

    def on_color_select(self, e):
        if callable(self.on_select):
            self.on_select(e.control.bgcolor)

class Nastavení(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.light_mode_switch = Switch(label="Tmavý režim", value=True, on_change=self.light_mode_changed)
        self.reset_password_button = ElevatedButton(text="Resetovat heslo", on_click=self.reset_password_click)
        self.chat_color_textfield = TextField(label="Hex kód barvy pozadí chatu", value="#FFFFFF", on_change=self.color_changed)
        self.change_color_button = ElevatedButton(text="Změnit barvu")
        self.change_color_button.on_click = self.change_color_click
        self.chat_background = ft.colors.WHITE  # Defaultní barva pozadí chatu
        self.trida_textfield = TextField(label="Zadej třídu:", on_change=self.trida_changed)
        self.apply_trida_button = ElevatedButton(text="Aplikovat třídu", on_click=self.apply_trida_click)
        self.jmeno_s_tridou = Text("")
        self.user_with_trida = ""

    def build(self):
        return ft.Column(
            [
                ft.Text("Nastavení", weight=ft.FontWeight.BOLD, size=35),
                ft.Text("Vyberte režim světla:", size=20),
                self.light_mode_switch,
                self.chat_color_textfield,
                self.change_color_button,
                self.reset_password_button,
                self.trida_textfield,
                self.apply_trida_button,
                self.jmeno_s_tridou,
                ft.Text("Nad dalším nastavením se pracuje! Jestli máte nějaké nápady co přidat do nastavení, ptejte se!"),
                
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            scroll=ft.ScrollMode.HIDDEN,
            spacing=7,
            expand=True
        )

    def light_mode_changed(self, e):
        if self.light_mode_switch.value:
            self.page.theme_mode = ft.ThemeMode.DARK
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT

    def color_changed(self, e):
        selected_color = e.control.value
        self.page.background_color = selected_color
        self.page.update()

    def change_color_click(self, e):
        # Zde můžete implementovat logiku pro změnu barvy chatu
        palette = ColorPalette(on_select=self.on_color_select)
        self.page.add(palette)

    def on_color_select(self, selected_color):
        self.chat_color_textfield.value = selected_color
        self.page.update()

    def reset_password_click(self, e):
        page = self.page
        page.clean()
        page.add(ResetHesla())
        page.add(ElevatedButton(text="Zpět k chatu", on_click=self.return_to_chat_click))

    def return_to_chat_click(self, e):
        # Zde přesměrujte uživatele na zadaný odkaz
        webbrowser.open("https://example.com/chat")

    def trida_changed(self, e):
        self.trida = e.control.value  # Aktualizace hodnoty atributu trida podle zadání uživatelem
        print("Zadaná třída:", self.trida)

    def apply_trida_click(self, e):
        self.user_with_trida = f"{"user"} ({self.user_with_trida})"
        self.jmeno_s_tridou.value = self.user_with_trida

    def login_user(self, login):
        text_username = self.page.get_control("text_username")
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        user = login["user"]["user_name"]
        trida = login["user"]["trida"]  # Získání třídy uživatele
        self.user_with_trida = f"{user} ({trida})"  # Vytvoření jména uživatele s třídou
        self.page.session.set("user_name", self.user_with_trida)
        self.page.session.set("user_id", login["user"]["id"])
        self.page.dialog.open = False
        new_message = self.page.get_control("new_message")
        new_message.prefix = ft.Text(f"{self.user_with_trida}: ")
        self.page.pubsub.send_all(ft.Message(user_name=self.user_with_trida, text=f"{self.user_with_trida} Se připojil do chatu!. Jeho IP: {ip_address}", message_type="login_message"))
        self.page.update()

class ResetHesla(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.user_name = TextField(label="Zadej uživatelské jméno:")
        self.class_name = TextField(label="Zadej třídu:")
        self.email = TextField(label="Zadej email : ")
        self.password = TextField(label="Zadej heslo:", password=True)
        self.password_confirm = TextField(label="Opakuj znovu heslo:", password=True)
        self.submit = ElevatedButton(text="Resetovat heslo", on_click=self.submit_click)

    def build(self):
        return ft.Column(
            [
                ft.Text ("Resetování hesla", weight=ft.FontWeight.BOLD, size=35),
                self.user_name,
                self.class_name,
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
            return
        
        if self.password.value != self.password_confirm.value:
            self.error_message.value = "Hesla se neshodují."
            self.error_message.update()
            return

        password, salt = (self.password_confirm.value)

        # Kontrola formátu třídy
        if not re.match(r'^\d+\.[A-Za-b]+$', self.class_name.value):
            self.error_message.value = "Špatný formát třídy. Použijte číslo následované tečkou a písmeny, např. 9.A."
            self.error_message.update()
            return

        cursor.execute("UPDATE user SET email = %s, password = %s, salt = %s WHERE user_name = %s AND class_name = %s", (self.email.value, password, salt, self.user_name.value, self.class_name.value))
        result = cursor.fetchone()

        if result:
            stored_password = result[2]  # Heslo uložené v databázi
            salt = result[4]  # Sůl uložená v databázi

            # Porovnání zadaného hesla s uloženým heslem
            if bcrypt.checkpw(self.password.value.encode('utf-8'), stored_password.encode('utf-8')):
                # Zde by byl kód pro odeslání emailu s odkazem na resetování hesla
                self.error_message.value = "Odkaz pro resetování hesla byl odeslán na váš email."
            else:
                self.error_message.value = "Nesprávné uživatelské jméno, email nebo heslo."
        else:
            self.error_message.value = "Uživatel s tímto uživatelským jménem a emailem neexistuje."
        self.error_message.update()

if __name__ == "__main__":
    def main(page: ft.Page):
        page.window_always_on_top = True
        page.add(Nastavení())
    ft.app(main, view=ft.WEB_BROWSER)
