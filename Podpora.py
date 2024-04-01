import random
from flet import *
import flet as ft
# todo: change  link to docs
# the content of the blur tab
class Podpora(ft.UserControl):
    def __init__(self):
        super().__init__()
    def build(self):
        return ft.Column(
            [
                ft.Text("Podpora", weight=ft.FontWeight.BOLD, size=35, max_lines=20,),
                ft.Text("Chceš mě finnančně podpořit? Nebo máš nějaký problém ohledně stránky? Kontaktuj mě a vyřešíme to",weight=ft.FontWeight.BOLD, size=15, max_lines=20),
                ft.Text("Moje kontakty najdeš zde!", weight=ft.FontWeight.BOLD, max_lines=20),
                ft.Text("Email : vojta.kurinec@gmail.com", max_lines=20),
                ft.Text("Moje telefoní číslo : napiš si o něj ;)", max_lines=20),
                ft.Text("Outlouk : kurinecv15@zstsobra.cz", max_lines=20),
                ft.Text("Zde mě můžeš finančně podpořit!", weight=ft.FontWeight.BOLD, max_lines=20),
                ft.ElevatedButton("Klikni zde pro podporu!", on_click=lambda e: self.page.launch_url("https://paypal.me/PodporaChatu")),
                ft.Text("Peníze co pošleš půjde na podporu, nebudeš moct si o ně žažádat zpátky, jestli by to bylo omylem, tak bych potřeboval důkaz a co se všechno stalo", weight=ft.FontWeight.BOLD, size=15, max_lines=20),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            scroll=ft.ScrollMode.HIDDEN,
            spacing=15,
            expand=True,
            width=self.page.width-10
        )


if __name__ == "__main__":
    def main(page: ft.Page):
        page.theme_mode = ft.ThemeMode.DARK
        page.window_always_on_top = True
        page.add(Podpora())
    ft.app(main, view=ft.WEB_BROWSER)