import flet as ft
from flet import Text,  ControlEvent, TextField, ElevatedButton, Row
import socket
import webbrowser
import os
from Novinky import Novinky
from Pravidla import Pravidla
from Podpora import Podpora
import mysql.connector
import bcrypt

mydb = mysql.connector.connect(
   host="127.0.0.1",
    port=3306,
    user="root",
    password="root",
    database="chat"
)
cursor = mydb.cursor()



class Message():
    def __init__(self, user_name: str, text: str, message_type: str):
        self.user_name = user_name
        self.text = text
        self.message_type = message_type
class ChatMessage(ft.Row):
    def __init__(self, message: Message):
        super().__init__()
        self.vertical_alignment="start"
        self.controls=[
                ft.CircleAvatar(
                    content=ft.Text(self.get_initials(message.user_name)),
                    color=ft.colors.WHITE,
                    bgcolor=self.get_avatar_color(message.user_name),
                ),
                ft.Column(
                    [
                        ft.Text(message.user_name, weight="bold"),
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
            return "Unknown"  # or any default value you prefer
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
            ft.colors.YELLOW,
        ]
        return colors_lookup[hash(user_name) % len(colors_lookup)]
def main(page: ft.Page):
    page.horizontal_alignment = "stretch"
    page.title = "Zstsobra chat (Beta verze)"
    page.theme_mode = ft.ThemeMode.DARK

    
    pravidla = Pravidla()
    novinky = Novinky()
    podpora = Podpora()
    page_map = [
        pravidla,
        novinky,
        podpora,

    ]



    def join_chat_click(e):
        login = submit(text_username, text_password)
        if not text_username.value or not text_password.value:
            error_message = "Zadej uživatélské jméno."
            text_password.error_text = "Zadej heslo."
            text_username.error_text = error_message
            text_password.error_text = text_password.error_text
            text_username.update()
            text_password.update()
            page.dialog.update()
            
            return
        
        if not login["success"]:
            error_message = login.get("message", "An unknown error occurred.")
            text_username.error_text = error_message
            text_username.update()

        # Přidáme tlačítko pro znovu přihlášení       

            page.dialog.update()

        else:
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            user = login["user"]["user_name"]
            page.session.set("user_name", login["user"]["user_name"])
            page.dialog.open = False
            new_message.prefix = ft.Text(f"{user}: ")
            page.pubsub.send_all(Message(user_name=user, text=f"{user} Se připojil do chatu!. Jeho IP: {ip_address}", message_type="login_message"))
            page.update()
    
    def clear_error_and_retry():
       text_username.error_text = ""
       text_username.update()

    # Kód pro skrytí tlačítka a možnost znovu zadat jméno a heslo
       page.dialog.actions.pop()  # Odebrat tlačítko "Znovu přihlásit"
       page.dialog.update()

       text_username.value = ""  # Vyčistit pole s uživatelským jménem
       text_password.value = ""  # Vyčistit pole s heslem
       text_username.focus()  # Nastavit kurzor do pole s uživatelským jménem

    def create_account(e):
    # Přesměrování na stránku pro registraci
        webbrowser.open("https://voku-skolni-chat.fly.dev/")
       

    
    
    
    
    def send_message_click(e):
        if new_message.value != "":
            page.pubsub.send_all(Message(page.session.get("user_name"), new_message.value, message_type="chat_message"))
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

    def hash_password(password, salt=None):
        # Hash a password using bcrypt
        if salt is None:
            salt = bcrypt.gensalt()
        else:
            salt = salt.encode('utf-8')

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password, salt

    
    def nav_change(index):
        main_body.controls.clear()
        if index < len(page_map):
            main_body.controls.append(page_map[index])
        else:
            main_body.controls.append(ft.Column([ ft.Text(f"Hmmm. Něco chybí zde. {index} Klikni na Novinky/Pravidla.")], alignment=ft.MainAxisAlignment.START, expand=True))
        page.update()

    def submit(username: TextField, password: TextField) -> dict:
        print("Username:", username.value)
        print("Password:", password.value)
        
        response = {"success": False}
        
        cursor.execute("SELECT * FROM user WHERE user_name = %s OR email = %s LIMIT 1",(username.value, username.value))
        result = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        data = [dict(zip(columns, row)) for row in result]

        if data and data[0]:
            hashed_password, _ = hash_password(password.value, data[0]['salt'])
            if data[0]['password'] == hashed_password.decode("utf-8"):
                response["success"] = True
                response["user"] = data[0]

            else:
                response["message"] = "Špatně jsi zadal heslo"
        else:
            response["message"] = "Špatně jsi zadal jméno"

        return response              




   
    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        # extended=True,
        min_width=100,
        min_extended_width=400,
        group_alignment=-0.9,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.icons.BOOK, selected_icon=ft.icons.BOOK, label="Pravidla"
            ),
            ft.NavigationRailDestination(
                icon_content=ft.Icon(ft.icons.NEWSPAPER),
                selected_icon_content=ft.Icon(ft.icons.NEWSPAPER),
                label="Novinky",
            ),
            ft.NavigationRailDestination(
                icon_content=ft.Icon(ft.icons.FAVORITE_BORDER),
                selected_icon_content=ft.Icon(ft.icons.FAVORITE),
                label="Podpora",
            ),
        ],
        on_change=lambda e: nav_change(e.control.selected_index),
    )

    main_body = ft.Column([Pravidla()], alignment=ft.MainAxisAlignment.START, expand=True, scroll=ft.ScrollMode.AUTO)

    page.add(
        ft.Row(
            [
                rail,
                ft.VerticalDivider(width=1),
                main_body
            ],
            expand=True,
        )
    )

    page.pubsub.subscribe(on_message)
    # A dialog asking for a user display name
    text_username = ft.TextField(
        label="Zadej jméno abys se připojil.",
        autofocus=True,
        on_submit=join_chat_click,
    )
    text_password = ft.TextField(
        label="Zadej heslo",
        password=True,
        on_submit=join_chat_click,
    )

    page.dialog = ft.AlertDialog(
        open=True,
        modal=True,
        title=ft.Text("Vítej!"),
        content=ft.Column([text_username, text_password], width=300, height=140, tight=True),
        actions=[
            ft.ElevatedButton(text="Připojit se", on_click=join_chat_click),
            ft.ElevatedButton(text="Registrovat účet", on_click=create_account),
        ],
        actions_alignment="end",
    )
    # Chat messages
    chat = ft.ListView(
        expand=True,
        spacing=10,
        auto_scroll=True,
    )
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
    # Add everything to the page
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
