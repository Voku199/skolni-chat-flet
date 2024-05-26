import flet as ft
from flet import Text, ControlEvent, TextField, Dropdown, ElevatedButton, Row, Checkbox
from datetime import datetime, timedelta
import os
import re
import webbrowser
import base64
from Novinky import Novinky
from Pravidla import Pravidla
from Podpora import Podpora
from Nastaveni import Nastavení
from Jsem import Jsem
from Otazky import Otazky
from Nahlaseni import Nahlaseni

import mysql.connector
import bcrypt

# Seznam přihlášených uživatelů
online_users = set()
online_users = {}
current_page = None
error_dialog_shown = False
user_achievements = {}

# Definice achievementů
achievements = [
    {"name": "První chat", "description": "Dokončil jste svůj první chat.", "condition": 1},
    {"name": "Deset chatů", "description": "Dokončil jste 10 chatů.", "condition": 10},
    {"name": "Sto chatů", "description": "Dokončil jste 100 chatů.", "condition": 100},
    {"name": "Aktivní účastník", "description": "Pravidelně se účastníte chatů po dobu jednoho týdne.", "condition": 7},  # Example condition
    # Další achievementy mohou být přidány sem
]


mydb = mysql.connector.connect(
    host=os.environ["DB_HOST"],
    port=os.environ["DB_PORT"],
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASS"],
    database=os.environ["DB_NAME"],
    connection_timeout=30
)
cursor = mydb.cursor()



class Registrace():
    def __init__(self, Page: ft.Page):

        tridy = []
        for i in range(9):
            tridy.append(ft.dropdown.Option(f"{i + 1}.A"))
            tridy.append(ft.dropdown.Option(f"{i + 1}.B"))

        self.user_name = TextField(label="Zadej uživatélské jméno:")
        self.email = TextField(label="Zadej email.")
        self.trida = Dropdown(label="Třída", options=tridy)
        self.password = TextField(label="Zadej heslo.", password=True)
        self.password_confirm = TextField(label="Potvrď heslo.", password=True)
        self.souhlas_pravidla = Checkbox(label="Souhlasíš s pravidly který jsou na školní chat?")
        self.show_pravidla_button = ElevatedButton(text="Zobrazit pravidla", on_click=self.show_pravidla)
        self.submit = ElevatedButton(text="Registrovat", on_click=lambda e: self.submit_click(Page, e))
        self.error_message = Text("Jestli se ty nejde zaregistrovat, tak zkus jiný jméno, třeba přidat za svým jménem tečku, čárku, nebo něco jiného. Někdo už bohužel má tohle jméno zabraný.", size=12)
        self.page = Page
        

    def submit_click(self, page, e):
        if not self.user_name.value or not self.email.value or not self.password.value or not self.password_confirm.value or not self.trida.value:
            self.error_message.value = "Všechny pole musí být vyplněny."
            self.error_message.update()
            return
        if self.password.value != self.password_confirm.value:
            self.error_message.value = "Hesla se neshodují."
            self.error_message.update()
            return
        if not self.souhlas_pravidla.value:
            self.error_message.value = "Musíš souhlasit s pravidly."
            self.error_message.update()
            return
        if not self.trida.value:
            self.error_message.value = "Musíš zadat třídu!"
            self.error_message.update()
            return
        hashed_password, salt = hash_password(self.password.value)
        cursor.execute("INSERT INTO user (user_name, email, class, password, salt) VALUES (%s, %s, %s, %s, %s)", (self.user_name.value, self.email.value, self.trida.value, hashed_password.decode("utf-8"), salt.decode("utf-8")))
        mydb.commit()

        login = _login(self.user_name, self.password)

        if login["success"]:
            page = self.page
            user = login["user"]["user_name"]
            role = login["user"]["role"]
            page.session.set("user_name", login["user"]["user_name"])
            page.session.set("user_id", login["user"]["id"])
            page.session.set("user_class", login["user"]["class"])
            page.session.set("user_role", login["user"]["role"])
            page.session.set("profile_picture", login["user"]["profile_picture"])
            page.dialog.open = False
            welcome = f"{user} Vítej mezi námi! Snad se ty to bude líbit. Můžeš napsat !Help nebo !help a zjistíš co je co!."
            if role:
                welcome = f"{user} {role} Vítej mezi námi! Snad se ty to bude líbit. Když tak, jsi {role}. Nevím jak jsi to získal, ale dobrá práce. Obešel jsi system"

            page.pubsub.send_all(Message(user_name=user, user_role=role, text=welcome, message_type="login_message", page=page)),
            cursor.execute("SELECT message, user_name, class, role, profile_picture FROM chat join user on user.id = chat.user_id order by chat.id desc limit 10")
            page.update()

        self.error_message.value = "Registrace proběhla úspěšně."
        self.error_message.update()

    def show_pravidla(self, e):
        # Otevřít dialogové okno s pravidly
        if not self.user_name.value or not self.email.value or not self.password.value or not self.password_confirm.value or not self.trida.value:
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
        self.page.dialog = ft.AlertDialog(
            open=True,
            modal=True,
            title=ft.Text("Pravidla chatu"),
            content=ft.Column([
                ft.Text(pravidla_text),
                ft.Text("Souhlasíte s pravidly?"), self.souhlas_pravidla, self.submit,  # Zahrneme tlačítko registrovat i sem, aby uživatel mohl pokračovat ve formuláři po přečtení pravidel
            ] ),
        )
        self.page.update()

    def createForm(self):
        return ft.Column([self.user_name,
                          self.email,
                          self.trida,
                          self.password,
                          self.password_confirm,
                          self.show_pravidla_button,
                          self.submit,
                          self.error_message], width=300, tight=True)


