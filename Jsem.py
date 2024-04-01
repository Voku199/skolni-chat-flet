import random

from flet import *
import flet as ft


# todo: change  link to docs

# the content of the blur tab
class Jsem(ft.UserControl):

    def __init__(self):
        super().__init__()

    def build(self):

        return ft.Column(
            [
                ft.Text("Kdo jsem?", weight=ft.FontWeight.BOLD, size=35, max_lines=20),
                ft.Text("Ahoj. Jmenuji se Vojtěch Kurinec. Jsem v 6 třídě a je mi 13 let (V tomhle roce 14). Moje koníčky jsou : Programování, Šachy, Tančení.",weight=ft.FontWeight.BOLD, size=15, max_lines=20),
                ft.Text("Chat pro školu jsem chtěl udělat kvůli tomu, tak aby jsi mezi třídy mohli bavit ohledně něčeho, napřiklad o tom jak se vypočítavá tohle a atd... Je to takový můj projekt.", max_lines=20),
                ft.Text("Nad projektem s názvem : ZstŠobra chat. Pracuje já, umělá inteligencie a ještě aj i někdo již jeho jméno nechci zmiňovat. Hlavně mi nejvíc pomahá ten člověk a umělá inteligence (AI).", max_lines=20),
                ft.Text("Chat pro školu pořád pracujeme nad tím, tak aby vše fungovalo jak by mělo, neboli tak aby to bylo co nejvíc dobrý a tak abyste to nejvíc pochopili. Bohužel já a AI nejsem nejlepší na programování věcích, rozumím věcech co fungujou, mohl bych aj i něco nakodovat,", max_lines=20),
                ft.Text("ale rozhodně nejsme nejlepší v programování, rozumím Python a trošku umím. (Kdo neví co je to Python, tak Python je programovací jazyk, hlavně skoro všechno jde přes Python, aj i moje stranka, max_lines=20), umím HTML a CSS.", max_lines=20),
                ft.Text("(Kdo neví tak je to značkovací jazyk, není to programovací jazyk, ale můžeš programovat, můžeš s tím programovat stranky jednoduše než Python, ale nebude všechno fungovat, CSS je tak aby u HTML vypadala ta stranka nějak pěkně)", max_lines=20),
                ft.Text("Jak jsem přišel na to že chci udělat chat pro školu?", weight=ft.FontWeight.BOLD, size= 35, max_lines=20),
                ft.Text("Jednoho dne když jsem dělal HTML, neboli jsem dokončil projekt kde jsem zkopíroval stranku a dal jsem to do mého, tak mě napadlo proč bych jsem nemohl udělat stranku pro školu na typu chat? Tak jsem začal kodovat, Jednoho dne jsem šel na", max_lines=20),
                ft.Text("Python kvůli tomu že je to jednoduší na programování typu stranek. A ano je to, ale je to moc složitý :D. Tak jsem programoval a programoval, až jsem udělal mojí první stranku. Byl jsem na to stranšě rád to že jsem to udělal,", max_lines=20),
                ft.Text("poprvé nic nemělo ale mohl jsi psát jenom a koukat se na pravidla, kontakty, podporu a jenom to že jsi měl zadat jméno tak aby jsi se mohl připojit, takže žádný heslo a žádný databáze. A co teďka já dělám, tak jsem na to pyšní, bez programování byste tuhle stranku nemuseli mít.", max_lines=20),

            ],
            alignment=ft.MainAxisAlignment.CENTER,
            scroll=ft.ScrollMode.HIDDEN,
            spacing=7,
            expand=True
        )



if __name__ == "__main__":
    def main(page: ft.Page):
        page.theme_mode = ft.ThemeMode.DARK
        page.window_always_on_top = True
        page.add(Jsem(), scroll=ft.ScrollMode.HIDDEN)


    ft.app(main, view=ft.WEB_BROWSER)