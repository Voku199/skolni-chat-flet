import flet as ft
from flet import ElevatedButton

class ChangeBackground(ft.UserControl):
    def __init__(self, page):
        super().__init__()
        self.page = page
        # Přidáme přepínače nebo tlačítka pro výběr barvy
        self.red_button = ElevatedButton(text="Červená", on_click=self.change_to_red)
        self.green_button = ElevatedButton(text="Zelená", on_click=self.change_to_green)
        self.blue_button = ElevatedButton(text="Modrá", on_click=self.change_to_blue)

    def build(self):
        return ft.Column(
            [
                ft.Text("Změnit barvu pozadí"),
                self.red_button,
                self.green_button,
                self.blue_button
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
        )

    def change_to_red(self, e):
        self.page.bgcolor = ft.colors.RED
        self.page.update()  # Aktualizace stránky pro zobrazení změny

    def change_to_green(self, e):
        self.page.bgcolor = ft.colors.GREEN
        self.page.update()

    def change_to_blue(self, e):
        self.page.bgcolor = ft.colors.BLUE
        self.page.update()

def main(page: ft.Page):
    page.add(ChangeBackground(page))

ft.app(main)