class Page:
    def __init__(self):
        self.help_shown = False

class Message():
    def __init__(self, user_name: str, text: str, message_type: str, user_role: str | None, page):
        self.user_name = user_name
        self.text = text
        self.message_type = message_type
        self.user_role = user_role
        self.page = page


class ChatMessage(ft.Row, str):
    def __init__(self, message: Message,):
        super().__init__()
        self.vertical_alignment = "start"
        user_info = message.user_name
        #self.message = message
        #self.replaced_text = replaced_text
    
        m = []

        if message.user_name:
            m = [
                ft.Text(message.user_name, weight="bold", color=ft.colors.WHITE),
                ft.Text(message.text, selectable=True, width=message.page.width - 100),
                #self.parse_message_content(message.text),
            ]
        
        if message.user_role != None:
            user_info += f" [{message.user_role}]"
            m = [
                ft.Text(user_info, weight="bold", color=ft.colors.YELLOW),
                ft.Text(message.text, selectable=True, width=message.page.width - 100),
                #self.parse_message_content(message.text),    
            ]

        self.controls = [
            ft.CircleAvatar(
                content=ft.Text(self.get_initials(message.user_name, )),
                color=ft.colors.WHITE,
                bgcolor=self.get_avatar_color(message.user_name, ),
            ),
            ft.Column(
                m,
                tight=True,
                spacing=5,
            ),
        ]
    #def parse_message_content(self, text: str):
   
        #url_pattern = re.compile(r'https?://\S+')
        #url_matches = url_pattern.findall(text)

    # Seznam pro uchování tlačítek
        #link_buttons = []

        #for url in url_matches:
            #link_button_text = f"Jít na stránku: {url}"

            #link_button = ft.ElevatedButton(
             #   content=ft.Text(link_button_text),
              #  on_click=lambda e, url=url: self.open_external_link(url),
            #)
            #link_buttons.append(link_button)

            #text = text.replace(url, link_button_text)

        #output_text = ft.Text(text, selectable=True, width=1000)

        #return output_text, link_buttons

    #def open_external_link(self, url: str):
        #
     #   webbrowser.open_new(url)

    def get_initials(self, user_name: str):
        if user_name:
            return user_name[:1].capitalize()
        print("Maskot")
        ft.Text("Maskot")
        return "Zib"

    def get_avatar_color(self, user_name: str):
        colors_lookup = [
            ft.colors.AMBER,
            ft.colors.BLUE,
            ft.colors.BROWN,
            ft.colors.CYAN,
            ft.colors.GREEN,
            ft.colors.INDIGO,
            ft.colors.LIME,
            ft.colors.ORANGE,
            ft.colors.PINK,
            ft.colors.PURPLE,
            ft.colors.RED,
            ft.colors.TEAL,
            ft.colors.INDIGO,
            ft.colors.TEAL,
            ft.colors.LIGHT_GREEN_ACCENT,
        ] 
        return colors_lookup[hash(user_name) % len(colors_lookup)]

def hash_password(password, salt=None):
    # Hash a password using bcrypt
    if salt is None:
        salt = bcrypt.gensalt()
    else:
        salt = salt.encode('utf-8')

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password, salt


def _logout(page: ft.Page, chat):
    page.session.clear()
    chat.controls.clear()
    page.dialog.open = True
    page.update()


# Use a dictionary to store usernames and session IDs
def _login(username: TextField, password: TextField) -> dict:
    response = {"success": False}

    cursor.execute("SELECT * FROM user WHERE user_name = %s OR email = %s LIMIT 1", (username.value, username.value))
    result = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    data = [dict(zip(columns, row)) for row in result]

    if data and data[0]:
        hashed_password, _ = hash_password(password.value, data[0]['salt'])
        if data[0]['password'] == hashed_password.decode("utf-8"):
            response["success"] = True
            response["user"] = data[0]

            # Přidání uživatele do seznamu přihlášených uživatelů
            online_users.update({data[0]['user_name']: None})  # Change this line

        else:
            response["message"] = "Špatně jsi zadal heslo"
    else:
        response["message"] = "Špatně jsi zadal jméno"

    return response


