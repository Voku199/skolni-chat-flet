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
                ft.Text("Zde se budou vypysovat novinky co se zde přidalo. ", weight=ft.FontWeight.BOLD, size=15 ),
                ft.Text("Plná verze zstsobra chatu je venku!"),
                ft.Text("Databáze zde byla přidaná! (čímz díky tomu máte aj i heslo a třídu.)"),
                ft.Text("Kdo jsem? Bylo přidano! Tam zjistíte kdo jsem, a proč jsme to udělal tuhle stranku"),
                ft.Text("Otazky. Otázky byly přidaní! "),
                ft.Text("Nastavení bylo přidáno! Neboli světlý a tmavý režim, a změna hesla!"),
                ft.Text("2 Pravidla byly přidání do sekce Pravidel!"),
                ft.Text("Nevíš heslo, nebo přihlasovací údaje? Na úvodní strance se objeví se ti tam ikonka s názvem : zapomenutý heslo?"),
                ft.Text("Registrace bylo přidáno!"),
                ft.Text("Odhlášení bylo přidáno!"),
                ft.Text("Třídy byly přidání!"),
                ft.Text("Počet online uživatelu! (Nefunguje nejlíp)"),
                ft.Text("Stranka je veřejná pro žáky Zstsobra (samozřejmě aj i pro učitele)"),
                ft.Text("Nahlašení uživatele je zde! Můžete nahlásit uživatele"),
                ft.Text("Plakáty po celým škole! (Možná) "),
                ft.Text("Změna v Podpoře!"),
                ft.Text("Odebráný zjištění IP adressy uživatele."),
                ft.Text("Zobrazený zpráv když někdo se připojí. (Co jste viděli poprvé)"),
                ft.Text("Nad vlastníma profilovíma obrázkama se precuje!"),
                ft.Text("Nad zapamatování systemu když omylem křížek na tabu!"),
                ft.Text("Nad hrama v prohlížeci se pracuje 👀"),
                ft.Text("Nad specialním updatě se pracuje 👀"),
            
                 
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