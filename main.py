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

        self.user_name = TextField(label="Zadej uživatélské jméno:")
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
            welcome = f"{user} Vítej mezi námi! Snad se ty to bude líbit."
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
        if page is not None:
            # Ověřte, že kontrolní prvky jsou správně inicializovány
            if isinstance(text_username, ft.TextField) and isinstance(text_password, ft.TextField):
                # Před voláním 'page.update()', ujistěte se, že všechny kontrolní prvky mají unikátní identifikátor
                page.update()

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
            page.dialog.update()

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
            page.pubsub.send_all(Message(user_name=user, text=f"{user} se připojil do chatu. Vítej mezi náma.", message_type="login_message", user_role=None, page=page))

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

            page.update()
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
                ElevatedButton(text="Zpět k chatu", on_click=lambda e: _logout(page, chat))
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

    def check_connection():
        if not mydb.is_connected():
            try:
                mydb.reconnect(attempts=3, delay=5)
            except mysql.connector.Error as err:
                print("Error reconnecting:", err)

    # Vrátít se zde, udělat zprávy tak aby se zobrazili jenom 1x, a ne vícekrát jak chce system.
    def handle_help(message: Message, page: ft.Page):

        help_text = "Ahoj, já jsem Zib! Jsem tady, abych ti pomohl. Dostupné příkazy jsou:\n"
        help_text += "- !Help: Zobrazí tuto nápovědu.\n"
        help_text += "- @JehoJméno: Pošle soukromou zprávu uživateli 'JehoJméno'.\n"
        help_text += "- Když tak, když klikneš na ty 3 čáry nahoře, tak to je menu, a uvidíš co je tam! .\n"
        help_text += "- Dodržuj pravidla, tak abys jsi nedostal ban, mute, nebo varování! Jestli máš nějaké otázky, ptej se Majitele.\n"

        # Sending the message from "Zib"
        message = Message(
            user_name="Zib",
            text=help_text,
            message_type="chat_message",
            user_role="Pomocník/Bot",
            page=page,

        )
        chat_message = ChatMessage(message)
        chat.controls.append(chat_message)


    def is_muted(user_id):
        cursor.execute("SELECT mute_end FROM muted_users WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        if result:
            mute_end_time = result[0]
            if datetime.now() < mute_end_time:
                return True
            else:
                # Odstranit záznam z umlčených po vypršení
                cursor.execute("DELETE FROM muted_users WHERE user_id = %s", (user_id,))
                mydb.commit()
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
                print(f"Muting user {user_id} for 15 minutes")

                # Mute Duration
                duration_minutes = 15

                # Mute the User
                mute_user(user_id, duration_minutes)

                # Notify the Chat
                current_page.pubsub.send_all(
                    Message(
                        user_name="Zib",
                        user_role="Bot/Pomocník",
                        text=f"Uživatel s ID : {user_id} byl umlčen na {duration_minutes} minut.",
                        message_type="system",
                        page=current_page,
                    )
                )
            except ValueError:
                current_page.pubsub.send_all(
                    Message(
                        user_name="Zib",
                        user_role="Bot/Pomocník",
                        text="Neplatné ID uživatele. Použijte správný formát !Mute <User_ID>.",
                        message_type="system",
                        page=current_page,
                    )
                )
        else:
            current_page.pubsub.send_all(
                Message(
                    user_name="Zib",
                    user_role="Bot/Pomocník",
                    text="Neplatný příkaz! Použijte formát !Mute <User_ID>.",
                    message_type="system",
                    page=current_page,
                )
            )

    command_list = {
        "!help": handle_help,
        "!mute": handle_mute_command,
        # Add more commands here
    }

    def send_message_click(e):
        message_text = new_message.value

        user_id = page.session.get("user_id")

        # Zkontrolovat, zda user_id není prázdné
        if user_id is None:
            page.pubsub.send_all(
                Message(
                    user_name="Zib",
                    user_role="Bot/Pomocník",
                    text="Chyba při ukládání zprávy, identifikátor uživatele není k dispozici.",
                    message_type="system",
                    page=page,
                )
            )
            return
        print("Odesílání zprávy:", message_text, "Uživatel:", user_id)

        # Zkuste provést SQL příkaz s ošetřením chyb
        # try:
        #     cursor.execute("INSERT INTO chat (message, user_id) VALUES (%s, %s)", (message_text, user_id))
        #     mydb.commit()
        #     print("Zpráva úspěšně uložena.")
        # except mysql.connector.Error as err:
        #     print("Chyba při ukládání zprávy:", err)

        # if new_message:
        #     message_text = new_message.value
        #
        # if message_text and user_id:
        #     page.pubsub.send_all(
        #         Message(
        #             user_name=f"{page.session.get('user_name')} {page.session.get('user_class')}",
        #             text=message_text,
        #             message_type="chat_message",
        #             user_role=page.session.get("user_role"),
        #             page=page
        #         )
        #     )
        # # cursor.execute("INSERT INTO chat (message, user_id) VALUES (%s, %s)", (message_text, user_id))
        # # mydb.commit()
        # new_message.value = ""
        # new_message.focus()
        # page.update()

        # if new_message.value != "":
        #     page.pubsub.send_all(Message(
        #         user_name=f"{page.session.get('user_name')} {page.session.get('user_class')}",
        #         text=new_message.value,
        #         message_type="chat_message",
        #         user_role=page.session.get("user_role"),
        #         page=page  # Include the missing 'page' argument
        #     ))
        #     cursor.execute("INSERT INTO chat (message, user_id) VALUES (%s, %s)", (new_message.value, page.session.get("user_id")))
        #     mydb.commit()
        #     new_message.value = ""
        #     new_message.focus()
        #     page.update()

        # if message_text!= "":
        #     if message_text.startswith("@"):  # Check if the message is private
        #         parts = message_text.split(" ", 1)
        #         if len(parts) == 2:
        #            target_user, private_message = parts
        #            target_user = target_user[1:]
        #            if target_user in online_users:
        #                 target_session_id = online_users[target_user]
        #             # Send to the specific user
        #                 page.pubsub.send(target_session_id, private_message)
        #                 cursor.execute(
        #                     "INSERT INTO private_chat (message, sender_id, receiver_id) VALUES (%s, %s, %s)",
        #                     (private_message, page.session.get("user_id"), target_session_id),
        #                 )
        #                 mydb.commit()
        #         else:
        #             # Handle user not online
        #             print("Uživatel není online")
        #     else:a
        #         # Handle invalid private message format
        #         print("Špatný formát soukromé zprávy")
        # else:
        # It's a public message, send to all users
        # page.pubsub.send_all(Message(
        #     user_name=f"{page.session.get('user_name')} {page.session.get('user_class')}",
        #     text=message_text,
        #     message_type="chat_message",
        #     user_role=page.session.get("user_role"),
        #     page=page
        # ))
        # cursor.execute("INSERT INTO chat (message, user_id) VALUES (%s, %s)", (message_text, page.session.get("user_id")))
        # mydb.commit()
        # new_message.value = ""
        # new_message.focus()
        # page.update()

        message_text_lower = message_text.lower().strip()  # Normalizace textu na malá písmena a odstranění mezer
        if message_text_lower.startswith("!help") or message_text_lower.startswith("!mute"):
            parts = message_text_lower.split(" ", 1)  # Rozdělení na příkaz a zbytek
            command = parts[0]  # První část je příkaz

            # Pokud je to příkaz !Help, zavolejte funkci handle_help

            if command in command_list:
                # Volání obslužné funkce
                print(f"Calling {command}")  # Ověření, že je volána správná funkce
                command_list[command](message_text_lower, page)  # Volání správné funkce z `command_list`

            else:
                print(f"Unknown command: {command}")
                page.pubsub.send_all(Message(
                    user_name="Zib",
                    user_role="Pomocník/Bot",
                    text=f"Neznámý příkaz: '{command}'",
                    message_type="chat_message",
                    page=page
                ))
                return
            new_message.value = ""
            new_message.focus()
            page.update()
            return # Ukončit funkci, aby zpráva nebyla odeslánaa

        if is_muted(user_id):
            # Informovat uživatele, že je umlčen
            page.pubsub.send_all(
                Message(
                    user_name="Zib",
                    text="Nemůžete posílat zprávy, protože jste umlčeni!",
                    message_type="system",
                    user_role="Pomocník/Bot",
                    page=page,
                )
            )
            return  # Ukončit funkci, aby zpráva nebyla odeslána

        # Pokud uživatel není umlčen, pokračujte s odesíláním zpráv
        message_text = new_message.value
        if message_text:
            page.pubsub.send_all(
                Message(
                    user_name=f"{page.session.get('user_name')} {page.session.get('user_class')}",
                    text=message_text,
                    message_type="chat_message",
                    user_role=page.session.get("user_role"),
                    page=page
                )
            )
            cursor.execute("INSERT INTO chat (message, user_id) VALUES (%s, %s)", (message_text, user_id))
            mydb.commit()

        # Vymazat pole pro zprávu
        new_message.value = ""
        new_message.focus()
        page.update()

    def on_message(message: Message, page: ft.Page):

        # Rozpoznání příkazu začínajícího "
        # Pokud to není příkaz, pokračujte ve zpracování běžných zpráv
        print("standart")
        chat_message = ChatMessage(message)
        chat.controls.append(chat_message)
        page.update()

    def nav_change(index):
        main_body.controls.clear()
        if index < len(page_map):
            main_body.controls.append(page_map[index])
        else:
            main_body.controls.append(ft.Column([ft.Text(f"HACKER!!! (dělám jsi srandu :D, našel jsi chybu takovou, Tohle ->). {index} je index, jestli máš tam 1 nebo 2 nebo jakýkoliv číslo tak to je jaký číslo má například pravidla. Klikni někam jinam než jsi se kliknul, a budeš zahráněn")], alignment=ft.MainAxisAlignment.START, expand=True))
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

    # Add everything to the page


ft.app(port=8550, target=main, view=ft.WEB_BROWSER)
