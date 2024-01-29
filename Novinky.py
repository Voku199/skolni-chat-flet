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
                ft.Text("Update Beta Verze"),
                ft.Text("Stranka byla veřejná jen pro vybrané lidi!"),
                ft.Text("Pravidla byly přidaní"),
                ft.Text("Styl stranky (jak vypadá)"),
                ft.Text("Zjištení IP adressy od lidí (Když stranka nebude v beta verze, tahle možnost bude odebraná)"),
                ft.Text("Čeština byla přidaná!"),
                ft.Text("Podpora byla přidaná! (Kde mě můžete kontaktovat a atd...)"),
                ft.Text("O dalších nápadech mi zkuste napsat!"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            scroll=ft.ScrollMode.HIDDEN,
            spacing=15,
            expand=True
        )



if __name__ == "__main__":
    def main(page: ft.Page):
        page.theme_mode = ft.ThemeMode.DARK
        page.window_always_on_top = True
        page.add(Novinky())


    ft.app(main, view=ft.WEB_BROWSER)