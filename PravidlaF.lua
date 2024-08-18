import random

from flet import *
import flet as ft


# todo: change  link to docs

# the content of the blur tab
class Pravidla(ft.UserControl):

    def __init__(self, page):
        super().__init__()
        self.page = page


    def build(self):

        return ft.Column(
            [
                ft.Text("Pravidla:", weight=ft.FontWeight.BOLD, size=35, max_lines=20),
                ft.Text("Zde jsou budou vypsaná pravidla. Jestli je porušíte, můžete dočasně být zabanován. Jestli by se to opakovalo tak budete permanentně zabanován. Dopuručím to neporušovat.",
                        weight=ft.FontWeight.BOLD,
                        size=15,
                        max_lines=20,
                    ),
                ft.Text("1. Pravdivé jméno nebo přezdívka:", weight=ft.FontWeight.BOLD, max_lines=20),
                ft.Text("Jste povinni zadat své skutečné jméno nebo používat přezdívku. Anonymní účty nebudou tolerovány. Například : a, k, a atd...", max_lines=20),
                ft.Text("2. Respektujte ostatní:",weight=ft.FontWeight.BOLD, max_lines=20),
                ft.Text("Budťe vždy zdvořilí a respektujte názory a pohledy ostatních účastníků chatu.", max_lines=20),
                ft.Text("3. Bez urážek a diskriminace:", weight=ft.FontWeight.BOLD, max_lines=20),
                ft.Text("Zakázané jsou urážky, nenávistné komentáře nebo diskriminace na základě pohlaví, rasové příslušnosti, náboženství, sexuální orientace nebo jakéhokoli jiného hlediska.", max_lines=20),
                ft.Text("4. Nesdílejte osobní informace:", weight=ft.FontWeight.BOLD, max_lines=20),
                ft.Text("Neposkytujte osobní informace o sobě nebo o ostatních, abyste chránili svou a jejich soukromí.", max_lines=20),
                ft.Text("5. Bez spamu:", weight=ft.FontWeight.BOLD, max_lines=20),
                ft.Text("Nedělejte spam nebo nevyžádanou reklamu. Udržujte konverzaci smysluplnou a relevantn", max_lines=20),
                ft.Text("6. Omezte vulgarity:", weight=ft.FontWeight.BOLD, max_lines=20),
                ft.Text("Omezte používání vulgarit a sprostého jazyka. Snažte se udržovat konverzaci příjemnou.", max_lines=20),
                ft.Text("7. Žádné nelegální obsahy:", weight=ft.FontWeight.BOLD, max_lines=20),
                ft.Text("Neposkytujte nebo nešiřte sexualní videa, nelegální videa nebo jiný odkazy tak aby mohl ten daný člověk zjistit vaše osobní informace.", max_lines=20),
                ft.Text("8. Nepoužívejte tak velmi velká písmena:", weight=ft.FontWeight.BOLD, max_lines=20),
                ft.Text("Zkuste nepsát celý věty s velkými písmenama. Neboli Flood.", max_lines=20),
                ft.Text("9. Nesdílejte falešné informace:", weight=ft.FontWeight.BOLD, max_lines=20),
                ft.Text("Ověřte si faktickou správnost informací, které sdílíte, a snažte se šířit pouze ověřené a pravdivé informace." , max_lines=20),
                ft.Text("10. Bez trollingu:", weight=ft.FontWeight.BOLD, max_lines=20),
                ft.Text("Nedělejte trolling nebo úmyslné vyvolávání konfliktů.", max_lines=20),
                ft.Text("11. Udržujte konverzaci aktivní:" , weight=ft.FontWeight.BOLD, max_lines=20),
                ft.Text("Snažte se být aktivní v konverzaci a odpovídejte na otázky nebo komentáře, abyste udrželi plynulý chod chatu. ", max_lines=20),
                ft.Text("12. Zakázané jsou nesmyslné zprávy:", weight=ft.FontWeight.BOLD, max_lines=20),
                ft.Text("Neposílejte opakovaně zprávy bez smyslu nebo nesmyslný obsah, zkuste to nějak vysvětlit.", max_lines=20),
                ft.Text("13. Respektujte Majitele/Učitele:", weight=ft.FontWeight.BOLD, max_lines=20),
                ft.Text("Poslouchejte pokyny Majitele/Učitelu a respektujte jejich rozhodnutí.", max_lines=20),
                ft.Text("14. Přispívejte k pozitivní atmosféře:", weight=ft.FontWeight.BOLD, max_lines=20),
                ft.Text("Snažte se tvořit pozitivní a podpůrnou atmosféru pro všechny účastníky chatu.", max_lines=20),
                ft.Text("15. Pravidla týkající se obsahu:", weight=ft.FontWeight.BOLD, max_lines=20),
                ft.Text("Jste povinni respektovat pravidla týkající se obsahu a neposkytovat nelegální nebo nevhodný materiál.", max_lines=20),
                ft.Text("16. Zákaz se přihlasovat za jiného:", weight=ft.FontWeight.BOLD, max_lines=20),
                ft.Text("Je přísný zákaz se přihlasovat za někoho jiného bez jeho povolení.", max_lines=20),
                ft.Text("17. Zákaz dávat report někomu ze srandy", weight=ft.FontWeight.BOLD, max_lines=20),
                ft.Text("Je přísný zákat dávat někomu report jen tak, když tohle pravidlo porušíte, tak mohli byste dostat mute.", max_lines=20),
                
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
            spacing=7,
            width=self.page.width-10 
        )


if __name__ == "__main__":
    def main(page: ft.Page):
        page.theme_mode = ft.ThemeMode.DARK
        page.window_always_on_top = True
        page.add(Pravidla())

    ft.app(main, view=ft.WEB_BROWSER)