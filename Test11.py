import flet as ft
from flet import Text, ControlEvent, TextField, Dropdown, ElevatedButton, Row
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


mydb = mysql.connector.connect(
    host=os.environ["DB_HOST"],
    port=os.environ["DB_PORT"],
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASS"],
    database=os.environ["DB_NAME"]
)
cursor = mydb.cursor()


class Registrace():
    def __init__(self, Page: ft.Page):
 
        tridy = []
        for i in range(9):
            tridy.append(ft.dropdown.Option(f"{i+1}.A"))
            tridy.append(ft.dropdown.Option(f"{i+1}.B"))
 
        self.user_name = TextField(label="Zadej uživatélské jméno:")
        self.email = TextField(label="Zadej email.")
        self.trida = Dropdown(label="Třída", options=tridy)
        self.password = TextField(label="Zadej heslo.", password=True)
        self.password_confirm = TextField(label="Potvrď heslo.", password=True)
        self.submit = ElevatedButton(text="Registrovat", on_click=self.submit_click)
        self.error_message = Text("Jestli se ty nejde zaregistrovat, tak zkus jiný jméno, třeba přidat za svým jménem tečku, čárku, nebo něco jiného. Někdo už bohužel má tohle jméno zabraný."  ,size=12)
        self.page = Page

    def submit_click(self, e):
        if not self.user_name.value or not self.email.value or not self.password.value or not self.password_confirm.value:
            self.error_message.value = "Všechny pole musí být vyplněny."
            self.error_message.update()
            return
        if self.password.value != self.password_confirm.value:
            self.error_message.value = "Hesla se neshodují."
            self.error_message.update()
            return
        hashed_password, salt = hash_password(self.password.value)
        cursor.execute("INSERT INTO user (user_name, email, class, password, salt) VALUES (%s, %s, %s, %s, %s)", (self.user_name.value, self.email.value, self.trida.value,hashed_password.decode("utf-8"), salt.decode("utf-8")))
        mydb.commit()

        login = _login(self.user_name, self.password)

        if login["success"]:
            page = self.page
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            user = login["user"]["user_name"]
            page.session.set("user_name", login["user"]["user_name"])
            page.session.set("user_id", login["user"]["id"])
            page.session.set("user_class", login["user"]["class"])
            page.dialog.open = False
            page.pubsub.send_all(Message(user_name=user, text=f"{user} Vítej mezi námi! Snad se ty to bude líbit. {ip_address}",message_type="login_message"))
            print("{ip_address}") 
            page.update()

        self.error_message.value = "Registrace proběhla úspěšně."
        self.error_message.update()

    def createForm(self):
        return ft.Column([self.user_name, self.email, self.trida, self.password, self.password_confirm, self.submit, self.error_message], width=300, tight=True)

class Message():
    def __init__(self, user_name: str, text: str, message_type: str, user_role: str):
        self.user_name = user_name
        self.text = text
        self.message_type = message_type
        self.user_role = user_role


class ChatMessage(ft.Row):
    def __init__(self, message: Message):
        super().__init__()
        self.vertical_alignment = "start"
    
        self.controls = [
            ft.CircleAvatar(
                content=ft.Text(self.get_initials(message.user_name)),
                color=ft.colors.WHITE,
                bgcolor=self.get_avatar_color(message.user_name),
            ),
            ft.Column(
                [
                    
                    ft.Text(message.user_name, weight="bold"),
                    ft.Text(f"Role: {message.user_role}" if message.user_role else "", size=10),
                    ft.Text(message.text, selectable=True),
                ],
                tight=True,
                spacing=5,
            ),
        ]


    def get_initials(self, user_name: str):
        if user_name:
            return user_name[:1].capitalize()
        else:
            return ""  # or any default value you prefer
        
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
            online_users.add(data[0]['user_name'])

        else:
            response["message"] = "Špatně jsi zadal heslo"
    else:
        response["message"] = "Špatně jsi zadal jméno"

    return response


def main(page: ft.Page):
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
            page.pubsub.send_all(Message(user_name=user, text=f"{user} se připojil do chatu. Vítej mezi náma", message_type="login_message", user_role="login_message"))

            cursor.execute("SELECT message, user_name, class, role  FROM chat join user on user.id = chat.user_id order by chat.id desc limit 10")
            result = cursor.fetchall()
            columns = [column[0] for column in cursor.description]

        for row in result:
            data = dict(zip(columns, row))
            user_name = data["user_name"]
            user_class = data.get("class", "")  # Získáme třídu uživatele, pokud existuje
            user_role = data.get("role", "")  # Získáme roli uživatele, pokud existuje
            message = Message(user_name=f"{user_name} {user_class} {user_role}", text=data["message"], message_type="chat_message", user_role=user_role)
            chat_message = ChatMessage(message)
            chat.controls.append(chat_message)



            page.update()

    def clear_error_and_retry(form):
        error_dialog = ft.AlertDialog(
            open=True,
            modal=True,
            title=ft.Text("Zapomenutý heslo/uživ. jméno"),
            content=ft.Column([
                ft.Text("Zapoměl jsi si heslo nebo uživatelské jméno?"),
                ft.Text("Kontaktuj mě : vojta.kurinec@gmail.com"),
                ft.Text("Budu se snažit tak aby to bylo dostatečně rychlý!"),
                ElevatedButton(text="Zpět k chatu", on_click=lambda e: _logout(page,chat))
            ], width=200, height=200, tight=True),
        )    
        page.dialog = error_dialog
        page.update()
    
    def create_account(e):
        # Přesměrování na stránku pro registraci
        form = Registrace(page).createForm()
        page.dialog = ft.AlertDialog(
            open=True,
            modal=True,
            title=ft.Text("Registrace!"),
            content=ft.Column([form], width=300, height=400, tight=True),
        )

        page.update()

    def chat_zpatky():
        webbrowser.open("https://voku-skolni-chat.fly.dev/")    
        

    def send_message_click(e):
        if new_message.value != "":
            page.pubsub.send_all(Message(f"{page.session.get("user_name")} {page.session.get("user_class")}", new_message.value, message_type="chat_message", user_role=page.session.get("user_role")))
            cursor.execute("INSERT INTO chat (message, user_id) VALUES (%s, %s)", (new_message.value,page.session.get("user_id") ))
            mydb.commit()
            new_message.value = ""
            new_message.focus()
            page.update()

    def on_message(message: Message):
        if message.message_type == "chat_message":
            m = ChatMessage(message)
        elif message.message_type == "login_message":
            m = ft.Text(message.text, italic=True, color=ft.colors.WHITE70, size=12)
        chat.controls.append(m)
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


    page.pubsub.subscribe(on_message)
    # A dialog asking for a user display name

    # A new message entry form
    new_message = ft.TextField(
        hint_text="Napiš zprávu...",
        autofocus=True,
        shift_enter=True,
        min_lines=1,
        max_lines=5,
        filled=True,
        expand=True,
        on_submit=send_message_click,
    )


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