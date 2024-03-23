import random
import tkinter as tk
from flet import *
import flet as ft

class Jsem(ft.UserControl):
    def __init__(self):
        super().__init__()

    def build(self):
        return ft.Column(
            [
                ft.Text("Kdo jsem?", weight=ft.FontWeight.BOLD, size=35),
                ft.Text("Ahoj. Jmenuji se Vojtěch Kurinec. Jsem v 6 třídě a je mi 13 let (V tomhle roce 14). Moje koníčky jsou: Programování, Šachy, Tančení.", weight=ft.FontWeight.BOLD, size=15),
                ft.Text("Chat pro školu jsem chtěl udělat kvůli tomu, aby jste mezi třídami mohli bavit ohledně něčeho, například o tom jak se vypočítává tohle a atd... Je to takový můj projekt."),
                ft.Text("Nad projektem s názvem: ZstŠobra chat. Pracuje já, umělá inteligencie a ještě aj i někdo již jeho jméno nechci zmiňovat. Hlavně mi nejvíc pomáhá ten člověk a umělá inteligence (AI)."),
                ft.Text("Chat pro školu pořád pracujeme nad tím, aby vše fungovalo jak by mělo, neboli tak aby to bylo co nejvíc dobré a tak abyste to nejvíc pochopili. Bohužel já a AI nejsme nejlepší v programování věcí, rozumíme věcem co fungujou, mohl bych aj i něco nakodovat, ale rozhodně nejsme nejlepší v programování, rozumím Python a trošku umím. (Kdo neví co je to Python, tak Python je programovací jazyk, hlavně skoro všechno jde přes Python, aj i moje stránka), umím HTML a CSS."),
                ft.Text("(Kdo neví tak je to značkovací jazyk, není to programovací jazyk, ale můžeš programovat, můžeš s tím programovat stránky jednoduše než Python, ale nebude všechno fungovat, CSS je tak aby u HTML vypadala ta stránka nějak pěkně)"),
                ft.Text("Jak jsem přišel na to, že chci udělat chat pro školu?", weight=ft.FontWeight.BOLD, size= 35),
                ft.Text("Jednoho dne když jsem dělal HTML, neboli jsem dokončil projekt kde jsem zkopíroval stránku a dal jsem to do mého, tak mě napadlo proč bych jsem nemohl udělat stránku pro školu na typu chat? Tak jsem začal kódovat, Jednoho dne jsem šel na Python kvůli tomu že je to jednoduší na programování typu stránek. A ano je to, ale je to moc složitý :D. Tak jsem programoval a programoval, až jsem udělal mojí první stránku. Byl jsem na to stránšě rád to že jsem to udělal, poprvé nic nemělo ale mohl jsi psát jenom a koukat se na pravidla, kontakty, podporu a jenom to že jsi měl zadat jméno tak aby jsi se mohl připojit, takže žádný heslo a žádný databáze. A co teďka já dělám, tak jsem na to pyšní, bez programování byste tuhle stránku nemuseli mít."),

            ],
            alignment=ft.MainAxisAlignment.CENTER,
            scroll=ft.ScrollMode.HIDDEN,
            spacing=7,
            expand=True
        )

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("600x400")

    page = ft.Page(root, theme_mode=ft.ThemeMode.DARK, window_always_on_top=True)
    page.pack(expand=True, fill="both")

    canvas = page.canvas

    jsem = Jsem()
    jsem.pack()

    scrollbar = tk.Scrollbar(root, orient="horizontal", command=canvas.xview)
    scrollbar.pack(side="bottom", fill="x")

    canvas.configure(xscrollcommand=scrollbar.set)

    root.mainloop()