def main(page: ft.Page):
    global current_page
    current_page = page

    new_message = ft.TextField(
        hint_text="Napiš zprávu...",
        autofocus=True,
        shift_enter=True,
        min_lines=1,
        max_lines=5,
        filled=True,
        expand=True,
        on_submit=lambda e: send_message_click(e),
    )
    

    page.horizontal_alignment = "stretch"
    page.title = "Chat ZŠ Tomáše Šobra"
    page.theme_mode = ft.ThemeMode.DARK


    pravidla = Pravidla(page)
    novinky = Novinky(page)
    podpora = Podpora(page)
    nastavení = Nastavení(page)
    jsem = Jsem(page)
    otazky = Otazky(page)
    nahlaseni = Nahlaseni(page)

    page_map = [
        pravidla,
        novinky,
        podpora,
        nastavení,
        jsem,
        otazky,
        nahlaseni,
    ]

    def join_chat_click(e):
        user_id = page.session.get("user_id")
        
        if page is not None:
            if isinstance(text_username, ft.TextField) and isinstance(text_password, ft.TextField):
                page.update()

        if user_id:
        # Zkontrolujte stav umlčení a aktualizujte UI
            update_ui_for_mute_status(user_id)        

        if not text_username.value or not text_password.value:
            error_message = "Zadej uživatélské jméno ."
            text_password.error_text = "Zadej heslo."
            text_username.error_text = error_message
            text_password.error_text = text_password.error_text
            text_username.update()
            text_password.update()
            page.dialog.update()
            page.dialog.actions.append(
                ft.ElevatedButton(text="Zapomenutý údaje?", on_click=clear_error_and_retry)
            )
            #page.dialog.update()

            return

        login = _login(text_username, text_password)
        # Clear the password field
        text_password.value = ""
        text_password.update()
        result = None  # Initialize result variable

        if not login["success"]:
            error_message = login.get("message", "An unknown error occurred.")
            text_username.error_text = error_message
            text_username.update()

            # Přidáme tlačítko pro znovu přihlášení
            page.dialog.actions.append(
                ft.ElevatedButton(text="Zapomenutý údaje?", on_click=clear_error_and_retry),
                error_dialog_shown = True,
            )
            # page.dialog.update()

        else:
            text_username.value = ""
            text_username.update()
            user = login["user"]["user_name"]
            profile_picture_url = login["user"]["profile_picture"] 
            page.session.set("user", login["user"])
            page.session.set("user_name", login["user"]["user_name"])
            page.session.set("user_id", login["user"]["id"])
            page.session.set("user_class", login["user"]["class"])
            page.session.set("user_email", login["user"]["email"])
            page.session.set("user_role", login["user"]["role"])
            page.session.set("profile_picture", login["user"]["profile_picture"])
            page.dialog.open = False
            new_message.prefix = ft.Text(f"{user} : ")
            
        if profile_picture_url or not profile_picture_url:
            profile_picture = ft.Image(src=profile_picture_url, width=50, height=50)
            new_message.prefix.content = [profile_picture, ft.Text(f"{user}: ")]
            print(profile_picture_url)

            page.pubsub.send_all(Message(user_name=user, text=f"{user} se připojil do chatu. Připoj se k pobavení!", message_type="login_message", user_role=None, page=page))

            cursor.execute("SELECT message, user_name, class, role, profile_picture FROM chat join user on user.id = chat.user_id order by chat.id desc limit 10")
            result = cursor.fetchall()
            columns = [column[0] for column in cursor.description]

        if result:
            for row in result:
                data = dict(zip(columns, row))
                user_name = data["user_name"]
                user_class = data.get("class", "")
                user_role = data.get("role", "")
                message = Message(user_name=f"{user_name} {user_class}", text=data["message"], message_type="chat_message", user_role=user_role, page=page)
                chat_message = ChatMessage(message)  # Add the page argument
                chat.controls.append(chat_message)

            # page.update()
        join_chat_click(e)

    def clear_error_and_retry(form):
        global error_dialog_shown
        if not error_dialog_shown:  # Pokud dialogové okno ještě nebylo zobrazeno
            error_dialog = ft.AlertDialog(
                open=True,
                modal=True,
                title=ft.Text("Zapomenutý heslo/uživ. jméno"),
                content=ft.Column([
                    ft.Text("Zapoměl jsi si heslo nebo uživatelské jméno?"),
                    ft.Text("Kontaktuj mě : vojta.kurinec@gmail.com"),
                    ft.Text("Budu se snažit tak aby to bylo dostatečně rychlý!"),
                    ElevatedButton(text="Zpět k chatu", on_click=lambda e: zpatky(page, chat))
                ], width=200, height=200, tight=True),
            )
            page.dialog = error_dialog
            page.update()
            error_dialog_shown = True 


    def create_account(e):
        # Přesměrování na stránku pro registraci
        registrace = Registrace(page)
        form = Registrace(page).createForm()
        page.dialog = ft.AlertDialog(
            open=True,
            modal=True,
            title=ft.Text("Registrace!"),
            content=ft.Column([form], width=300, height=400, tight=True),
        )

        page.update()

    def zpatky(page, chat):
        webbrowser.open_new_tab("voku-skolni-chat.fly.dev")
   
    def update_ui_for_mute_status(user_id):
    # Zkontrolujte, zda je uživatel umlčen
        if is_muted(user_id):
        # Zakažte textové pole a skryjte tlačítko
            new_message.disabled = True
            new_message.visible = False
        else:
        # Povolit textové pole a zobrazit tlačítko
            new_message.disabled = False
            new_message.visible = True

        new_message.update()  # Aktualizujte uživatelské rozhraní
        new_message.update()

    def show_messages(message, page):
     # Rozdělení textu na části, aby se zkontrolovalo, zda je uveden uživatel
        parts = message.text.split(" ", 1)  # Rozdělení na příkaz a případný zbytek
    
        if len(parts) == 1:  
            cursor.execute("SELECT message, user_id FROM chat ORDER BY id DESC LIMIT 100")
            result = cursor.fetchall()
        
            all_messages_text = "Posledních 100 zpráv:\n"
            for row in result:
                all_messages_text += f"Uživatel ID {row[1]}: {row[0]}\n"

            chat.controls.append(
                ChatMessage(
                    Message(
                        user_name="Zib",
                        text=all_messages_text,
                        message_type="chat_message",
                        user_role="Bot",
                        page=page,
                    )
                )
            )
    
        elif len(parts) == 2:  # Pokud je zadán identifikátor (uživatelské jméno nebo ID)
            user_identifier = parts[1].strip()  # Získat jméno nebo ID

            if user_identifier.isdigit():
                # Dotaz na zprávy podle uživatelského ID
                cursor.execute("SELECT message FROM chat WHERE user_id = %s ORDER BY id", (int(user_identifier),))
            else:
                # Dotaz na zprávy podle uživatelského jména
                cursor.execute("SELECT message FROM chat WHERE user_id = (SELECT id FROM user WHERE user_name = %s) ORDER BY id", (user_identifier,))

            result = cursor.fetchall()

            if not result:
                user_messages = f"Nenašli jsme žádné zprávy od uživatele s identifikátorem '{user_identifier}'."
            else:
                user_messages = f"Zprávy od uživatele s ID nebo Uživatelským jménem '{user_identifier}':\n"
                for row in result:
                    user_messages += f"- {row[0]}\n"

            chat.controls.append(
                ChatMessage(
                    Message(
                        user_name="Zib",
                        text=user_messages,
                        message_type="chat_message",
                        user_role="Bot",
                        page=page,
                    )
                )
            )
        page.update()



    def show_all_users(message, page):
    # Přečtěte uživatele z databáze
        cursor.execute("SELECT user_name, class, role, id FROM user ORDER BY id DESC LIMIT 1000 ")
        result = cursor.fetchall()
    # Zformátujte seznam uživatelů
        users_text = "Všechny uživatele:\n"
        for row in result:
            users_text += f"{row[0]} (Třída: {row[1]}, Role: {row[2]}, Id : {row[3]} )\n"
    # Vložte je do chatu
        chat.controls.append(
            ChatMessage(
                Message(
                    user_name="Zib",
                    text=users_text,
                    message_type="chat_message",
                    user_role="Bot",
                    page=page,
                )
            )
        )
        page.update()



    def show_user_details(message, page):
        parts = message.text.split(" ")
        if len(parts) < 2:
        # Pokud je formát špatný, zobrazte zprávu o chybě
            chat.controls.append(
                ChatMessage(
                    Message(
                        user_name="Zib",
                        text="Musíte zadat jméno uživatele nebo ID! Např. '!users Vojta' nebo '!users 123'.",
                        message_type="chat_message",
                        user_role="Bot",
                        page=page,
                    )
                )
            )
            page.update()
            return
    
        user_identifier = parts[1].strip()  
        if user_identifier.isdigit():
            cursor.execute("SELECT user_name, class, role, id, email FROM user WHERE id = %s LIMIT 1", (user_identifier,))
        else:
            cursor.execute("SELECT user_name, class, role, id, email FROM user WHERE user_name = %s LIMIT 1", (user_identifier,))

        result = cursor.fetchone()

        if result:
            user_text = f"Uživatel: {result[0]}\nTřída: {result[1]}\nRole: {result[2]}\nID: {result[3]}\nEmail: {result[4]}\n"
        else:
            user_text = f"Uživatel '{user_identifier}' nebyl nalezen."

        chat.controls.append(
            ChatMessage(
                Message(
                    user_name="Zib",
                    text=user_text,
                    message_type="chat_message",
                    user_role="Bot",
                    page=page,
                )
            )
        )
        page.update()
        command_list["!message"] = show_messages
    
    def handle_calculator(message: Message, page: ft.Page,):
        calculator_text = "Tohle je kalkulačka. Zatím není podporované více příkladu např : 5+5 a víc už ne .Podporované operátory jsou: +, -, *, /, %.\n"

    #Přidat pak tak aby mohl člověk psát více toho než jenom : 5+5. Např : 5+5+5+5+5+5.

        try:
            parts = re.split(r'(\d+\s*[+-/*%]\s*\d+)', message.text)
            if len(parts) > 1:
                expression = parts[1].strip()
                result = eval(expression)
                calculator_text += f"Příklad který jsi dal je : *{expression}*\n"
                
                calculator_text += f"Výsledek výpočtu: **{result}**\n"
                
            else:
                calculator_text = "Neplatný vstup. Zadej výraz ve formátu [Příklad] [Operátor] [Příklad].\n"
        except Exception as e:
            calculator_text = f"Chyba při výpočtu: {e}\n"

        message = Message(
            user_name="Zib",
            text=calculator_text,
            message_type="chat_message",
            user_role="Bot",
            page=page,
        )
        chat_message = ChatMessage(message)
        chat.controls.append(chat_message)
    
    
    def handle_help(message: Message, page: ft.Page,):
        help_text = "Ahoj, já jsem Zib! Jsem robot a dělám to abych jsem ti pomohl. Dostupné příkazy jsou:\n"
        help_text += "- !Help : Zobrazí tuhle zprávu \n"
        help_text += "- !cl [Příklad] [Příklad] : cl je kalkulačka. \n"
        help_text += "- !s [Cokoliv] : !s stojí za 'Search', neboli vyhledávat, umožní vám to vyhledat cokoliv aniž byste otevřeli nějakou kartu"
        
        help_text += "- !m [Cokoliv] : Tenhle příkaz funguje tak že vyhledáš všechny zprávy ohledně tý zprávy"
        help_text += "- Majitel je Vojtěch Kurinec. Jeho nick je Vojta 6.B [Majitel].\n"
        help_text += "- Když tak, když klikneš na ty 3 čáry nahoře, tak to je menu, a uvidíš co je tam! .\n"
        help_text += "- Roli získáš nějak, role jsou zde důležitý, tak aby se zde nezfalšovalo kdo je co. Role jsou zatím jenom : Majitel, Admin, Žák/Žákyně (Tu roli žádnou nemá), Učitel. Samozřejmě že se budou přidávat.\n"
        help_text += "- Dodržuj pravidla, tak abys jsi nedostal ban, mute, nebo varování! Jestli máš nějaké otázky, ptej se Majitele.\n"
    
        if message.user_role in full_permissions:
            help_text += "\n"
            help_text += "\n"
            help_text += "- Další pokročilé příkazy, které jsou dostupné pouze pro Majitele, Adminy a Učitelé a Ředitele.\n"
            help_text += "-!users [ID (Číslo)/Name (Jméno)] : Zobrazí všechny uživatele. [ID/Name] není povinný, ale když to dáte, všechny jeho věci co známe se zobrazí\n"
            help_text += "-!message [ID (ČÍslo)/Name (Jméno)] : Zobrazí všechny zprávy od uživatele. [ID/Name] není povinný, ale když to dáte, všechny jeho zprávy co známe se zobrazí\n"
            help_text += "-!m [Jakýkoliv slovo] : Vyhledá to slovo který ten danný uživatel napsal např : !me Ahoj. Vyhledá to všechny zprávy ohledně Ahoj. "
            help_text += "-!mute [ID (Číslo)] [Doba] [Důvod] : Umlčí uživatele. [ID] a [Doba] je důležitá! Doba jsou na minuty a Uživatel je přes ID a Důvod není povinný, ale bylo by to dobrý, Vypíše se to do databáze\n"
            help_text += "-!warn [Name (Jméno)] : Varovaní pro toho uživatele. Vypíše se to do databáze"
        
        message = Message(
            user_name="Zib",
            text=help_text,
            message_type="chat_message",
            user_role="Bot",
            page=page,

        )
        chat_message = ChatMessage(message)
        chat.controls.append(chat_message)
        

    def is_muted(user_id):
        try:
            cursor.execute("SELECT mute_end FROM muted_users WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
        
        # Ujistěte se, že jste dokončili čtení všech výsledků
            cursor.fetchall()  # Nebo cursor.reset()

            if result:
                mute_end_time = result[0]
                if datetime.now() < mute_end_time:
                    return True
                else:
                    cursor.execute("DELETE FROM muted_users WHERE user_id = %s", (user_id,))
                    mydb.commit()
        
            return False
        except mysql.connector.Error as err:
            print("Error during checking mute status:", err)
            return False
    

    # Funkce pro umlčení uživatele
    def mute_user(user_id, duration_minutes, reason=""):
        try:
            mute_end_time = datetime.now() + timedelta(minutes=duration_minutes)
            print(f"{user_id} {mute_end_time}")
            cursor.execute("INSERT INTO muted_users (user_id, mute_end) VALUES (%s, %s)", (user_id, mute_end_time))
            # mydb.commit()
            print(f"Uživatel {user_id} byl umlčen na {duration_minutes} minut.")

        except mysql.connector.Error as err:
            print("Chyba při umlčení uživatele:", err)

    # Funkce pro zpracování příkazu !Mute
    def handle_mute_command(message, page, ):
        parts = message.text.split(" ")

        if len(parts) >= 3:  # Přidána podmínka pro kontrolu dostatečné délky vstupu
            try:
                user_id = int(parts[1].strip())
                duration_minutes = int(parts[2].strip())  # Přidána délka umlčení
                reason = " ".join(parts[3:]) if len(parts) > 3 else ""  # Získání důvodu umlčení
                print(f"Muting user {user_id} for {duration_minutes} minutes with reason: {reason}")
                mute_user(user_id, duration_minutes, reason)

            # Notify the Chat
                current_page.pubsub.send_all(
                    Message(
                        user_name="Zib",
                        user_role="Bot",
                        text=f"Uživatel s ID : {user_id} byl umlčen na {duration_minutes} minut. Důvod: {reason}",
                        message_type="system",
                        page=current_page,
                    )
                )
            except ValueError:
                message(
                    Message(
                        user_name="Zib",
                        user_role="Bot",
                        text="Neplatné ID uživatele nebo délka umlčení. Použijte správný formát !Mute <User_ID> <Duration_in_minutes> [<Reason>].",
                        message_type="system",
                        page=current_page,
                    )
                )
        else:
            message(
                Message(
                    user_name="Zib",
                    user_role="Bot",
                    text="Neplatný příkaz! Použijte formát !Mute <User_ID> <Duration_in_minutes> [<Reason>].",
                    message_type="system",
                    page=current_page,
                )
            )
    
    def handle_warn_command(message, page):
        parts = message.text.split(" ", 1)
    
    # Kontrola, zda byl zadán uživatel
        if len(parts) < 2:
            chat.controls.append(
                ChatMessage(
                    Message(
                        user_name="Zib",
                        text="Musíte zadat jméno uživatele! Např. '!warn Vojta'.",
                        message_type="chat_message",
                        user_role="Bot",
                        page=page,
                    )
                )
            )
            page.update()
            return

        user_name = parts[1].strip()  # Získat jméno uživatele

    # Vyhledat uživatele podle jména
        cursor.execute("SELECT id, user_name FROM user WHERE user_name = %s LIMIT 1", (user_name,))
        user_data = cursor.fetchone()

    # Zkontrolovat, zda byl uživatel nalezen
        if not user_data:
            chat.controls.append(
                ChatMessage(
                    Message(
                        user_name="Zib",
                        text=f"Uživatel '{user_name}' nebyl nalezen.",
                        message_type="chat_message",
                        user_role="Bot",
                        page=page,
                    )
                )
            )
            page.update()
            return

    # Pokud byl uživatel nalezen, přidejte varování
        user_id = user_data[0]
        cursor.execute("INSERT INTO warnings (user_id, warning_date, warned_by) VALUES (%s, NOW(), %s)", (user_id, page.session.get("user_id")))
        mydb.commit()

        chat.controls.append(
            current_page.pubsub.send_all(
                Message(
                    user_name="Zib",
                    text=f"Uživatel '{user_name}' byl varován.",
                    message_type="chat_message",
                    user_role="Bot",
                    page=page,
                )
            )
        )
        page.update()

    def search_command(msg, page):
        if len(msg.text.split()) < 2:
        # Pokud uživatel neposkytl žádné hledané výrazy
            message(
                Message(
                    user_name="Bot",
                    user_role="Bot",
                    text="Nebyly zadány žádné hledané výrazy.",
                    message_type="chat_message",
                    page=page,
                )
            )
            return
    
    # Získání hledaného výrazu ze zprávy
        search_query = ' '.join(msg.text.split()[1:])
    
    # Vytvoření URL pro vyhledávání na webu
        search_url = f"https://www.google.com/search?q={search_query}"
    
        try:
            webbrowser.open_new_tab(search_url)
            message = Message(
                user_name="Zib",
                text=f"Vyhledávání pro '*{search_query}*' bylo uspěšné! Zde je váš odkaz: '{search_url}'",
                message_type="chat_message",
                user_role="Bot",
                page=page,
            )
            chat_message = ChatMessage(message)
            chat.controls.append(chat_message)
        
        except Exception as e:
        # Informovat uživatele o chybě
            message = Message(
                user_name="Zib",
                text=f"Při vyhledávání pro '{search_query}' došlo k chybě: {str(e)}",
                message_type="chat_message",
                user_role="Bot",
                page=page,
            )
            chat_message = ChatMessage(message)
            chat.controls.append(chat_message)


    def search_messages(message, page):
    # Rozdělení textu na části, aby se získal hledaný výraz
        parts = message.text.split(" ", 1)  # Rozdělení na příkaz a hledaný výraz

        if len(parts) == 1:  
            chat.controls.append(
                ChatMessage(
                    Message(
                        user_name="Zib",
                        text="Nebyl zadán žádný hledaný výraz.",
                        message_type="chat_message",
                        user_role="Bot",
                        page=page,
                    )
                )
            )
            page.update()
            return
    
        search_query = parts[1].strip()  # Získání hledaného výrazu

    # Dotaz na zprávy obsahující hledaný výraz
        cursor.execute("SELECT message, user_id FROM chat WHERE message LIKE %s ORDER BY id DESC LIMIT 100", ('%' + search_query + '%',))
        result = cursor.fetchall()

        if not result:
            chat.controls.append(
                ChatMessage(
                    Message(
                        user_name="Zib",
                        text=f"Nebyly nalezeny žádné zprávy obsahující výraz '{search_query}'.",
                        message_type="chat_message",
                        user_role="Bot",
                        page=page,
                    )
                )
            )
            page.update()
            return

    # Vytvoření zprávy s nalezenými zprávami
        search_results_text = f"Výsledky vyhledávání pro výraz '{search_query}':\n"
        for row in result:
            search_results_text += f"Uživatel ID {row[1]}: {row[0]}\n"

        chat.controls.append(
            ChatMessage(
                Message(
                    user_name="Zib",
                    text=search_results_text,
                    message_type="chat_message",
                    user_role="Bot",
                    page=page,
                )
            )
        )
        page.update()


    def evaluate_achievements(user_name, message_count):
        achieved = []
        for achievement in achievements:
            if message_count == achievement["condition"]:
                achieved.append(achievement)
        return achieved
    print("eveluate")

# Funkce pro zpracování nové zprávy
    def process_new_message(message: Message, chat, page: ft.Page):
        user_name = message.user_name

    # Inicializace uživatele v globálním slovníku, pokud ještě neexistuje
        if user_name not in user_achievements:
            user_achievements[user_name] = {"message_count": 0, "achieved": []}

    # Zvýšení počtu zpráv uživatele
        user_achievements[user_name]["message_count"] += 1
        message_count = user_achievements[user_name]["message_count"]

    # Vyhodnocení nových achievementů
        new_achievements = evaluate_achievements(user_name, message_count)

    # Přidání nových achievementů do stavu uživatele
        for achievement in new_achievements:
            user_achievements[user_name]["achieved"].append(achievement)

    # Zobrazení zprávy o nových achievementech
        if new_achievements:
            achievements_text = "Gratulujeme! Dosáhli jste následujících achievementů:\n"
            for achievement in new_achievements:
                achievements_text += f"- {achievement['name']}: {achievement['description']}\n"

        # Vytvoření nové zprávy s achievementy
            achievement_message = Message(
                user_name="Zib",
                text=achievements_text,
                message_type="chat_message",
                user_role="Bot",
                page=page,
            )

        # Vytvoření chatové zprávy a přidání do chatových kontrol
            chat_message = ChatMessage(achievement_message)
            chat.controls.append(chat_message)

    # Přidání uživatelské zprávy do chatu
        chat_message = ChatMessage(message)
        chat.controls.append(chat_message)
        print("process_new_message")
        page.update()

# Funkce pro zpracování odeslání zprávy uživatelem
    def on_user_message_submit(e):
        user_message_text = user_message_input.value  # Získání textu zprávy od uživatele
        user_name = page.session.get("user_name")  # Získání jména uživatele ze session
        message = Message(
            user_name=user_name,
            text=user_message_text,
            message_type="chat_message",
            user_role="User",
            page=page,
        )
        print("on_user_message_submit")

        process_new_message(message, chat, page)
        user_message_input.value = ""  # Vyčištění vstupního pole
        page.update()

# Funkce pro zpracování seznamu achievementů
    def list_achievements(message: Message, page: ft.Page):
        page = message.page
        achievements_text = "Dostupné achievementy:\n"
        for index, achievement in enumerate(achievements, start=1):
            achievements_text += f"{index}. {achievement['name']}: {achievement['description']}\n"

    # Vytvoření nové zprávy s achievementy
        new_message = Message(
            user_name="Zib",
            text=achievements_text,
            message_type="chat_message",
            user_role="Bot",
            page=page,
        )

    # Vytvoření chatové zprávy a přidání do chatových kontrol
        chat_message = ChatMessage(new_message)
        chat.controls.append(chat_message)
    
    
    command_list = {
        "!help": handle_help,
        "!mute": handle_mute_command,
        "!message": show_messages,
        "!users": lambda msg, pg: show_all_users(msg, pg) if len(msg.text.split()) == 1 else show_user_details(msg, pg),
        "!warn": handle_warn_command,
        "!cl": handle_calculator,
        "!s": search_command,
        "!m": search_messages,
        "!av": list_achievements
    }

    user_permissions = ["Majitel", "Admin", "Učitel", None, "Test", "Ředitel"]
    full_permissions = ["Majitel", "Admin", "Učitel", "Test", "Ředitel"]

    command_permissions = {
    "!help": user_permissions,
    "!cl": user_permissions,
    "!s": user_permissions,
    "!mute": full_permissions,
    "!message": full_permissions,
    "!users": full_permissions,
    "!warn": full_permissions,
    "!m": user_permissions,
    "!av": user_permissions,
    }

    def process_command(command, user_role, message_text, page):
        if command not in command_list:
            chat.controls.append(
                ChatMessage(
                    Message(
                        user_name="Zib",
                        text=f"Příkaz '{command}' neexistuje. Zkuste jiný.",
                        message_type="chat_message",
                        user_role="Bot",
                        page=page,
                    )
                )
            )
            page.update()
            return  # Ukončete funkci, protože příkaz neexistuje
        
        allowed_roles = command_permissions.get(command, [])
        if user_role in allowed_roles:
            command_list[command](Message(
                user_name=page.session.get("user_name"),
                text=message_text,
                message_type="command",
                user_role=user_role,
                page=page
            ), page)
        else:
            chat.controls.append(
                ChatMessage(
                    Message(
                        user_name="Zib",
                        text=f"Nemáte oprávnění k použití příkazu '{command}'.",
                        message_type="chat_message",
                        user_role="Bot",
                        page=page,
                    )
                )
            )
        new_message.value = ""
        new_message.focus()
        page.update()

    def send_message_click(e):        
        message_text = new_message.value
        user_id = page.session.get("user_id")
        user_role = page.session.get("user_role")

        local_cursor = mydb.cursor()
        
        if message_text.lower().startswith("!"):
            parts = message_text.lower().split(" ", 1)  # Rozdělení na příkaz a zbytek
            command = parts[0]
            process_command(command, user_role, message_text, page)
            return  
        
        if user_id is None:
            message = Message(
                Message(
                    user_name="Zib",
                    user_role="Bot",
                    text="Chyba při ukládání zprávy, identifikátor uživatele není k dispozici.",
                    message_type="system",
                    page=page,
                )
            )

            chat_message = ChatMessage(message)
            chat.controls.append(chat_message)
            return
        
        print("Odesílání zprávy:", message_text, "Uživatel:", user_id)

        message_text_lower = message_text.lower().strip()  
        if message_text_lower.startswith("!help") or message_text_lower.startswith("!calculate"):
            parts = message_text_lower.split(" ", 1)  
            command = parts[0]
            process_command(command, user_role, message_text, page)

            if command in command_list:
                print(f"Calling {command}") 
                command_list[command](Message(user_name=page.session.get("user_name"), text=message_text_lower, message_type="command", user_role=page.session.get("user_role"), page=page), page)  # Volání správné funkce z `command_list`

            else:
                print(f"Unknown command: {command}")
                ChatMessage(
                    Message(
                        user_name="Zib",
                        text=f"Příkaz '{command}' neexistuje. Zkuste jiný.",
                        message_type="chat_message",
                        user_role="Bot",
                        page=page,
                    )
                )
            page.update()
            new_message.value = ""
            new_message.focus()
            page.update()
            return 
        
        mute_text = "Nemůžete posílat zprávy, protože jste umlčeni!"
        
        if is_muted(user_id):
            message = Message(  # Chyba nastane, pokud není dříve definována
                user_name="Zib",
                text=mute_text,
                message_type="chat_message",
                user_role="Bot",
                page=page,
            )
            chat_message = ChatMessage(message)
            chat.controls.append(chat_message)
            new_message.focus()


        new_message.focus()
        new_message.update()
        new_message.disabled = True
            
        new_message.disabled = False  
        message_text = new_message.value
        update_ui_for_mute_status(user_id)  # Aktualizujte UI, pokud je umlčen
        #return

        if message_text:
            page.pubsub.send_all(
                Message(
                    user_name=f"{page.session.get('user_name')} {page.session.get('user_class')}",
                    text=message_text,
                    message_type="chat_message",
                    user_role=page.session.get("user_role"),
                    page=page,
                )
            )
            print(cursor)
            print(message_text, user_id)
            local_cursor.execute("INSERT INTO chat (message, user_id) VALUES (%s, %s)", (message_text, user_id))
            mydb.commit()


        # Vymazat pole pro zprávu
        new_message.value = ""
        new_message.focus()
        
    def session_handler(page):
        global chat, user_message_input

    # Nastavení UI a chatové komponenty
        chat = ft.Column()
        user_message_input = ft.TextField(label="Vaše zpráva", on_submit=on_user_message_submit)

        page.add(chat)
        page.add(user_message_input)

        page.update()

    def on_message(message: Message, page: ft.Page):
        chat_message = ChatMessage(message)
        chat.controls.append(chat_message)
        page.update()
        text_password.on_submit = lambda e: join_chat_click(e); page.update()
            # Create a new ChatMessage instance with the required arguments


    def nav_change(index):
        main_body.controls.clear()
        if index < len(page_map):
            main_body.controls.append(page_map[index])
        else:
            main_body.controls.append(ft.Column([ft.Text(f"HACKER!!! dělám jsi srandu :D, našel jsi chybu takovou, Tohle ->. {index} je index, jestli máš tam 1 nebo 2 nebo jakýkoliv číslo tak to je jaký číslo má například pravidla. Klikni někam jinam než jsi se kliknul, a budeš zahráněn. Když tak, mi to pravidlo nahlaš.")], alignment=ft.MainAxisAlignment.START, expand=True))
        page.update()

    def toggle_menu(e):
        page.drawer.open = True
        page.drawer.update()

    page.drawer = ft.NavigationDrawer(
        selected_index=0,
        controls=[
            ft.Container(height=12),
            ft.NavigationDrawerDestination(
                icon_content=ft.Icon(ft.icons.BOOK),
                selected_icon_content=ft.Icon(ft.icons.BOOK),
                label="Pravidla"
            ),
            ft.NavigationDrawerDestination(
                icon_content=ft.Icon(ft.icons.NEWSPAPER),
                selected_icon_content=ft.Icon(ft.icons.NEWSPAPER),
                label="Novinky",
            ),
            ft.NavigationDrawerDestination(
                icon_content=ft.Icon(ft.icons.FAVORITE_BORDER),
                selected_icon_content=ft.Icon(ft.icons.FAVORITE),
                label="Podpora",
            ),
            ft.NavigationDrawerDestination(
                icon_content=ft.Icon(ft.icons.SETTINGS),
                selected_icon_content=ft.Icon(ft.icons.SETTINGS),
                label="Nastavení"
            ),
            ft.NavigationDrawerDestination(
                icon_content=ft.Icon(ft.icons.EDIT_DOCUMENT),
                selected_icon_content=ft.Icon(ft.icons.EDIT_DOCUMENT),
                label="Kdo jsem?",
            ),
            ft.NavigationDrawerDestination(
                icon_content=ft.Icon(ft.icons.QUESTION_MARK),
                selected_icon_content=ft.Icon(ft.icons.QUESTION_MARK),
                label="Otazky",
            ),
            ft.NavigationDrawerDestination(
                icon_content=ft.Icon(ft.icons.REPORT),
                selected_icon_content=ft.Icon(ft.icons.REPORT),
                label="Nahlášení užv.",
            ),
        ],
        on_change=lambda e: nav_change(e.control.selected_index),

        # trailing=ft.Icon(ft.Icons.HELP)
    )

    divider = ft.VerticalDivider(width=1)

    main_body = ft.Column([Pravidla(page)], alignment=ft.MainAxisAlignment.START, expand=True, scroll=ft.ScrollMode.AUTO)
    # Chat messages
    chat = ft.ListView(
        expand=True,
        spacing=10,
        auto_scroll=True,
    )

    text_username = ft.TextField(
        label="Zadej uživatélské jméno",
        autofocus=True,
        on_submit=join_chat_click,
    )
    text_password = ft.TextField(
        label="Zadej heslo",
        password=True,
        on_submit=join_chat_click,
    )
    text_1 = ft.Text(
        "Nefunguje zde školní přihlášení! Jestli jste zde nový, klikněte na Registrovat účet",
        size=11
    )

    page.dialog = ft.AlertDialog(
        open=True,
        modal=True,
        title=ft.Text("Vítej!"),
        content=ft.Column([text_username, text_password, text_1], width=340, height=145, tight=True),
        actions=[
            ft.ElevatedButton(text="Připojit se", on_click=join_chat_click),
            ft.ElevatedButton(text="Registrovat účet", on_click=create_account),
        ],
        actions_alignment="end",
    )

    online_users_text = ft.Text(f"Počet uživatelů online: {len(online_users)}", color=ft.colors.WHITE, size=12)

    page.add(
        ft.AppBar(
            leading=ft.IconButton(
                icon=ft.icons.MENU,
                tooltip="Menu",
                on_click=toggle_menu,
            ),
            leading_width=100,
            title=ft.Text(""),
            center_title=False,
            bgcolor=ft.colors.SURFACE_VARIANT,
            actions=[
                online_users_text,
                ft.IconButton(
                    icon=ft.icons.LOGOUT,
                    tooltip="Odhlásit",
                    on_click=lambda e: _logout(page, chat),
                ),
            ],
        )
    )

    page.pubsub.subscribe(lambda message, page=page: on_message(message, page))

    page.add(
        ft.Row(
            [
                ft.Column([main_body,
                           # ft.Container(
                           #     content=chat,
                           #     border=ft.border.all(1, ft.colors.OUTLINE),
                           #     border_radius=5,
                           #     padding=10,
                           #     expand=True,
                           # ),
                           # ft.Row(
                           #     [
                           #         new_message,
                           #         ft.IconButton(
                           #             icon=ft.icons.SEND_ROUNDED,
                           #             tooltip="Pošli zprávu",
                           #             on_click=send_message_click,
                           #         ),
                           #     ]
                           # ),
                           ])
            ],
            expand=True,
        )
    )

    page.add(
        ft.Container(
            content=chat,
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=5,
            padding=10,
            expand=True,
        ),
        ft.Row(
            [
                new_message,
                ft.IconButton(
                    icon=ft.icons.SEND_ROUNDED,
                    tooltip="Pošli zprávu",
                    on_click=send_message_click,
                ),
            ]
        ),
    )



ft.app(port=8550, target=main, view=ft.WEB_BROWSER)