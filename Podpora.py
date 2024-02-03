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
                ft.Text("Podpora!", weight=ft.FontWeight.BOLD, size=35),
                ft.Text("Chceš pomoc s něčím a nejseš jsi rady? Chceš někdo tak aby získal ban kvůli tomu že porušil pravidlo? Nebo chceš jenom mě podpořit finančně? Zde bude všechno ohledně tohotle!",weight=ft.FontWeight.BOLD, size=20),
                ft.Text("Moje kontakty najdeš zde!", weight=ft.FontWeight.BOLD),
                ft.Text("Email : vojta.kurinec@gmail.com"),
                ft.Text("Moje telefoní číslo : +420 721 055 334"),
                ft.Text("Moje telefoní číslo : napiš si o něj ;)"),
                ft.Text("Můj discord : voku199"),
                ft.Text("Snapchat : voku199"),
                ft.Text("Zde mě můžeš finančně podpořit!", weight=ft.FontWeight.BOLD),
                ft.Text("https://paypal.me/PodporaChatu (musíš to přepsat bohužel)"),
                ft.ElevatedButton("Klikni zde pro podporu!", on_click=lambda e: self.page.launch_url("https://paypal.me/PodporaChatu")),
                ft.Text("Peníze co pošleš půjde na podporu, nebudeš moct si o ně žažádat zpátky, jestli by to bylo omylem, tak bych poprosil důkaz a co se všechno stalo", weight=ft.FontWeight.BOLD, size=15),
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
        page.add(Podpora())
    ft.app(main, view=ft.WEB_BROWSER)