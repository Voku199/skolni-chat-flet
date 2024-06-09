    def show_pravidla(self, e):
        # Otevřít dialogové okno s pravidly
        if (
            not self.user_name.value
            or not self.email.value
            or not self.password.value
            or not self.password_confirm.value
            or not self.trida.value
        ):
            self.error_message.value = "Nejdříve vyplňte všechna povinná pole."
            self.error_message.update()
            return

        pravidla_text = """Pravidla:
        1. Pravdivé jméno nebo přezdívka:
            - Jste povinní zadat své skutečné jméno nebo použít přezdívku. Anonymní účty nebudou tolerovány. Například: a, k, ;, a atd...
        2. Respektujte ostatní:
            - Budťe vždy zdvořilí a respektujte názory a pohledy ostatních lidí v chatu
        3. Bez uřážek a diskriminace:
            - Zakázané jsou urážky, nenávistné komentáře nebo diskriminace na základě pohlaví, rasové příslušnosti, náboženství, sexuální orientace nebo jakéhokoli jiného hlediska.
        4. Nesdílejte osobní informace:
            - Neposkytujte osobní informace o sobě nebo o ostatních, abyste chránili svou a jejich soukromí.
        5. Bez spamu
            - Nedělejte spam nebo nevyžádanou reklamu. Udržujte konverzaci smysluplnou a relevantn
        6. Omezte vulgarity:
            - Omezte používání vulgarit a sprostého jazyka. Snažte se udržovat konverzaci příjemnou. (Platí aj i v jiných jazycích!)
        7. Žádné nelegální obsah:
            - Neposkytujte nebo nešiřte sexualní videa, nelegální videa nebo jiný odkazy které jsou nelegální pro malé děti. (Žádný stranky pro dospělé, podpora drog a atd...)
        8. Nesdílejte falešné informace:
            - Ověřte si faktickou správnost informací, které sdílíte, a snažte se šířit pouze ověřené a pravdivé informace.
        9. Bez trolling:
            - Nedělejte trolling nebo úmyslné vyvolávání konfliktů.
        10. Udržujte konverzaci aktivný (Tohle pravidlo není povinný!):
            - Snažte se být aktivní v konverzaci a odpovídejte na otázky nebo komentáře, abyste udrželi plynulý chod chatu.
        11. Zakázané jsou nesmyslné zprávy:
            - Neposílejte opakovaně zprávy bez smyslu nebo nesmyslný obsah, zkuste to nějak vysvětlit.
        12. Respektujte Majitele/Učitelu/Admin/Spolu Majitel
            - Poslouchejte pokyny Majitele/Učitelu/Admin/Spolu Majitel a respektujte jejich rozhodnutí.
        13. Přispívejte k pozitivní atmosféře:
            - Snažte se tvořit pozitivní a podpůrnou atmosféru pro všechny účastníky chatu.
        14. Zákat se přihlasovat za jiného:
            - Je přísný zákaz se přihlasovat za někoho jiného bez jeho povolení.
        15. Zákaz dávat report někomu ze srandy
            - Je přísný zákat dávat někomu report jen tak, bez žádnýho důvodu
        """
        pravidla_content = ft.Column(
            [
                ft.Text(pravidla_text),
                ft.Text("Souhlasíte s pravidly?"),
                self.souhlas_pravidla,
                self.submit,  # Zahrneme tlačítko registrovat i sem, aby uživatel mohl pokračovat ve formuláři po přečtení pravidel
            ]
        )

        self.page.dialog = ft.AlertDialog(
            open=True,
            modal=True,
            title=ft.Text("Pravidla chatu"),
            content=ft.Container(
                pravidla_content,
                scroll=True,
                alignment=ft.MainAxisAlignment.CENTER,
                width=self.page.width - 10,
            ),
        )
        self.page.update()
