import flet as ft
from flet import Text, ControlEvent, TextField, Dropdown, ElevatedButton, Row
from datetime import datetime, timedelta
import socket
import webbrowser
import os
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

        self.user_name = TextField(label="Zadej uživatélské jméno:::")
        self.email = TextField(label="Zadej email.")
        self.trida = Dropdown(label="Třída", options=tridy)
        self.password = TextField(label="Zadej heslo.", password=True)
        self.password_confirm = TextField(label="Potvrď heslo.", password=True)
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
            page.dialog.open = False
            welcome = f"{user} Vítej mezi námi! Snad se ty to bude líbit. Můžeš napsat !Help nebo !help a zjistíš co je co!."
            if role:
                welcome = f"{user} {role} Vítej mezi námi! Snad se ty to bude líbit. Když tak, jsi {role}."

            page.pubsub.send_all(Message(user_name=user, user_role=role, text=welcome, message_type="login_message", page=page)),

            page.update()

        self.error_message.value = "Registrace proběhla úspěšně."
        self.error_message.update()

    def createForm(self):
        return ft.Column([self.user_name,
                          self.email,
                          self.trida,
                          self.password,
                          self.password_confirm,
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
    def __init__(self, message: Message):
        super().__init__()
        self.vertical_alignment = "start"

        user_info = message.user_name

        m = []

        if message.user_name:
            m = [
                ft.Text(message.user_name, weight="bold", color=ft.colors.WHITE),
                ft.Text(message.text, selectable=True, width=message.page.width - 100),
            ]

        if message.user_role != None:
            user_info += f" [{message.user_role}]"
            m = [
                ft.Text(user_info, weight="bold", color=ft.colors.YELLOW),
                ft.Text(message.text, selectable=True, width=message.page.width - 100),
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
            # Ověřte, že kontrolní prvky jsou správně inicializovány
            if isinstance(text_username, ft.TextField) and isinstance(text_password, ft.TextField):
                # Před voláním 'page.update()', ujistěte se, že všechny kontrolní prvky mají unikátní identifikátor
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
            return

        login = _login(text_username, text_password)
        # Clear the password field
        text_password.value = ""
        text_password.update()

        if not login["success"]:
            error_message = login.get("message", "An unknown error occurred.")
            text_username.error_text = error_message
            text_username.update()

            # Přidáme tlačítko pro znovu přihlášení
            page.dialog.actions.append(
                ft.ElevatedButton(text="Zapomenutý údaje?", on_click=clear_error_and_retry)
            )
            # page.dialog.update()

        else:
            text_username.value = ""
            text_username.update()
            user = login["user"]["user_name"]
            page.session.set("user", login["user"])
            page.session.set("user_name", login["user"]["user_name"])
            page.session.set("user_id", login["user"]["id"])
            page.session.set("user_class", login["user"]["class"])
            page.session.set("user_email", login["user"]["email"])
            page.session.set("user_role", login["user"]["role"])
            page.dialog.open = False
            new_message.prefix = ft.Text(f"{user}: ")
            page.pubsub.send_all(Message(user_name=user, text=f"{user} se připojil do chatu. Připoj se k pobavení!", message_type="login_message", user_role=None, page=page))

            cursor.execute("SELECT message, user_name, class, role FROM chat join user on user.id = chat.user_id order by chat.id desc limit 10")
            result = cursor.fetchall()
            columns = [column[0] for column in cursor.description]

        for row in result:
            data = dict(zip(columns, row))
            user_name = data["user_name"]
            user_class = data.get("class", "")
            user_role = data.get("role", "")  # Získáme třídu uživatele, pokud existuje  # Získáme roli uživatele, pokud existuje
            message = Message(user_name=f"{user_name} {user_class}", text=data["message"], message_type="chat_message", user_role=user_role, page=page)
            chat_message = ChatMessage(message)
            chat.controls.append(chat_message)

            # page.update()
        join_chat_click(e)

    def clear_error_and_retry(form):
        error_dialog = ft.AlertDialog(
            open=True,
            modal=True,
            title=ft.Text("Zapomenutý heslo/uživ. jméno"),
            content=ft.Column([
                ft.Text("Zapoměl jsi si heslo nebo uživatelské jméno?"),
                ft.Text("Kontaktuj mě : vojta.kurinec@gmail.com"),
                ft.Text("Budu se snažit tak aby to bylo dostatečně rychlý!"),
                # ElevatedButton(text="Zpět k chatu", on_click=lambda e: _logout(page, chat))
            ], width=200, height=200, tight=True),
        )
        page.dialog = error_dialog
        page.update()

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
    
        if len(parts) == 1:  # Pokud není zadáno uživatelské jméno, zobrazíme všechny zprávy
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
        elif len(parts) == 2:  # Pokud je zadáno uživatelské jméno, zobrazíme zprávy daného uživatele
            user_name = parts[1].strip()
            cursor.execute("SELECT message FROM chat WHERE user_id = (SELECT id FROM user WHERE user_name = %s) ORDER BY id DESC", (user_name,))
            result = cursor.fetchall()

            if not result:
                user_messages = f"Nenašli jsme žádné zprávy od uživatele {user_name}."
            else:
                user_messages = f"Zprávy od uživatele {user_name}:\n"
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
                        text="Musíte zadat jméno uživatele! Např. '!users Vojta'.",
                        message_type="chat_message",
                        user_role="Bot",
                        page=page,
                    )
                )
            )
            page.update()
            return
    
        username = parts[1].strip()  # Jméno uživatele
        cursor.execute("SELECT user_name, class, role, id FROM user WHERE user_name = %s LIMIT 1", (username,))
        result = cursor.fetchone()

        if result:
            user_text = f"Uživatel: {result[0]}\nTřída: {result[1]}\nRole: {result[2]}\nID: {result[3]}\n"
        else:
            user_text = f"Uživatel s jménem '{username}' nebyl nalezen."

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
    
    def handle_help(message: Message, page: ft.Page):
        help_text = "Ahoj, já jsem Zib! Jsem robot a dělám to abych jsem ti pomohl. Dostupné příkazy jsou:\n"
        help_text += "- !Help: Zobrazí tuto nápovědu.\n"
        #help_text += "- @JehoJméno: Pošle soukromou zprávu uživateli 'JehoJméno'.\n"
        help_text += "- Když tak, když klikneš na ty 3 čáry nahoře, tak to je menu, a uvidíš co je tam! .\n"
        help_text += "- Dodržuj pravidla, tak abys jsi nedostal ban, mute, nebo varování! Jestli máš nějaké otázky, ptej se Majitele.\n"

        
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
    def mute_user(user_id, duration_minutes):
        try:
            # if not mydb.is_connected():
            #     mydb.reconnect(attempts=100, delay=5)

            # Zkontrolujte, zda sloupec 'mute_end' existuje
            # cursor.execute("SHOW COLUMNS FROM muted_users LIKE 'mute_end'")
            # if not cursor.fetchone():
            #     print("Sloupec 'mute_end' neexistuje.")
            #     return

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

        if len(parts) == 2:
            try:
                user_id = int(parts[1].strip())
                print(f"Muting user {user_id} for 1 minutes")
                duration_minutes = 1
                mute_user(user_id, duration_minutes)

                            # Použijte nový kurzor pro umlčení uživatele
                local_cursor = mydb.cursor()
            
            # Umlčení uživatele
                mute_end_time = datetime.now() + timedelta(minutes=duration_minutes)
                local_cursor.execute("INSERT INTO muted_users (user_id, mute_end) VALUES (%s, %s)", (user_id, mute_end_time))
                mydb.commit()

            # Notify the Chat
                current_page.pubsub.send_all(
                    Message(
                        user_name="Zib",
                        user_role="Bot",
                        text=f"Uživatel s ID : {user_id} byl umlčen na {duration_minutes} minut.",
                        message_type="system",
                        page=current_page,
                    )
                )
            except ValueError:
                current_page.pubsub.send_all(
                    Message(
                        user_name="Zib",
                        user_role="Bot",
                        text="Neplatné ID uživatele. Použijte správný formát !Mute <User_ID>.",
                        message_type="system",
                        page=current_page,
                    )
                )
        else:
            current_page.pubsub.send_all(
                Message(
                    user_name="Zib",
                    user_role="Bot",
                    text="Neplatný příkaz! Použijte formát !Mute <User_ID>.",
                    message_type="system",
                    page=current_page,
                )
            )

    command_list = {
        "!help": handle_help,
        "!mute": handle_mute_command,
        "!message": show_messages,
        "!users": lambda msg, pg: show_all_users(msg, pg) if len(msg.text.split()) == 1 else show_user_details(msg, pg),  # Podmíněné zpracování
        # Add more commands here
    }

    command_permissions = {
    "!mute": ["Majitel",] or ["Admin"],
    "!message": ["Majitel",] or ["Admin"],
    "!users": ["Majitel",] or [ "Admin"],
    }

    def process_command(command, user_role, message_text, page):
    # Zkontrolujte, zda uživatel má oprávnění pro daný příkaz
        
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
        # Pokud má oprávnění, zavolejte příslušnou funkci
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
            page.update()

    def send_message_click(e):        
        message_text = new_message.value
        user_id = page.session.get("user_id")
        user_role = page.session.get("user_role")

        local_cursor = mydb.cursor()


        if message_text.lower().startswith("!"):
            parts = message_text.lower().split(" ", 1)  # Rozdělení na příkaz a zbytek
            command = parts[0]  # První část je příkaz
        # Zpracujte příkaz pouze pokud má uživatel oprávnění
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
        if message_text_lower.startswith("!help") or message_text_lower.startswith("!mute"):
            parts = message_text_lower.split(" ", 1)  
            command = parts[0]

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
        page.update()


    def on_message(message: Message, page: ft.Page):

        # Rozpoznání příkazu začínajícího "
        # Pokud to není příkaz, pokračujte ve zpracování běžných zpráv
        chat_message = ChatMessage(message)
        chat.controls.append(chat_message)
        page.update()
        text_password.on_submit = lambda e: join_chat_click(e); page.update()

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
    # A dialog asking for a user display name

    # A new message entry form
    # ZDE TO BYLO

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
