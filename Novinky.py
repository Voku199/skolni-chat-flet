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
                ft.Text("Novinky:", weight=ft.FontWeight.BOLD, size=35),
                ft.Text("Zde se budou psát novinky ohledně toho jestli se zde něco přidalo. Neboli Updaty ohledně tohotle stranky!",weight=ft.FontWeight.BOLD, size=20 ),
                ft.Text("Databáze přidáno!",),
                ft.Text("Registorvání účtu bylo přidáno",),
                ft.Text("Nad automatický pamatování že jsi/jste se přihlásili se pracuje nad tím",),
                ft.Text("Odhlásení systemu bylo přidáno",),
                ft.Text("Nastavení bylo přidáno!",),
                ft.Text("Nad velikonočním update se pracuje!",),
                ft.Text("",),
                 
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            scroll=ft.ScrollMode.HIDDEN,
            spacing=10,
            expand=True
        )



if __name__ == "__main__":
    def main(page: ft.Page):
        page.theme_mode = ft.ThemeMode.DARK
        page.window_always_on_top = True
        page.add(Novinky())


    ft.app(main, view=ft.WEB_BROWSER)