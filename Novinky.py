import random

from flet import *
import flet as ft


# todo: change  link to docs

# the content of the blur tab
class Novinky(ft.UserControl):

    def __init__(self):
        super().__init__()

    def build(self):

        return ft.Column(
            [
                ft.Text("Novinky:", weight=ft.FontWeight.BOLD, size=21),
                ft.Text("Moje novinky..."),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            scroll=ft.ScrollMode.HIDDEN,
            spacing=30,
            expand=True
        )



if __name__ == "__main__":
    def main(page: ft.Page):
        page.theme_mode = ft.ThemeMode.LIGHT
        page.window_always_on_top = True
        page.add(Novinky())


    ft.app(main, view=ft.WEB_BROWSER)