import random

from flet import *
import flet as ft


# todo: change  link to docs

# the content of the blur tab
class Otazky(ft.UserControl):

    def __init__(self):
        super().__init__()

    def build(self):

        return ft.Column(
            [
                ft.Text("Otázky ohledně na stránce.", weight=ft.FontWeight.BOLD, size=35, max_lines=20),
                ft.Text("1. Proč bych měl být na týhle stránce když mám Whatsapp, Messanger a Snapchat?", weight=ft.FontWeight.BOLD, size=25, max_lines=20),
                ft.Text("Proč bych měl být zde? Podpoříš mě že jseš na mojí strance a snažíš tak aby to bylo aktivní, ano máš Whatsapp, Messanger, Snapchat a atd... Ale asi myslím jsi, že nehceš ziskávat od každého tel. číslo tak abys jsi je mohl dát všechny na whatsapp nebo na snapchat.", max_lines=20),
                ft.Text("Tady se budeš moct bavit s kým koliv, s učitelem/učitelkama, žákama, ředitelem, zástupkyně a atd... Hlavně by byly docela aktivní updaty na mojí strance, takže například to že velikonoční updaty, nebo nějaké věci které jsme našel a byly špatné, takže je musím odstranit.", max_lines=20),
                ft.Text("Nebo budete moct hrát s někým nějaké hry, třeba quiz, šachy, poznej co to je, a atd... A tohle třeba nemáš na Snapchat. Whatsapp nebo na Messanger, to potřebuješ mít nějakou stranku! A to se horste co? Vyplatí! Nebojte se, když uděláme něco co je fakt důležitý,", max_lines=20),
                ft.Text("například ta databáze tak abysme mohli udělat to že zapamatovat vás, zobrazení zpráv, změnění profilovky a atd... tak samozřejmě to budeme muset udělat co nejdřív než nějaké hry, ale nebojte se, hry rozhodně na strance budou!", max_lines=20),
                ft.Text("2. Budou zde aj i nějaké updaty které budou specialní? Například velikonoční a atd...?", weight=ft.FontWeight.BOLD, size=25, max_lines=20),
                ft.Text("Ano, samozřejmě se budou specialní updaty! Takže ano, můžete se těšit na nějaké specialní updaty, třeba vánoční nebo hallowenský.", max_lines=20),
                ft.Text("3. Budeme moct posílat obrázky, vlastní emoji a atd...?", weight=ft.FontWeight.BOLD, size=25, max_lines=20),
                ft.Text("Ano, budete jsi moct posílat obrázky, emoji a atd... Jenom jsi budete muset chvilku počkat, až uděláme nějaké věci, které jsou důležité.", max_lines=20),
                ft.Text("4. Přes co koduji, a jaký programovací jazyk používám?", weight=ft.FontWeight.BOLD, size=25, max_lines=20),
                ft.Text("Používám : Visual code studio. A programovací jazyk používám : Python (Flet)", max_lines=20),
                ft.Text("5. Když porušíme pravidlo, tak jak nás zjistíš že jsme to opravdu my?", weight=ft.FontWeight.BOLD, size=25, max_lines=20),
                ft.Text("Když porušíte pravidlo, tak mě může kdykoliv někdo nahlásit, hlavně když mě příjdete nějaký podezřelí, tak kdykoliv můžu jít do databáze, a najít to, co jsi napsal a dát ty mute (pauza).", max_lines=20),
                
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
        page.add(Otazky(), scroll=ft.ScrollMode.HIDDEN)


    ft.app(main, view=ft.WEB_BROWSER)