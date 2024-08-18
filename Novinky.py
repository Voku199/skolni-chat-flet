from flet import *
import flet as ft

# Novinky k zobrazení
NOVINKY_TEXT = """
*PATCH NOTE 1.0 ZŠT Šobra*

1. Plná verze chatu je už venku!
2. Databáze byla přidaná! (Díky tomu vidíte zprávy)
3. Kdo jsem, Otázky, Recenze a Nahlášení uživatele bylo přidáno!
4. V sekci "Nastavení" bylo přidáno "Bio", "Vlastní" tapety, Resetování hesla, A vlastní profilovky!
5. 2 Pravidla byly přidaní do pravidel!
6. Nevíš přihlasovací údaje? Tlačítko na "zapomenutý údaje" se ty zobrazí!
7. Lepší Registrace bylo přidáno! (Potvrdit hesla a atd..)
8. Odhlášení bylo přidáno!
9. Role, Třídy, Vlastní profilovky a zjištění uživatelského profilu bylo přidáno! (Stačí jenom kliknout na jeho profil)
10. Počet online uživatelu bylo přidáno! 
11. Stranka je veřejna jen pro ZŠ Tomáše Šobra
12. Změna v podpoře
13. Odebraný zjištění uživatele 
14. Nový bot byl přidán! Jmenuje se "Zib"!
15. !Help, !cl, !s, !user, !m, !av byly přidáni jako command! Byly taky přidání aj i pro vyšší role!
16. Vybrat jsi soubor a dát ho do chatu! 
17. Jinej styl sekce!
"""
NOVINKY_BUGS = """
*BUGS 1.0*

1. Když jsi se chtěl zaregistrovat, tak jsi nemusel dát třídu. Teďka je to opravené!
2. Nemohl jsi poslat zprávu víc jak 255 slov. Bylo opraveno
3. Když jsi kliknul odhlásit se, tak jsi byl předtím, takže kdo se zaregistroval, a odhlásil se, tak byl pořád na registraci. Bylo opraveno
4. Když jsi nebyl přihlášen, mohl jsi posílat zprávy. Bylo opraveno
"""
NOVINKY_NAD = """
*Nad čím se teďka pracuje?*

1. Vlastní emoji.
2. !cl 1+1+1+1 (Můžeš dát více toho příkladu)
3. Počásí (zjištění počasí)
4. Soukromý chat
5. Authorizované aplikace a přihlásit se přes tím
6. Achvimenty
7. MiniSpotify
8. Když otevřeš jinej tab, tak abys jsi byl přihlášen znovu.
"""


class Novinky(ft.UserControl):

    def __init__(self, page):
        super().__init__()
        self.page = page

    def build(self):
        return ft.Column(
            [
                ft.Text("Novinky:", weight=ft.FontWeight.BOLD, size=35),
                ft.Text(NOVINKY_TEXT, size=15, max_lines=20),
                ft.Text(NOVINKY_BUGS, size=15, max_lines=20),
                ft.Text(NOVINKY_NAD, size=15, max_lines=20),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            scroll=ft.ScrollMode.HIDDEN,
            spacing=10,
            expand=True,
            width=self.page.width - 10
        )


if __name__ == "__main__":
    def main(page: ft.Page):
        page.theme_mode = ft.ThemeMode.DARK
        page.window_always_on_top = True
        page.add(Novinky(page))


    ft.app(main, view=ft.WEB_BROWSER)
