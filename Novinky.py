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
                ft.Text("Novinky:", weight=ft.FontWeight.BOLD, size=35, max_lines=20),
                ft.Text("Zde se budou vypysovat novinky co se zde přidalo. ", weight=ft.FontWeight.BOLD, size=15, max_lines=20),
                ft.Text("Plná verze zstsobra chatu je venku!", max_lines=20),
                ft.Text("Databáze zde byla přidaná! (čímz díky tomu máte aj i heslo a třídu.)", max_lines=20),
                ft.Text("Kdo jsem? Bylo přidano! Tam zjistíte kdo jsem, a proč jsme to udělal tuhle stranku", max_lines=20),
                ft.Text("Otazky. Otázky byly přidaní! ", max_lines=20),
                ft.Text("Nastavení bylo přidáno! Neboli světlý a tmavý režim, a změna hesla!", max_lines=20),
                ft.Text("2 Pravidla byly přidání do sekce Pravidel!", max_lines=20),
                ft.Text("Nevíš heslo, nebo přihlasovací údaje? Na úvodní strance se objeví se ti tam ikonka s názvem : zapomenutý heslo?", max_lines=20),
                ft.Text("Registrace bylo přidáno!", max_lines=20),
                ft.Text("Odhlášení bylo přidáno!", max_lines=20),
                ft.Text("Třídy byly přidání!", max_lines=20),
                ft.Text("Počet online uživatelu! (Nefunguje nejlíp)", max_lines=20),
                ft.Text("Stranka je veřejná pro žáky Zstsobra (samozřejmě aj i pro učitele)", max_lines=20),
                ft.Text("Nahlašení uživatele je zde! Můžete nahlásit uživatele", max_lines=20),
                ft.Text("Plakáty po celým škole! (Možná) ", max_lines=20),
                ft.Text("Změna v Podpoře!", max_lines=20),
                ft.Text("Odebráný zjištění IP adressy uživatele.", max_lines=20),
                ft.Text("Zobrazený zpráv když někdo se připojí. (Co jste viděli poprvé)", max_lines=20),
                ft.Text("Nad vlastníma profilovíma obrázkama se precuje!", max_lines=20),
                ft.Text("Nad zapamatování systemu když omylem křížek na tabu!", max_lines=20),
                ft.Text("Nad hrama v prohlížeci se pracuje 👀", max_lines=20),
                ft.Text("Nad specialním updatě se pracuje 👀", max_lines=20),
            
                 
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            scroll=ft.ScrollMode.HIDDEN,
            spacing=10,
            expand=True,
            width=self.page.width-10
        )



if __name__ == "__main__":
    def main(page: ft.Page):
        page.theme_mode = ft.ThemeMode.DARK
        page.window_always_on_top = True
        page.add(Novinky())


    ft.app(main, view=ft.WEB_BROWSER)