import flet as ft
from flet import Text, TextField, ElevatedButton, Switch, colors, Dropdown, FilePicker
import os
import mysql.connector
from pathlib import Path
import base64
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
    def __init__(self, page):
        super().__init__()
        self.light_mode_switch = Switch(label="Tmavý režim", value=True, on_change=self.light_mode_changed)
        self.reset_password_button = ElevatedButton(text="Resetovat heslo", on_click=self.reset_password_click)
        self.chat_background = ft.colors.WHITE  # Defaultní barva pozadí chatu
        self.page = page
        self.wallpaper_dropdown = Dropdown(label="Vyberte tapetu:", options=[
            ft.dropdown.Option("Žluto/Oranžová"),
            ft.dropdown.Option("Růžovo/Fialová"),
            ft.dropdown.Option(""),
            ft.dropdown.Option("Černá"),
            # Přidejte další barvy podle potřeby
        ], on_change=self.wallpaper_changed)
        self.pick_file_button = ElevatedButton(text="Vybrat soubor", on_click=self.pick_file_click)
        

    def build(self):
        return ft.Column(
            [
                ft.Text("Nastavení", weight=ft.FontWeight.BOLD, size=35),
                ft.Text("Vyberte režim světla:", size=20),
                self.light_mode_switch,
                self.reset_password_button,
                ft.Text("Vyberte tapetu:", size=20),
                self.wallpaper_dropdown,
                ft.Text("Vyberte soubor:", size=20),
                self.pick_file_button,
                ft.Text("Nad dalším nastavením se pracuje! Jestli máte nějaké nápady co přidat do nastavení, ptejte se!", 
                        max_lines=20
                        ),
                
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

    def wallpaper_changed(self, e):
        # Změna barvy pozadí chatu podle výběru
        selected_wallpaper = self.wallpaper_dropdown.value
        if selected_wallpaper == "Žluto/Oranžová":
            self.page.bgcolor = ft.colors.YELLOW_800
        elif selected_wallpaper == "Růžovo/Fialová":
            self.page.bgcolor = ft.colors.PINK_800
        elif selected_wallpaper == "":
            self.page.bgcolor = ft.colors.TEAL_50
        elif selected_wallpaper == "Černá":
            self.page.bgcolor = ft.ThemeMode.DARK   
        
        self.page.update()  # Aktualizace stránky


    def pick_file_click(self, e):
        file_picker = FilePicker(on_result=self.file_picker_result)
        file_picker.allowed_extensions = [".jpg", ".jpeg", ".png"]  # Set allowed file extensions
        self.page.overlay.append(file_picker)  # Přidání FilePickeru na stránku
        self.page.update()  # Aktualizace stránky pro zobrazení FilePickeru
        file_picker.pick_files(allow_multiple=False) 

    def file_picker_result(self, e: ft.FilePickerResultEvent):
        if e.files:
            selected_file = e.files[0]  # Získání vybraného souboru
            print("Vybraný soubor:", selected_file.name)

        # Zde zkontrolujeme, zda je vybraný soubor obrázek
            if selected_file.name.lower().endswith((".jpg", ".jpeg", ".png")):
                try:
                    file_path = os.path.abspath(selected_file.name)
                    with open(file_path, "rb") as file:
                        file_data = file.read()  # Čtení binárních dat souboru

            # Kódování binárních dat pomocí Base64
                    base64_data = base64.b64encode(file_data).decode('utf-8')

            # Vytvoříme src pro obrázek jako data URL
                    src = f"data:image/{selected_file.name.split('.')[-1]};base64,{base64_data}"

            # Vytvoříme obrázek
                    image = ft.Image(src=src, width=400, height=400)

            # Vytvoříme dialogové okno pro zobrazení obrázku
                    self.image_dialog = ft.AlertDialog(
                        title=ft.Text("Zobrazení obrázku"),
                        content=ft.Column([
                            image,
                            ft.ElevatedButton("Uložit do databáze", on_click=lambda e: self.save_profile_picture_to_db(base64_data))
                        ], width=500, height=500, tight=True ),
                        actions=[ft.TextButton("Zavřít", on_click=self.close_dialog)],
                    )

            # Zobrazíme dialogové okno
                    self.page.dialog = self.image_dialog
                    self.page.dialog.open = True
                    self.page.update()
                except Exception as ex:
                    print("Chyba při čtení souboru:", ex)
            else:
                print("Vybraný soubor není obrázek.")
        else:
            print("Operace byla zrušena.")

    def save_profile_picture_to_db(self, base64_data):
        try:
            user_id = self.page.session.get("user_id")  # Předpokládáme, že user_id je uložen v session
            if user_id is None:
                print("Uživatel není přihlášen.")
                return

            cursor.execute("UPDATE user SET profile_picture = %s WHERE id = %s", (base64_data, user_id))
            mydb.commit()
            print("Profilový obrázek uložen do databáze.")
            self.close_dialog(None)
        except Exception as ex:
            print("Chyba při ukládání profilového obrázku do databáze:", ex)


    def close_dialog(self, e):
        self.image_dialog.open = False
        self.page.update()
    
    
    def _logout(page: ft.Page, chat):
        page.session.clear()
        chat.controls.clear()
        page.dialog.open = True
        page.update()
        

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
