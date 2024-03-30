import random

from flet import *
import flet as ft


# todo: change  link to docs

# the content of the blur tab
class Pravidla(ft.UserControl):

    def __init__(self):
        super().__init__()

    def build(self):

        return ft.Column(
            [
                ft.Text("Pravidla:", weight=ft.FontWeight.BOLD, size=35),
                ft.Text("Zde jsou budou vypsaná pravidla. Jestli je porušíte, můžete dočasně být zabanován. Jestli by se to opakovalo tak budete permanentně zabanován. Dopuručím to neporušovat.",weight=ft.FontWeight.BOLD, size=15),
                ft.Text("1. Pravdivé jméno nebo přezdívka:", weight=ft.FontWeight.BOLD), 
                ft.Text("Jste povinni zadat své skutečné jméno nebo používat přezdívku. Anonymní účty nebudou tolerovány."),
                ft.Text("2. Respektujte ostatní:",weight=ft.FontWeight.BOLD),
                ft.Text("Budťe vždy zdvořilí a respektujte názory a pohledy ostatních účastníků chatu."),
                ft.Text("3. Bez urážek a diskriminace:", weight=ft.FontWeight.BOLD), 
                ft.Text("Zakázané jsou urážky, nenávistné komentáře nebo diskriminace na základě pohlaví, rasové příslušnosti, náboženství, sexuální orientace nebo jakéhokoli jiného hlediska.", ),
                ft.Text("4. Nesdílejte osobní informace:", weight=ft.FontWeight.BOLD),
                ft.Text("Neposkytujte osobní informace o sobě nebo o ostatních, abyste chránili svou a jejich soukromí."),
                ft.Text("5. Bez spamu:", weight=ft.FontWeight.BOLD), 
                ft.Text("Nedělejte spam nebo nevyžádanou reklamu. Udržujte konverzaci smysluplnou a relevantn"),
                ft.Text("6. Omezte vulgarity:", weight=ft.FontWeight.BOLD), 
                ft.Text("Omezte používání vulgarit a sprostého jazyka. Snažte se udržovat konverzaci příjemnou."),
                ft.Text("7. Žádné nelegální obsahy:", weight=ft.FontWeight.BOLD), 
                ft.Text("Neposkytujte nebo nešiřte sexualní videa, nelegální videa nebo jiný odkazy tak aby mohl ten daný člověk zjistit vaše osobní informace.", ),
                ft.Text("8. Nepoužívejte tak velmi velká písmena:", weight=ft.FontWeight.BOLD), 
                ft.Text("Zkuste nepsát celý věty s velkými písmenama. Neboli Flood."),
                ft.Text("9. Nesdílejte falešné informace:", weight=ft.FontWeight.BOLD), 
                ft.Text("Ověřte si faktickou správnost informací, které sdílíte, a snažte se šířit pouze ověřené a pravdivé informace." ),
                ft.Text("10. Bez trollingu:", weight=ft.FontWeight.BOLD),
                ft.Text("Nedělejte trolling nebo úmyslné vyvolávání konfliktů."),
                ft.Text("11. Udržujte konverzaci aktivní:" , weight=ft.FontWeight.BOLD), 
                ft.Text("Snažte se být aktivní v konverzaci a odpovídejte na otázky nebo komentáře, abyste udrželi plynulý chod chatu. "),
                ft.Text("12. Zakázané jsou nesmyslné zprávy:", weight=ft.FontWeight.BOLD), 
                ft.Text("Neposílejte opakovaně zprávy bez smyslu nebo nesmyslný obsah, zkuste to nějak vysvětlit."),
                ft.Text("13. Respektujte Majitele/Učitele:", weight=ft.FontWeight.BOLD), 
                ft.Text("Poslouchejte pokyny Majitele/Učitelu a respektujte jejich rozhodnutí.", ),
                ft.Text("14. Přispívejte k pozitivní atmosféře:", weight=ft.FontWeight.BOLD), 
                ft.Text("Snažte se tvořit pozitivní a podpůrnou atmosféru pro všechny účastníky chatu."),
                ft.Text("15. Pravidla týkající se obsahu:", weight=ft.FontWeight.BOLD),
                ft.Text("Jste povinni respektovat pravidla týkající se obsahu a neposkytovat nelegální nebo nevhodný materiál.", ),
                ft.Text("16. Zákaz se přihlasovat za jiného:", weight=ft.FontWeight.BOLD),
                ft.Text("Je přísný zákaz se přihlasovat za někoho jiného bez jeho povolení."),
                ft.Text("17. Zákaz dávat report někomu ze srandy", weight=ft.FontWeight.BOLD),
                ft.Text("Je přísný zákat dávat někomu report jen tak, když tohle pravidlo porušíte, tak mohli byste dostat mute.")
                
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
        page.add(Pravidla())


    ft.app(main, view=ft.WEB_BROWSER)