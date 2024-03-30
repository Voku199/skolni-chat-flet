import mysql.connector
import os
from flet import *
import flet as ft

# Připojení k databázi
mydb = mysql.connector.connect(
    host=os.environ["DB_HOST"],
    port=os.environ["DB_PORT"],
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASS"],
    database=os.environ["DB_NAME"]
)
cursor = mydb.cursor()

class Nahlaseni(ft.UserControl):

    def __init__(self):
        super().__init__()
        self.user_to_report = ft.TextField(label="Uživatel k nahlášení:")
        self.reason_to_report = ft.TextField(label="Důvod nahlášení:")
        self.submit_button = ft.ElevatedButton(text="Nahlásit uživatele", on_click=self.report_user)
        self.result_text = ft.Text("")


    def build(self):
        return ft.Column(
            [
                ft.Text("Nahlásit uživatele", weight=ft.FontWeight.BOLD, size=35),
                self.user_to_report,
                self.reason_to_report,
                self.submit_button,
                self.result_text,
                ft.Text("Když nahlásíte uživatele. Majitel se na to koukne a zajistí jestli by měl dostat mute nebo ne."),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            scroll=ft.ScrollMode.HIDDEN,
            spacing=7,
            expand=True
        )

    def report_user(self, e):
        report_guys = self.user_to_report.value
        reason = self.reason_to_report.value
        if report_guys:
            try:
                # Vložení nahlášeného uživatele do databáze
                cursor.execute("INSERT INTO report_guys (report_guys, reason) VALUES (%s, %s)", (report_guys, reason))
                mydb.commit()
                self.result_text.value = "Uživatel byl úspěšně nahlášen"
                self.update()
                print("Uživatel byl úspěšně nahlášen do databáze.")
            except mysql.connector.Error as err:
                print(f"Nastala chyba: {err}")
                self.result_text.value = "Nastala chyba"
                self.update()
        else:
            self.result_text.value = "Prosím, zadejte jméno uživatele k nahlášení."
            self.update()
            print("Nastala chyba1")

if __name__ == "__main__":
    def main(page: ft.Page):
        page.theme_mode = ft.ThemeMode.DARK
        page.window_always_on_top = True
        page.add(Nahlaseni())

    ft.app(main, view=ft.WEB_BROWSER)