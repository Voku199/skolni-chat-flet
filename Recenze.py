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


class Recenze(ft.UserControl):
    def __init__(self, page):
        super().__init__()
        self.page = page
        user_name = page.session.get("user_name")  # Get the user_name from the session
        self.user_name = ft.TextField(label=f"Vaše jméno: {user_name}" if user_name else "Vaše jméno:")
        self.review_text = ft.TextField(label="Napiš recenzi:")
        self.submit_button = ft.ElevatedButton(text="Odeslat recenzi", on_click=self.submit_review)
        self.result_text = ft.Text("")
        self.reviews_list = ft.Column()
        self.load_reviews()
        print(f"{user_name} oka")

    def build(self):
        return ft.Column(
            [
                ft.Text("Přidat recenzi", weight=ft.FontWeight.BOLD, size=35),
                self.user_name,
                self.review_text,
                self.submit_button,
                self.result_text,
                ft.Text("Zde můžete přidat své recenze k našemu produktu nebo službě.", max_lines=20),
                ft.Divider(),
                ft.Text("Recenze:", weight=ft.FontWeight.BOLD, size=25),
                self.reviews_list,
            ],
            alignment=ft.MainAxisAlignment.START,
            scroll=ft.ScrollMode.HIDDEN,
            spacing=10,
            expand=True,
            width=self.page.width - 10
        )

    def submit_review(self, e):
        user_name = self.user_name.value.strip()
        review_text = self.review_text.value.strip()
        if review_text and self.user_name.value:
            try:
                # Vložení recenze do databáze
                cursor.execute("INSERT INTO reviews (user_name, review_text) VALUES (%s, %s)", (user_name, review_text))
                mydb.commit()
                self.result_text.value = "Recenze byla úspěšně odeslána"
                self.result_text.color = ft.colors.GREEN_500
                self.update()
                self.add_review_to_list(user_name, review_text)
                self.user_name.value = ""
                self.review_text.value = ""
            except mysql.connector.Error as err:
                print(f"Nastala chyba: {err}")
                self.result_text.value = "Nastala chyba"
                self.result_text.color = ft.colors.RED_500
                self.update()
        else:
            self.result_text.value = "Prosím, napište recenzi."
            self.result_text.color = ft.colors.RED_500
            self.update()

    def load_reviews(self):
        pass
        try:
            # Načtení recenzí z databáze
            cursor.execute("SELECT user_name, review_text FROM reviews ORDER BY id DESC")
            for (user_name, review_text) in cursor:
                self.add_review_to_list(user_name, review_text)
        except mysql.connector.Error as err:
            print(f"Nastala chyba: {err}")

    def add_review_to_list(self, user_name, review_text):
        self.reviews_list.controls.append(
            ft.Row(
                controls=[
                    ft.Text(f"{user_name}: ", weight=ft.FontWeight.BOLD),
                    ft.Text(review_text),
                ]
            )
        )
        self.page.update()


if __name__ == "__main__":
    def main(page: ft.Page):
        # global user_name
        page.theme_mode = ft.ThemeMode.DARK
        page.window_always_on_top = True
        page.session.get("user_name")
        page.add(Recenze(page))


    ft.app(main, view=ft.WEB_BROWSER)
