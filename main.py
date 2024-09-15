# Python a atd..
import flet as ft
from flet import Text, TextField, Dropdown, ElevatedButton, Row, Checkbox, FilePicker, Ref
from datetime import datetime, timedelta
import os
import re
import webbrowser
import base64
from functools import partial
import requests
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading
import time

# Důležité
from Novinky import Novinky
from Pravidla import Pravidla
from Podpora import Podpora
from Nastaveni import Nastavení
from Recenze import Recenze
from Jsem import Jsem
from Otazky import Otazky
from Nahlaseni import Nahlaseni

# Databáze
import mysql.connector
import bcrypt
import sqlite3

# Seznam přihlášených uživatelů
online_users = set()
online_users = {}
current_page = None
error_dialog_shown = False
milestones = [10, 100, 1000, 10000]
incorrect_attempts = 0

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------


mydb = mysql.connector.connect(
    host=os.environ["DB_HOST"],
    port=os.environ["DB_PORT"],
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASS"],
    database=os.environ["DB_NAME"],
    connection_timeout=30,
)
cursor = mydb.cursor()


# ----------------------------------------------------------------------------------------------------------------------------------------------------------------


class Registrace:
    def __init__(self, page: ft.Page):
        tridy = []
        for i in range(9):
            tridy.append(ft.dropdown.Option(f"{i + 1}.A"))
            tridy.append(ft.dropdown.Option(f"{i + 1}.B"))

        self.error_message = ft.Text("", size=15)
        self.error_message = ft.colors.RED_500

        self.user_name = ft.TextField(label="Zadej uživatelské jméno:")
        self.trida = ft.Dropdown(label="Třída", options=tridy)
        self.password = ft.TextField(label="Zadej heslo:", password=True)
        self.info = ft.Text("Jestli se ty nejde přihlásit, zkus tam dát tečku nebo číslo. ", size=15)

        self.submit1 = ft.ElevatedButton(
            text="Přihlásit se", on_click=lambda e: self.submit_click(page, e)
        )

        self.submit = ft.ElevatedButton(
            text="Ověřit jsi účet", on_click=lambda e: self.show_email_dialog()
        )

        self.email_school = ft.TextField(label="Školní email:")  # Adjust as per flet API
        self.email_personal = ft.TextField(label="Osobní email:")  # Adjust as per flet API
        self.verify_email_button = ft.ElevatedButton(
            text="Poslat kod do emailu", on_click=lambda e: self.verify_email(page)
        )
        self.verification_code_entry = ft.TextField(label="Ověřovací kód:")  # Adjust as per flet API
        self.verify_code_button = ft.ElevatedButton(
            text="Ověřit si kód", on_click=lambda e: self.verify_code()
        )
        self.error_message = ft.Text("", size=10)
        self.verify_code_button_bubble = ft.ElevatedButton(
            text="Zadat ověřovací kód", on_click=lambda e: self.show_verification_code_entry()
        )  # Button for navigating to verification code entry
        self.page = page
        self.verification_code = None
        self.email_dialog = None  # Initialize the email dialog instance
        self.email_sent_to = None  # Store the email address where the code was sent

    def submit_click(self, page, e):
        if (
                not self.user_name.value
                # or not self.email.value
                or not self.password.value
                # or not self.password_confirm.value
                or not self.trida.value
        ):
            self.error_message.value = "Všechny pole musí být vyplněny."
            self.error_message.update()
            return
        # if self.password.value != self.password_confirm.value:
        #   self.error_message.value = "Hesla se neshodují."
        #  self.error_message.update()
        # return
        # if not self.souhlas_pravidla.value:
        # self.error_message.value = "Musíš souhlasit s pravidly."
        # self.error_message.update()
        # return
        if not self.trida.value:
            self.error_message.value = "Musíš zadat třídu!"
            self.error_message.update()
            return
        hashed_password, salt = hash_password(self.password.value)
        cursor.execute(
            "INSERT INTO user (user_name, email, class, password, salt) VALUES (%s, %s, %s, %s, %s)",
            (
                self.user_name.value,
                self.email_sent_to,  # Použijeme email z self.email_sent_to
                self.trida.value,
                hashed_password.decode("utf-8"),
                salt.decode("utf-8"),
            ),
        )
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

            page.pubsub.send_all(
                Message(
                    user_name=user,
                    user_role=role,
                    text=welcome,
                    message_type="login_message",
                    page=page,
                )
            ),
            cursor.execute(
                "SELECT message, user_name, class, role, profile_picture FROM chat join user on user.id = chat.user_id order by chat.id desc limit 10"
            )
            page.update()

        self.error_message.value = "Registrace proběhla úspěšně."
        self.error_message.update()

    def show_email_dialog(self):
        self.page.add(self.error_message)
        self.error_message.value = ""
        if (
                not self.user_name.value
                # or not self.email.value
                or not self.password.value
                # or not self.password_confirm.value
                or not self.trida.value
        ):
            self.error_message.value = "Všechny pole musí být vyplněny!"
            self.error_message.value = ft.colors.RED_500
            self.error_message = ft.colors.RED_500
            self.error_message.update()
            return
        # Create content for the email dialog
        dialog_content = ft.Column([
            self.email_school,
            self.email_personal,
            self.verify_email_button,
            self.error_message,
        ], width=400, height=400)

        # Show the email dialog
        self.email_dialog = ft.AlertDialog(
            open=True,
            modal=True,
            title=ft.Text("Emailová pole"),
            content=dialog_content,
        )
        self.page.dialog = self.email_dialog
        self.page.update()

    def verify_email(self, page):
        self.page.add(self.error_message)  # Add the error message control to the page
        self.error_message.value = ""
        self.error_message.update()

        school_email = self.email_school.value
        personal_email = self.email_personal.value

        if not school_email:
            self.error_message.value = "Školní email musí být vyplněn."
            self.error_message.update()
            print(self.error_message.value)
            return

        if not personal_email:
            personal_email = school_email  # Use school email if personal email is not provided
            self.email_sent_to = school_email
        else:
            self.email_sent_to = personal_email

        # Assuming send_email function and generate_verification_code are defined
        self.verification_code = generate_verification_code()
        email_subject = "Ověřovací kód"
        email_body = f"Váš ověřovací kód je: {self.verification_code}"

        if send_email(personal_email, email_subject, email_body):
            self.show_verification_code_dialog()
            self.show_verification_code_button()
        else:
            self.error_message.value = "Nepodařilo se odeslat ověřovací kód."
            self.error_message.update()

        page.update()

    def show_verification_code_dialog(self):
        dialog_content = ft.Column([
            ft.Text(f"Ověřovací kód byl odeslán na {self.email_sent_to}. Zadejte jej níže:"),
            self.verification_code_entry,
            self.verify_code_button
        ])
        self.page.dialog = ft.AlertDialog(
            open=True,
            modal=True,
            title=ft.Text("Ověřovací kód"),
            content=dialog_content,
        )
        self.page.update()

    def show_verification_code_button(self):
        # Show button for navigating to verification code entry
        self.page.add(self.verify_code_button_bubble)

    def show_verification_code_entry(self):
        self.verify_code_button_bubble.visible = False  # Hide the button after navigating to verification entry
        self.page.dialog = None  # Clear any existing dialog

        # Show verification code entry fields
        self.page.add(self.verification_code_entry)
        self.page.add(self.verify_code_button)

    def verify_code(self):
        self.page.add(self.error_message)
        entered_code = self.verification_code_entry.value

        if entered_code == self.verification_code:
            self.error_message.value = "Ověření účtu proběhlo úspěšně."
            self.error_message.update()
            self.show_pravidla()
        else:
            self.error_message.value = "Nesprávný ověřovací kód. Zkuste to znovu."
            self.error_message.update()

    def show_pravidla(self):
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
            content=ft.Column(
                [
                    ft.Text(pravidla_text),
                    self.submit1,
                ],
                scroll=ft.ScrollMode.AUTO,
            ),
        )
        self.page.update()

    def createForm(self):
        return ft.Column(
            [
                self.user_name,
                self.trida,
                self.password,
                self.submit,
                self.error_message,
            ],
            width=300,
            tight=True,
        )


def generate_verification_code():
    return str(random.randint(100000, 999999))


def send_email(to_email, subject, body):
    from_email = "skolnichat.zib@gmail.com"
    from_password = "vfqf cefz tjuh txor"  # Replace with actual application-specific password

    # Create email
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connect to SMTP server and send email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, from_password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


# ----------------------------------------------------------------------------------------------------------------------------------------------------------------


class MeCommand:
    def __init__(self, page):
        self.page = page


class Message:
    def __init__(
            self,
            user_name: str,
            text: str,
            message_type: str,
            user_role: str | None,
            page,
            user_id=None,
            user_profile_picture: bytes | None = None,
    ):
        self.user_name = user_name
        self.text = text
        self.message_type = message_type
        self.user_role = user_role
        self.user_profile_picture = user_profile_picture
        self.user_id = user_id
        self.page = page


# ----------------------------------------------------------------------------------------------------------------------------------------------------------------


class ChatMessage(ft.Row, str):
    def __init__(self, message: Message):
        super().__init__()
        self.vertical_alignment = "start"
        user_info = message.user_name

        self.message = message
        self.controls = [
            ft.Row(
                controls=[
                    message.user_profile_picture,  # Zobrazit profilovou fotku
                    ft.Column(
                        controls=[
                            ft.Text(message.user_name, weight=ft.FontWeight.BOLD),
                            ft.Text(message.text),
                        ]
                    ),
                ]
            )
        ]

        m = []

        if message.user_name:
            m = [
                ft.Text(message.user_name, weight="bold", color=ft.colors.WHITE),
                ft.Text(message.text, selectable=True, width=message.page.width - 100),
                # self.parse_message_content(message.text),
            ]

        if message.user_role is not None:
            user_info += f" [{message.user_role}]"
            m = [
                ft.Text(user_info, weight="bold", color=ft.colors.YELLOW),
                ft.Text(message.text, selectable=True, width=message.page.width - 100),
                # self.parse_message_content(message.text),
            ]

        avatar_content = ft.Text(self.get_initials(message.user_name))
        avatar_color = ft.colors.WHITE
        avatar_bgcolor = self.get_avatar_color(message.user_name)

        if message.user_profile_picture:
            avatar_content = ft.Image(
                src_base64=message.user_profile_picture.decode("ascii"),
                width=50,
                height=50,
            )
            avatar_bgcolor = ft.colors.TRANSPARENT,

        avatar = ft.CircleAvatar(
            content=avatar_content,
            color=avatar_color,
            bgcolor=avatar_bgcolor,
        )

        avatar_with_click = ft.GestureDetector(  # Zde jsem přidal GestureDetector pro zpracování kliknutí
            content=avatar,
            on_tap=lambda e: self.on_avatar_click(e, message.user_id, )
            # Zde jsem předal message.user_id
        )

        self.controls = [
            avatar_with_click,  # Zde jsem nahradil avatar za avatar_with_click
            ft.Column(
                m,
                tight=True,
                spacing=5,
            ),
        ]

    def on_avatar_click(self, event, user_id, ):
        print("Avatar clicked!")
        # Můžete sem přidat další logiku, například otevření dialogu nebo zobrazení informací o uživateli
        self.execute(event.page, user_id, ),

    def execute(self, page, user_id):
        user_role = page.session.get("user_role")
        # Získání ID aktuálně přihlášeného uživatele

        if user_id is None:
            # Pokud uživatel není přihlášen, vypište chybu
            chat_message = ChatMessage(
                Message(
                    user_name="Zib",
                    text=f"Něco se stalo a není to dobře :( ",
                    message_type="chat_message",
                    user_role="Bot",
                    page=page,
                )
            )
            page.dialog = ft.AlertDialog(
                title=ft.Text("Chyba"),
                content=ft.Text("Něco se stalo a není to dobře :("),
                on_dismiss=lambda e: print("Dialog dismissed")
            )
            page.dialog.open = True
            page.update()
            return

        cursor.execute(
            "SELECT user_name, class, role, id, email, password, created_at, bio FROM user WHERE id = %s LIMIT 1",
            (user_id,),
        )
        result = cursor.fetchone()

        if user_role != None:
            user_text = (f"Uživatel: {result[0]}"
                         f"\nTřída: {result[1]}"
                         f"\n"
                         f"\nRole: {result[2]}\n"
                         f"\n"
                         f"ID: {result[3]}"
                         f"\n"
                         f"\nEmail: {result[4]}"
                         f"\n"
                         f"\nHeslo/Salt: {result[5]} "
                         f"<- (Z toho nemůžeš zjistit heslo. Ani Majitela)"
                         f"\n"
                         f"\nKdy byl vytvořen?: {result[6]}"
                         f"\n"
                         f"\nBio: {result[7]}\n")
            page.dialog = ft.AlertDialog(
                title=ft.Text("Informace o uživateli"),
                content=ft.Column(
                    [
                        ft.Text(user_text),
                        ft.ElevatedButton("Zabanovat", on_click=lambda e: self.show_ban_dialog(e, user_id)),
                        ft.ElevatedButton("Umlčit", on_click=lambda e: self.show_mute_dialog(e, user_id)),
                        ft.ElevatedButton("Varovat", on_click=lambda e: self.show_warn_dialog(e, user_id)),
                        ft.ElevatedButton("Dej roli", on_click=lambda e: self.show_role_dialog(e, user_id)),
                        ft.ElevatedButton("Odstranit roli",
                                          on_click=lambda e: self.show_remove_role_dialog(e, user_id)),
                        # Přidáno tlačítko Odstranit roli
                    ], width=500, height=545
                ),
                on_dismiss=lambda e: print("Dialog dismissed"),
            )
            page.dialog.open = True
            page.update()

        if user_role == None:
            user_text = (f"Uživatel: {result[0]}"
                         f"\nTřída: {result[1]}"
                         f"\n"
                         f"\nRole: {result[2]}\n"
                         f"\n"
                         f"ID: {result[3]}"
                         f"\n"
                         f"\nEmail: {result[4]}"
                         f"\n"
                         f"\nHeslo/Salt: {result[5]} "
                         f"<- (Z toho nemůžeš zjistit heslo. Ani Majitela)"
                         f"\n"
                         f"\nKdy byl vytvořen?: {result[6]}"
                         f"\n"
                         f"\nBio: {result[7]}\n")
            page.dialog = ft.AlertDialog(
                title=ft.Text("Informace o uživateli"),
                content=ft.Column([
                    ft.Text(user_text),
                ], width=450, height=400

                )
            )
            page.dialog.open = True
            page.update()

    def show_role_dialog(self, event, user_id):
        # Vytvoření vstupního pole pro zadání role
        role_field = ft.TextField(label="Role uživatele", hint_text="Zadejte roli")

        def set_role(e):
            role = role_field.value

            cursor.execute(
                "UPDATE user SET role = %s WHERE id = %s",
                (role, user_id)
            )
            mydb.commit()

            e.page.dialog = ft.AlertDialog(
                title=ft.Text("Role přiřazena"),
                content=ft.Text(f"Uživateli {user_id} byla přiřazena role: {role}"),
                on_dismiss=lambda e: print("Dialog dismissed")
            )
            e.page.dialog.open = True
            e.page.update()

        # Vytvoření a otevření dialogu pro zadání role
        event.page.dialog = ft.AlertDialog(
            title=ft.Text("Přiřadit roli uživateli"),
            content=ft.Column([
                role_field,
                ft.ElevatedButton("Odeslat", on_click=set_role),
                ft.Text(
                    f"Je k nabídce přiřadit roli : Admin/ka, Helper, Učitel/ka, Test, Ředitel/ka, Zástupkyně, Assisten/ka")
            ], width=400, height=200),
            on_dismiss=lambda e: print("Role dialog dismissed")
        )
        event.page.dialog.open = True
        event.page.update()

    def show_remove_role_dialog(self, event, user_id, ):
        def close_dialog(event):
            event.page.dialog.open = False
            event.page.update()

        def remove_role(e):
            cursor.execute(
                "UPDATE user SET role = NULL WHERE id = %s",
                (user_id,)
            )
            mydb.commit()

            e.page.dialog = ft.AlertDialog(
                title=ft.Text("Role odstraněna"),
                content=ft.Text("Role byla úspěšně odstraněná."),
                on_dismiss=lambda e: print("Dialog dismissed")
            )
            e.page.dialog.open = True
            e.page.update()

        # Vytvoření a otevření dialogu pro potvrzení odstranění role
        event.page.dialog = ft.AlertDialog(
            title=ft.Text("Odstranit roli uživatele"),
            content=ft.Text("Opravdu chcete odstranit roli tohoto uživatele?"),
            actions=[
                ft.ElevatedButton("Ano", on_click=remove_role),
                ft.ElevatedButton("Ne", on_click=lambda e: close_dialog(e))
            ],
            on_dismiss=lambda e: print("Remove role dialog dismissed")
        )
        event.page.dialog.open = True
        event.page.update()

    def show_mute_dialog(self, event, user_id):
        duration_field = ft.TextField(label="Doba umlčení (minuty)", hint_text="Zadejte dobu v minutách")
        reason_field = ft.TextField(label="Důvod umlčení", hint_text="Zadejte důvod umlčení")

        def mute_user(e):
            duration = duration_field.value
            reason = reason_field.value

            if not duration.isdigit():
                e.page.dialog = ft.AlertDialog(
                    title=ft.Text("Chyba"),
                    content=ft.Text("Neplatná doba umlčení. Zadejte počet minut."),
                    on_dismiss=lambda e: print("Dialog dismissed")
                )
                e.page.dialog.open = True
                e.page.update()
                return

            duration = int(duration)
            mute_end_time = datetime.now() + timedelta(minutes=duration)

            cursor.execute(
                "INSERT INTO muted_users (user_id, mute_end, reason) VALUES (%s, %s, %s)",
                (user_id, mute_end_time, reason)
            )
            mydb.commit()

            e.page.dialog = ft.AlertDialog(
                title=ft.Text("Uživatel umlčen"),
                content=ft.Text(f"Uživatel {user_id} byl umlčen na {duration} minut. Důvod: {reason}"),
                on_dismiss=lambda e: print("Dialog dismissed")
            )
            e.page.dialog.open = True
            e.page.update()

        event.page.dialog = ft.AlertDialog(
            title=ft.Text("Umlčet uživatele"),
            content=ft.Column([
                duration_field,
                reason_field,
                ft.ElevatedButton("Odeslat", on_click=mute_user)
            ], width=400, height=300, ),
            on_dismiss=lambda e: print("Mute dialog dismissed")
        )
        event.page.dialog.open = True
        event.page.update()

    # ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def show_warn_dialog(self, event, user_id):
        # Vytvoření vstupního pole pro zadání důvodu varování
        reason_field = ft.TextField(label="Důvod varování", hint_text="Zadejte důvod varování")

        def warn_user(e):
            reason = reason_field.value

            cursor.execute(
                "INSERT INTO warnings (user_id, warning_date, warned_by, reason) VALUES (%s, NOW(), %s, %s)",
                (user_id, event.page.session.get("user_id"), reason)
            )
            mydb.commit()

            e.page.dialog = ft.AlertDialog(
                title=ft.Text("Uživatel varován"),
                content=ft.Text(f"Uživatel {user_id} byl varován. Důvod: {reason}"),
                on_dismiss=lambda e: print("Dialog dismissed")
            )
            e.page.dialog.open = True
            e.page.update()

        # Vytvoření a otevření dialogu pro zadání důvodu varování
        event.page.dialog = ft.AlertDialog(
            title=ft.Text("Varovat uživatele"),
            content=ft.Column([
                reason_field,
                ft.ElevatedButton("Odeslat", on_click=warn_user)
            ], width=400, height=200),
            on_dismiss=lambda e: print("Warn dialog dismissed")
        )
        event.page.dialog.open = True
        event.page.update()

    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def show_ban_dialog(self, event, user_id):
        # Vytvoření vstupních polí pro dobu a důvod banu
        duration_field = ft.TextField(label="Doba banu (minuty)", hint_text="Zadejte dobu v minutách")
        reason_field = ft.TextField(label="Důvod banu", hint_text="Zadejte důvod banu")
        textskidbi = ft.Text("Když dáte -1. Tak bude nekonečný ban.")

        def ban_user(e):
            duration = duration_field.value
            reason = reason_field.value

            if not duration.isdigit() and duration != "-1":
                e.page.dialog = ft.AlertDialog(
                    title=ft.Text("Chyba"),
                    content=ft.Text("Neplatná doba banu. Zadejte počet minut."),
                    on_dismiss=lambda e: print("Dialog dismissed")
                )
                e.page.dialog.open = True
                e.page.update()
                return

            if duration == '-1':
                ban_end_time = None  # Nekonečný ban
            else:
                duration = int(duration)
                ban_end_time = datetime.now() + timedelta(minutes=duration)

            cursor.execute(
                "INSERT INTO banned_users (user_id, ban_end, reason) VALUES (%s, %s, %s)",
                (user_id, ban_end_time, reason)
            )
            mydb.commit()

            e.page.dialog = ft.AlertDialog(
                title=ft.Text("Uživatel zabanován"),
                content=ft.Text(
                    f"Uživatel {user_id} byl zabanován na {duration} minut. Důvod: {reason}"),
                on_dismiss=lambda e: print("Dialog dismissed")
            )
            e.page.dialog.open = True
            e.page.update()

        # Vytvoření a otevření dialogu pro zadání doby a důvodu banu
        event.page.dialog = ft.AlertDialog(
            title=ft.Text("Zabanovat uživatele"),
            content=ft.Column([
                duration_field,
                reason_field,
                textskidbi,
                ft.ElevatedButton("Odeslat", on_click=ban_user)
            ], width=400, height=300, ),
            on_dismiss=lambda e: print("Ban dialog dismissed")
        )
        event.page.dialog.open = True
        event.page.update()

    # -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def get_initials(self, name: str):
        parts = name.split()
        if len(parts) == 0:
            return ""
        else:
            # Vezměte pouze první písmeno prvního slova
            return parts[0][0].upper()

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


# ----------------------------------------------------------------------------------------------------------------------------------------------------------------


def hash_password(password, salt=None):
    # Hash a password using bcrypt
    if salt is None:
        salt = bcrypt.gensalt()
    else:
        salt = salt.encode("utf-8")

    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password, salt


# ----------------------------------------------------------------------------------------------------------------------------------------------------------------


def _logout(page: ft.Page, chat):
    page.session.clear()
    chat.controls.clear()
    page.dialog.open = True
    page.update()


# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def _login(username: TextField, password: TextField) -> dict:
    response = {"success": False}

    cursor.execute(
        "SELECT * FROM user WHERE user_name = %s OR email = %s LIMIT 1",
        (username.value, username.value),
    )
    result = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    data = [dict(zip(columns, row)) for row in result]

    if data and data[0]:
        user_id = data[0]["id"]

        # Check if user is banned
        banned_end_time = is_ban(user_id)
        if banned_end_time:
            time_remaining = banned_end_time - datetime.now()
            days = time_remaining.days
            hours, remainder = divmod(time_remaining.seconds, 3600)
            minutes = remainder // 60
            response["message"] = f"Jsi zabanovaný z chatu. Zbývá {days} dní, {hours} hodin a {minutes} minut."
            return response

        hashed_password, _ = hash_password(password.value, data[0]["salt"])
        if data[0]["password"] == hashed_password.decode("utf-8"):
            response["success"] = True
            response["user"] = data[0]

            # Přidání uživatele do seznamu přihlášených uživatelů
            online_users.update({data[0]["user_name"]: None})  # Change this line

        else:
            response["message"] = "Špatně jsi zadal heslo"
    else:
        response["message"] = "Špatně jsi zadal jméno"
    return response


# ----------------------------------------------------------------------------------------------------------------------------------------------------------------
def is_ban(user_id):
    try:
        cursor.execute(
            "SELECT ban_end FROM banned_users WHERE user_id = %s", (user_id,)
        )
        result = cursor.fetchone()

        if result:
            banned_end_time = result[0]
            if banned_end_time is None or datetime.now() < banned_end_time:
                return banned_end_time
            else:
                cursor.execute(
                    "DELETE FROM banned_users WHERE user_id = %s", (user_id,)
                )
                mydb.commit()

        return None  # Změněno na None místo False
    except mysql.connector.Error as err:
        print("Error during checking ban status:", err)
        return None  # Změněno na None místo False


# -----------------------

class User:
    def __init__(self, user_name, page=None):
        self.user_name = user_name
        self.page = page

    def __repr__(self):
        return f"User(user_name={self.user_name})"


def main(page: ft.Page, ):
    # global current_page
    # current_page = page

    chat = ft.Column()  # Definujte chat, pokud ještě není definován

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
    recenze = Recenze(page)
    jsem = Jsem(page)
    otazky = Otazky(page)
    nahlaseni = Nahlaseni(page)

    page_map = [
        pravidla,
        novinky,
        podpora,
        nastavení,
        recenze,
        jsem,
        otazky,
        nahlaseni,
    ]
    try:
        page.update()
    except Exception as e:
        print(e)

    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------

    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    online_users = {}

    def join_chat_click(e):
        global incorrect_attempts

        user_id = page.session.get("user_id")
        user_name = page.session.get("user_name")

        if page is not None:
            if isinstance(text_username, ft.TextField):
                page.update()

        if user_id:
            update_ui_for_mute_status(user_id)

        if not text_username.value or not text_password.value:
            error_message = "Zadej uživatelské jméno."
            text_password.error_text = "Zadej heslo."
            text_username.error_text = error_message
            text_password.error_text = text_password.error_text
            text_username.update()
            text_password.update()

            incorrect_attempts += 1
            if incorrect_attempts >= 2:
                add_forgot_details_button()
            return

        login = _login(text_username, text_password)
        text_password.value = ""
        text_password.update()

        if not login["success"]:
            error_message = login.get("message", "An unknown error occurred.")
            text_username.error_text = error_message
            text_username.update()

            incorrect_attempts += 1
            if incorrect_attempts >= 2:
                add_forgot_details_button()
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

            add_user_to_online(login["user"]["id"], user)

            page.dialog.open = False
            new_message.prefix = ft.Text(f"{user} : ")

            page.pubsub.send_all(
                Message(
                    user_name=user,
                    text=f"{user} se připojil do chatu. Připoj se k pobavení!",
                    message_type="login_message",
                    user_role=None,
                    page=page,
                    user_profile_picture=profile_picture_url,
                )
            )

            weather_response = get_weather("Písek")
            message = Message(
                user_name="Zib",
                text=weather_response,
                message_type="chat_message",
                user_role="Bot",
                page=page,
            )
            chat_message = ChatMessage(message)
            chat.controls.append(chat_message)

            cursor.execute(
                "SELECT message, user_name, user_id, class, role, profile_picture FROM chat JOIN user ON user.id = chat.user_id ORDER BY chat.id DESC LIMIT 10"
            )
            result = cursor.fetchall()
            columns = [column[0] for column in cursor.description]

            if result:
                for row in result:
                    data = dict(zip(columns, row))
                    user_name = data["user_name"]
                    user_class = data.get("class", "")
                    user_role = data.get("role", "")

                    if data["profile_picture"]:
                        message = Message(
                            user_name=f"{user_name} {user_class}",
                            user_id=data["user_id"],
                            text=data["message"],
                            message_type="chat_message",
                            user_role=user_role,
                            page=page,
                            user_profile_picture=data["profile_picture"],
                        )
                        chat_message = ChatMessage(message)
                        chat.controls.append(chat_message)

                    else:
                        message = Message(
                            user_name=f"{user_name} {user_class}",
                            user_id=data["user_id"],
                            text=data["message"],
                            message_type="chat_message",
                            user_role=user_role,
                            page=page,
                        )
                        chat_message = ChatMessage(message)
                        chat.controls.append(chat_message)

            update_message_count(user_id)
            login_user(user_id)
            page.update()

            # Zpracování soukromé zprávy
            private_message = page.session.get("private_message")
            if private_message:
                receiver = private_message["receiver"]
                text = private_message["text"]

                online_users = [user[1] for user in get_online_users()]  # Získání seznamu online uživatelů z DB
                if receiver in online_users:
                    receiver_page = next(user[1] for user in get_online_users() if user[1] == receiver)
                    private_message_text = f"Soukromá zpráva od '{user}': {text}"
                    message_obj = Message(
                        user_name=user,
                        text=private_message_text,
                        message_type="private_message",
                        user_role=None,
                        page=receiver_page,
                    )
                    chat_message = ChatMessage(message_obj)
                    receiver_page.controls.append(chat_message)
                    receiver_page.update()

                    print(f"Soukromá zpráva poslána uživateli {receiver}")
                else:
                    print(f"Uživatel {receiver} není online. Zpráva bude odeslána na e-mail.")
                    send_email_to_offline_user(user, receiver, text)

                page.session.set("private_message", None)
            page.update()

    def add_forgot_details_button():
        if "forgot_details_button" not in [action.key for action in page.dialog.actions]:
            page.dialog.actions.append(
                ft.ElevatedButton(
                    key="forgot_details_button",
                    text="Zapomenuté údaje?",
                    on_click=clear_error_and_retry
                )
            )
            page.dialog.update()

    def generate_verification_code():
        return str(random.randint(100000, 999999))

    def send_email(to_email, subject, body):
        from_email = "skolnichat.zib@gmail.com"
        from_password = "vfqf cefz tjuh txor"  # Replace with actual application-specific password

        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(from_email, from_password)
            text = msg.as_string()
            server.sendmail(from_email, to_email, text)
            server.quit()
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False

    def zpatky(page, chat):
        # Function to navigate back to chat
        page.go(chat)

    def clear_error_and_retry(e):
        email_input = ft.TextField(label="Váš email:")
        verify_email_button = ft.ElevatedButton(
            text="Ověřit si email", on_click=lambda e: verify_email(page, email_input)
        )
        error_dialog = ft.AlertDialog(
            open=True,
            modal=True,
            title=ft.Text("Zapomenuté heslo/uživ. jméno"),
            content=ft.Column(
                [
                    ft.Text("Zadejte svůj email pro ověření:"),
                    email_input,
                    verify_email_button,
                    ft.Text("", key="error_message", color="red")  # Placeholder for error message
                ],
                width=300,
                tight=True,
            ),
        )
        page.dialog = error_dialog
        page.update()

    def verify_email(page, email_input):
        global verification_code, email_sent_to

        email_sent_to = email_input.value
        if not email_sent_to:
            show_error_message(page, "Email musí být vyplněn.")
            return

        verification_code = generate_verification_code()
        email_subject = "Ověřovací kód"
        email_body = f"Váš ověřovací kód je: {verification_code}"

        if send_email(email_sent_to, email_subject, email_body):
            show_verification_code_dialog(page)
        else:
            show_error_message(page, "Nepodařilo se odeslat ověřovací kód.")

    def show_verification_code_dialog(page):
        verification_code_entry = ft.TextField(label="Ověřovací kód:")
        verify_code_button = ft.ElevatedButton(
            text="Ověřit kód", on_click=lambda e: verify_code(page, verification_code_entry)
        )
        verification_dialog = ft.AlertDialog(
            open=True,
            modal=True,
            title=ft.Text("Ověřovací kód"),
            content=ft.Column(
                [
                    ft.Text(f"Ověřovací kód byl odeslán na {email_sent_to}. Zadejte jej níže:"),
                    verification_code_entry,
                    verify_code_button,
                    ft.Text("", key="error_message", color="red")  # Placeholder for error message
                ],
                width=300,
                tight=True,
            ),
        )
        page.dialog = verification_dialog
        page.update()

    def verify_code(page, verification_code_entry):
        entered_code = verification_code_entry.value

        if entered_code == verification_code:
            show_new_password_dialog(page)
        else:
            show_error_message(page, "Nesprávný ověřovací kód. Zkuste to znovu.")

    def show_new_password_dialog(page):
        new_password_entry = ft.TextField(label="Nové heslo:", password=True)
        confirm_new_password_entry = ft.TextField(label="Potvrďte nové heslo:", password=True)
        set_password_button = ft.ElevatedButton(
            text="Nastavit nové heslo",
            on_click=lambda e: set_new_password(page, new_password_entry, confirm_new_password_entry)
        )
        new_password_dialog = ft.AlertDialog(
            open=True,
            modal=True,
            title=ft.Text("Nastavit nové heslo"),
            content=ft.Column(
                [
                    new_password_entry,
                    confirm_new_password_entry,
                    set_password_button,
                    show_error_message,
                    show_success_message,
                ],
                width=300,
                tight=True,
            ),
        )
        page.dialog = new_password_dialog
        page.update()

    def set_new_password(page, new_password_entry, confirm_new_password_entry):
        new_password = new_password_entry.value
        confirm_new_password = confirm_new_password_entry.value

        if not new_password or not confirm_new_password:
            show_error_message(page, "Všechna pole musí být vyplněna.")

            return

        if new_password != confirm_new_password:
            show_error_message(page, "Hesla se neshodují.")

            return

        cursor.execute("SELECT id FROM user WHERE email = %s", (email_sent_to,))
        result = cursor.fetchone()
        if result:
            user_id = result[0]
            hashed_password, salt = hash_password(new_password)
            cursor.execute(
                "UPDATE user SET password = %s, salt = %s WHERE id = %s",
                (hashed_password.decode("utf-8"), salt.decode("utf-8"), user_id)
            )
            mydb.commit()
            show_success_message(page, "Heslo bylo úspěšně změněno.")

        else:
            show_error_message(page, "Nepodařilo se najít uživatele s tímto emailem.")

    def show_error_message(page, message):
        error_message = ft.Text(value=message, color="red")
        page.add(error_message)
        page.update()

    def show_success_message(page, message):
        success_message = ft.Text(value=message, color="green")
        page.add(success_message)
        page.update()

    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
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

    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------

    def soukromy_send_email(to_email, subject, body):
        from_email = "skolnichat.zib@gmail.com"
        from_password = "vfqf cefz tjuh txor"  # Replace with actual application-specific password

        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(from_email, from_password)
            text = msg.as_string()
            server.sendmail(from_email, to_email, text)
            server.quit()
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False

    class User:
        def __init__(self, name):
            self.name = name
            self.page = None

        def set_page(self, page):
            self.page = page

        def send_message(self, sender, message):
            if self.page:
                bot_message = f"Uživatel '{sender}' ti poslal zprávu! : {message}"
                self.page.controls.append(
                    ChatMessage(
                        Message(
                            user_name="Zib",
                            text=bot_message,
                            message_type="chat_message",
                            user_role="Bot",
                            page=self.page,
                        )
                    )
                )
                self.page.update()
                page.update()

    # Dictionary to hold online users
    online_users = {}

    # Function to get the database connection
    def add_user_to_online(user_id, user_name):
        conn = get_db_connection()
        cursor = conn.cursor()

        # Aktualizace nebo vložení uživatele do tabulky
        cursor.execute("""
            INSERT INTO online_users (user_id, user_name, last_activity)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
            user_name = VALUES(user_name),
            last_activity = VALUES(last_activity);
        """, (user_id, user_name, datetime.now()))

        conn.commit()
        cursor.close()
        conn.close()

    def update_online_status(user_name, is_online, user_id):
        conn = get_db_connection()
        cursor = conn.cursor()

        # Předpokládáme, že máme proměnné `user_id` a `status`
        cursor.execute('''
            INSERT INTO online_users (user_name, is_online, user_id) 
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE is_online = VALUES(is_online);
        ''', (user_name, is_online, user_id))  # Ujistěte se, že máte správně nastavený user_id
        conn.commit()
        conn.close()

    def is_user_online(user_name):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT user_name FROM online_users WHERE user_name = %s', (user_name,))
        result = cursor.fetchone()
        conn.close()
        return result is not None

    def get_online_users():
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT user_id, user_name FROM online_users")
        users = cursor.fetchall()
        cursor.close()
        conn.close()

        return users

    def check_for_new_messages(page, user_name):
        def task():
            while True:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('SELECT sender, message FROM chat WHERE receiver = %s', (user_name,))
                messages = cursor.fetchall()
                conn.close()

                if messages:
                    for sender, message in messages:
                        bot_message = f"Uživatel '{sender}' ti poslal zprávu: {message}"
                        message_obj = Message(
                            user_name="Zib",
                            text=bot_message,
                            message_type="chat_message",
                            user_role="Bot",
                            page=page,
                        )
                        chat_message = ChatMessage(message_obj)
                        chat.controls.append(chat_message)
                        page.update()
                    # Odstranění zpráv z databáze po jejich zobrazení
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute('DELETE FROM chat WHERE receiver = %s', (user_name,))
                    conn.commit()
                    conn.close()

                time.sleep(10)  # Kontrolujte nové zprávy každých 10 sekund

        threading.Thread(target=task, daemon=True).start()

    def remove_inactive_users():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM online_users
            WHERE TIMESTAMPDIFF(MINUTE, last_activity, NOW()) > %s
        """, (15,))  # Odstranit uživatele, kteří byli neaktivní více než 15 minut
        conn.commit()
        cursor.close()
        conn.close()

    # def print_online_users():
    #     print("Online uživatelé:")
    #     for user_name, user in online_users.items():
    #         print(f"{user_name} - {user}")

    # def login_user(user_name, page):
    #     # Funkce pro přihlášení uživatele
    #     online_users[user_name] = User(user_name, page)
    #     update_online_users_text(page)

    # def logout_user(user_name):
    #     if user_name in online_users:
    #         del online_users[user_name]
    #         update_online_users_text(page)

    def update_online_users_text(page):
        online_user_names = ", ".join(online_users.keys())
        # Předpokládáme, že máte nějaký widget nebo textové pole pro zobrazení online uživatelů
        online_users_text = ft.Text(f"Online uživatelé: {online_user_names}")
        # Předpokládejme, že máte panel, kde zobrazuje seznam online uživatelů
        page.controls.append(online_users_text)
        page.update()

    def get_db_connection():
        return mysql.connector.connect(
            host=os.environ.get("DB_HOST"),
            port=os.environ.get("DB_PORT"),
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PASS"),
            database=os.environ.get("DB_NAME"),
            connection_timeout=30,
        )

    def debug_user_state():
        print(f"Current online users: {list(online_users.keys())}")
        for user_name, user in online_users.items():
            print(f"User: {user_name}, Page: {user.page}")

    # Function to send a message
    def send_message(sender, receiver, message, user_id):
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the receiver exists
        cursor.execute('SELECT * FROM user WHERE user_name = %s', (receiver,))
        if cursor.fetchone() is None:
            print(f"Error: User '{receiver}' does not exist.")
            conn.close()
            return

        # Save the message to the database
        cursor.execute('INSERT INTO chat (sender, receiver, message, user_id) VALUES (%s, %s, %s, %s)',
                       (sender, receiver, message, user_id))
        conn.commit()

        # Check if the user is online
        if is_user_online(receiver):
            user = online_users.get(receiver)
            if user and user.page:
                print(f"Sending message to user '{receiver}' with page object: {user.page}")
                bot_message = f"Uživatel '{sender}' ti poslal zprávu! : {message}"
                user.page.controls.append(
                    ChatMessage(
                        Message(
                            user_name="Zib",
                            text=bot_message,
                            message_type="chat_message",
                            user_role="Bot",
                            page=user.page,
                        )
                    )
                )
                user.page.update()
            else:
                print(f"Error: User '{receiver}' is online but does not have a valid page object.")
                debug_user_state()
        else:
            # If the user is offline, send an email
            send_email_to_offline_user(sender, receiver, message)

        conn.close()
        print("Message sent successfully.")
        debug_user_state()

    # Function to handle user login
    def get_user_id(user_name):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM user WHERE user_name = %s', (user_name,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    def on_user_login(user_name, user_page):
        # Přidání uživatele do seznamu online uživatelů
        if user_name not in online_users:
            online_users[user_name] = User(user_name)
        user = online_users[user_name]
        user.set_page(user_page)

        # Získání user_id
        user_id = get_user_id(user_name)
        if user_id is None:
            print(f"Error: User '{user_name}' does not have a valid user_id.")
            return

        # Aktualizace online stavu v databázi
        update_online_status(user_name, is_online=True, user_id=user_id)

        # Kontrola zpráv v databázi pro nového uživatele
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT sender, message FROM chat WHERE receiver = %s', (user_name,))
        messages = cursor.fetchall()

        # Odeslání zpráv na chatovou stránku
        for sender, message in messages:
            bot_message = f"Uživatel '{sender}' ti poslal zprávu: {message}"
            message_obj = Message(
                user_name="Zib",
                text=bot_message,
                message_type="chat_message",
                user_role="Bot",
                page=user_page,
            )
            chat_message = ChatMessage(message_obj)
            chat.controls.append(chat_message)
            page.update()

        # Odstranění zpráv z databáze po jejich zobrazení
        cursor.execute('DELETE FROM chat WHERE receiver = %s', (user_name,))
        conn.commit()
        conn.close()

        print(f"User {user_name} logged in and received messages.")

    # Function to get users
    def get_users():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT user_name FROM user')
        users = cursor.fetchall()
        conn.close()
        return [user[0] for user in users]

    # Main function
    def soukromy(e):
        page = e.page
        user_name1 = page.session.get("user_name")
        user_name = user_name1  # Replace with the actual username of the logged-in user

        # Načti uživatele a jejich stránku, ale neaktualizuj online stav
        if user_name not in online_users:
            online_users[user_name] = User(user_name)
        user = online_users[user_name]
        user.set_page(page)

        check_for_new_messages(page, user_name)  # Spuštění kontrolování nových zpráv
        warnk = ("\nTohle je beta verze. Některý věci nebudou fungovat, některý jo."
                 "\nFunguje to tak, že když odeslete zprávu, tak se mu to odešle, aj i na email."
                 "\nBohužel budete si muset zase rozkliknout znovu chat, tak abyste viděli soukromé zprávy. Bude to vyřešeno co nejdříve.")

        page.title = "Soukromý chat"

        # Reference pro textová pole
        recipient_ref = ft.Ref[ft.Dropdown]()
        message_ref = ft.Ref[ft.TextField]()

        # Dialog pro zadání uživatele a zprávy
        private_message_dialog = ft.AlertDialog(
            title=ft.Text("Poslat Soukromý chat"),
            content=ft.Column([
                ft.Dropdown(ref=recipient_ref, label="Pro:", options=[]),
                ft.TextField(label="Zpráva:", ref=message_ref),
                ft.Text(warnk)
            ], width=384, height=300),
            actions=[
                ft.TextButton("Poslat", on_click=lambda e: send_private_message(e, recipient_ref, message_ref, page)),
                ft.TextButton("Zrušit", on_click=lambda e: close_dialog(private_message_dialog, page))
            ]
        )

        # Upozornění na beta verzi
        beta_warning_dialog = ft.AlertDialog(
            title=ft.Text("Beta Version Notice"),
            content=ft.Text(
                "\nSoukromý chat je v beta verzi. "
                "\nNefunguje jak má správně, ale můžete si trošku vyzkoušet alespoň jak bude fungovat "),
            actions=[
                ft.TextButton("Chci si vyzkoušet soukromý chat",
                              on_click=lambda e: open_private_message_dialog(e, page, private_message_dialog)),
                ft.TextButton("Zrušit", on_click=lambda e: close_dialog(beta_warning_dialog, page))
            ]
        )

        # Načtení uživatelů do private_message_dialog
        users = get_users()
        recipient_ref.current.options = [ft.dropdown.Option(user) for user in users]

        # Otevření beta_warning_dialog
        beta_warning_dialog.open = True
        page.dialog = beta_warning_dialog
        page.update()

    def open_private_message_dialog(e, page, private_message_dialog):
        private_message_dialog.open = True
        page.dialog = private_message_dialog
        page.update()

    # Function to send private message

    def send_message_to_online_user(sender, receiver, message_text):
        if receiver in online_users:
            print(f"Receiver '{receiver}' is online.")  # Debugging output
            receiver_page = online_users[receiver].page
            private_message = f"Uživatel '{sender}' ti poslal zprávu: {message_text}"
            message_obj = Message(
                user_name=sender,
                text=private_message,
                message_type="chat_message",
                user_role="User",
                page=receiver_page,
            )
            chat_message = ChatMessage(message_obj)
            receiver_page.controls.append(chat_message)
            receiver_page.update()

            # Optionally, use a dialog to alert the user about the new message
            # This is optional; chat message update should suffice
            alert_dialog = ft.AlertDialog(
                title=ft.Text("Nová zpráva"),
                content=ft.Text(private_message),
                actions=[ft.TextButton("OK", on_click=lambda e: close_dialog(alert_dialog, receiver_page))]
            )
            receiver_page.dialog = alert_dialog
            receiver_page.update()

            return True
        else:
            print(f"Receiver '{receiver}' is not online.")  # Debugging output
        return False

    page.update()

    def send_email_to_offline_user(sender, receiver, message_text):
        conn = get_db_connection()
        cursor = conn.cursor()

        receiver_email = page.session.get(f"{receiver}_email")
        if not receiver_email:
            cursor.execute('SELECT email FROM user WHERE user_name = %s', (receiver,))
            result = cursor.fetchone()
            if result:
                receiver_email = result[0]

        if receiver_email:
            subject = f"Nová soukromá zpráva od uživatele '{sender}'"
            body = f"Ahoj {receiver},\n\nUživatel '{sender}' ti poslal novou soukromou zprávu: {message_text}\n\nPřihlaš se do chatu, abys odpověděl.\n\nS pozdravem,\nZib"
            if soukromy_send_email(receiver_email, subject, body):
                print(f"Email sent to {receiver} at {receiver_email}")
            else:
                print(f"Failed to send email to {receiver} at {receiver_email}")
        else:
            print(f"No email found for user '{receiver}'")

        conn.close()
        page.update()

    def send_private_message(e, recipient_ref, message_ref, page):
        sender = page.session.get("user_name")
        receiver = recipient_ref.current.value
        message_text = message_ref.current.value

        # Uložení zprávy do databáze
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO chat (sender, receiver, message) VALUES (%s, %s, %s)',
                       (sender, receiver, message_text))
        conn.commit()

        # Zkontrolujte, zda je příjemce online
        if not send_message_to_online_user(sender, receiver, message_text):
            # Pokud není online, odešlete e-mail
            send_email_to_offline_user(sender, receiver, message_text)

        conn.close()
        print(f"Message processed for user {receiver}.")
        page.update()

    # Function to close the dialog
    def close_dialog(dialog, page):
        dialog.open = False
        page.update()

    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def zpatky(page, chat):
        webbrowser.open_new_tab("voku-skolni-chat.fly.dev")

    # ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    FILES_FOLDER = "files"
    if not os.path.exists(FILES_FOLDER):
        os.makedirs(FILES_FOLDER)

    def beta_pick_files():
        beta_warning_dialog = ft.AlertDialog(
            title=ft.Text("Beta Version Notice"),
            content=ft.Text(
                "\nVybírání soubory je ještě v bete. "
                "\nNefunguje jak má správně, ale můžete si trošku vyzkoušet alespoň jak bude fungovat "),
            actions=[
                ft.TextButton("Chci si vyzkoušet vybírání souboru",
                              on_click=lambda e: pick_files_result(e)),
                ft.TextButton("Zrušit", on_click=lambda e: close_dialog(beta_warning_dialog, page))
            ]
        )

    def pick_files_result(e: ft.FilePickerResultEvent):
        page = e.page  # Get the page instance from the event

        if e.files:
            selected_file = e.files[0]
            file_extension = os.path.splitext(selected_file.name)[1].lower()

            # Check if the file extension is one of the allowed image types
            if file_extension not in [".png", ".jpg", ".jpeg"]:
                pick_files_dialog.value = "Vyberte prosím soubor typu PNG, JPG nebo JPEG!"
                pick_files_dialog.update()
                return

            # Ensure that selected_file.path is not None and is a valid file path
            if selected_file.path:
                file_path = selected_file.path

                if not os.path.isfile(file_path):
                    pick_files_dialog.value = "Soubor neexistuje!"
                    pick_files_dialog.update()
                    return

                # Save the file to the files folder
                file_save_path = os.path.join(FILES_FOLDER, selected_file.name)
                with open(file_path, "rb") as src_file:
                    file_content = src_file.read()
                    with open(file_save_path, "wb") as dest_file:
                        dest_file.write(file_content)

                pick_files_dialog.value = f"Vybraný soubor: {selected_file.name} byl úspěšně uložen."
            else:
                pick_files_dialog.value = "Není vybrán žádný soubor!"
                pick_files_dialog.update()
        else:
            pick_files_dialog.value = "Zrušeno!"

        pick_files_dialog.update()
        page.update()

    pick_files_dialog = ft.FilePicker(on_result=pick_files_result)
    page.overlay.append(pick_files_dialog)

    # -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

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

    def update_ui_for_ban_status(user_id):
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

    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------

    def show_messages(message, page):
        # Rozdělení textu na části, aby se zkontrolovalo, zda je uveden uživatel
        parts = message.text.split(" ", 1)  # Rozdělení na příkaz a případný zbytek

        if len(parts) == 1:
            cursor.execute(
                "SELECT message, user_id FROM chat ORDER BY id DESC LIMIT 100"
            )
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
            user_id = page.session.get('user_id')

            cursor.execute(
                "INSERT INTO zib (user_id, message, created_at) VALUES (%s, %s, NOW())",
                (user_id, all_messages_text)
            )


        elif (
                len(parts) == 2
        ):  # Pokud je zadán identifikátor (uživatelské jméno nebo ID)
            user_identifier = parts[1].strip()  # Získat jméno nebo ID

            if user_identifier.isdigit():
                # Dotaz na zprávy podle uživatelského ID
                cursor.execute(
                    "SELECT message FROM chat WHERE user_id = %s ORDER BY id",
                    (int(user_identifier),),
                )
            else:
                # Dotaz na zprávy podle uživatelského jména
                cursor.execute(
                    "SELECT message FROM chat WHERE user_id = (SELECT id FROM user WHERE user_name = %s) ORDER BY id",
                    (user_identifier,),
                )

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
            user_id = page.session.get('user_id')

            cursor.execute(
                "INSERT INTO zib (user_id, message, created_at) VALUES (%s, %s, NOW())",
                (user_id, user_messages)
            )

        page.update()

    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------

    def show_all_users(message, page):
        # Přečtěte uživatele z databáze
        cursor.execute(
            "SELECT user_name, class, role, id FROM user ORDER BY id DESC LIMIT 1000 "
        )
        result = cursor.fetchall()
        # Zformátujte seznam uživatelů
        users_text = "Všechny uživatele:\n"
        for row in result:
            users_text += (
                f"{row[0]} (Třída: {row[1]}, Role: {row[2]}, Id : {row[3]} )\n"
            )
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
        user_id = page.session.get('user_id')

        cursor.execute(
            "INSERT INTO zib (user_id, message, created_at) VALUES (%s, %s, NOW())",
            (user_id, users_text)
        )
        page.update()

    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------

    def show_user_details(message, page):
        parts = message.text.split(" ")
        if len(parts) < 2:
            # Pokud je formát špatný, zobrazte zprávu o chybě
            chat.controls.append(
                ChatMessage(
                    Message(
                        user_name="Zib",
                        text=test4,
                        message_type="chat_message",
                        user_role="Bot",
                        page=page,
                    )
                )
            )
            user_id = page.session.get('user_id')
            test4 = "Musíte zadat jméno uživatele nebo ID! Např. '!users Vojta' nebo '!users 123'."

            cursor.execute(
                "INSERT INTO zib (user_id, message, created_at) VALUES (%s, %s, NOW())",
                (user_id, test4)
            )

            page.update()
            return

        user_identifier = parts[1].strip()
        if user_identifier.isdigit():
            cursor.execute(
                "SELECT user_name, class, role, id, email, created_at FROM user WHERE id = %s LIMIT 1",
                (user_identifier,),
            )
        else:
            cursor.execute(
                "SELECT user_name, class, role, id, email, created_at FROM user WHERE user_name = %s LIMIT 1",
                (user_identifier,),
            )

        result = cursor.fetchone()

        if result:
            user_text = f"Uživatel: {result[0]}\nTřída: {result[1]}\nRole: {result[2]}\nID: {result[3]}\nEmail: {result[4]}\nKdy byl vytvořen?: {result[5]}\n"
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

        user_id = page.session.get('user_id')

        cursor.execute(
            "INSERT INTO zib (user_id, message, created_at) VALUES (%s, %s, NOW())",
            (user_id, user_text)
        )

        page.update()
        command_list["!message"] = show_messages

    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------

    def handle_calculator(
            message: Message,
            page: ft.Page,
    ):
        calculator_text = "Tohle je kalkulačka. Zatím není podporované více příkladu např : 5+5 a víc už ne .Podporované operátory jsou: +, -, *, /, %.\n"

        # Přidat pak tak aby mohl člověk psát více toho než jenom : 5+5. Např : 5+5+5+5+5+5.

        try:
            parts = re.split(r"(\d+\s*[+-/*%]\s*\d+)", message.text)
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
        user_id = page.session.get('user_id')

        cursor.execute(
            "INSERT INTO zib (user_id, message, created_at) VALUES (%s, %s, NOW())",
            (user_id, calculator_text)
        )
        mydb.commit()

        chat_message = ChatMessage(message)
        chat.controls.append(chat_message)

    # --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def handle_help(message: Message, page: ft.Page, ):
        help_text = "Ahoj, já jsem Zib! Jsem robot a dělám to abych jsem ti pomohl. Dostupné příkazy jsou:\n"
        help_text += "- !Help : Zobrazí tuhle zprávu \n"
        help_text += "- !cl [Příklad] [Příklad] : cl je kalkulačka. \n"
        help_text += "- !s [Cokoliv] : !s stojí za 'Search', neboli vyhledávat, umožní vám to vyhledat cokoliv aniž byste otevřeli nějakou kartu\n"
        help_text += "- !m [Cokoliv] : Tenhle příkaz funguje tak že vyhledáš všechny zprávy ohledně tý zprávy\n"
        help_text += "- !we [Město/Vesnice] : Tenhle příkaz funguje tak, že dáš !we Písek. A napíše ty všechno ohledně Písku\n"
        help_text += "- Majitel je Vojtěch Kurinec. Jeho nick je Vojta 6.B [Majitel].\n"
        help_text += "- Ban můžeš získat, můžeš získat 2 tipy banu, nekoneční nebo na nějakou dobu, stejně jako mute!\n"
        help_text += "- Když tak, když klikneš na ty 3 čáry nahoře, tak to je menu, a uvidíš co je tam! .\n"
        help_text += "- Roli získáš nějak, role jsou zde důležitý, tak aby se zde nezfalšovalo kdo je co. Role jsou zatím jenom : Majitel, Admin, Žák/Žákyně (Tu roli žádnou nemá), Učitel. Samozřejmě že se budou přidávat.\n"
        help_text += "- Dodržuj pravidla, tak abys jsi nedostal ban, mute, nebo varování! Jestli máš nějaké otázky, ptej se Majitele.\n"

        if message.user_role in full_permissions:
            help_text += "\n"
            help_text += "\n"
            help_text += "- Další pokročilé příkazy, které jsou dostupné pouze pro Majitele, Adminy a Učitelé a Ředitele.\n"
            help_text += "-!users [ID (Číslo)/Name (Jméno)] : Zobrazí všechny uživatele. [ID/Name] není povinný, ale když to dáte, všechny jeho věci co známe se zobrazí\n"
            help_text += "-!message [ID (ČÍslo)/Name (Jméno)] : Zobrazí všechny zprávy od uživatele. [ID/Name] není povinný, ale když to dáte, všechny jeho zprávy co známe se zobrazí\n"
            help_text += "-!mute [ID (Číslo)] [Doba] [Důvod] : Umlčí uživatele. [ID] a [Doba] je důležitá! Doba jsou na minuty a Uživatel je přes ID a Důvod není povinný, ale bylo by to dobrý, Vypíše se to do databáze\n"
            help_text += "-!user_mute : Uvidíš jestli je někdo umlčenej\n"
            help_text += "-!unmute [User_ID] : Ztratí se mu umlčení\n"
            help_text += "-!warn [Name (Jméno)] : Varovaní pro toho uživatele. Vypíše se to do databáze\n"
            help_text += "-!user_warm : Zjistíš jestli má někdo varovaní\n"
            help_text += "-!unwarn [User_ID] : Ztratí se mu varovaní\n"
            help_text += "-!ban [User_ID] [Doba (-1 = nekonečno)] [Důvod] : !ban funguje jako mute, ale když se odpojí od školního chatu, tak se nebude moct přihlásit, ani zaregistrovat. Když dáš -1, znamenáto že se nikdy nebude moct přihlásit, pokud já jako Majitel neodstraní mu z databáze ten čas. \n"
            help_text += "-!user_ban : Uvidíš jaký uživatel má ban, nebo ne\n"
            help_text += "-!unban [User_ID] : Ztratí se mu ban\n"

        message = Message(
            user_name="Zib",
            text=help_text,
            message_type="chat_message",
            user_role="Bot",
            page=page,
        )
        user_id = page.session.get('user_id')

        # Přidání zprávy bota do tabulky `zib`
        cursor.execute(
            "INSERT INTO zib (user_id, message, created_at) VALUES (%s, %s, NOW())",
            (user_id, help_text)
        )
        mydb.commit()

        chat_message = ChatMessage(message)
        chat.controls.append(chat_message)

    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------

    def is_muted(user_id):
        try:
            cursor.execute(
                "SELECT mute_end FROM muted_users WHERE user_id = %s", (user_id,)
            )
            result = cursor.fetchone()

            # Ujistěte se, že jste dokončili čtení všech výsledků
            cursor.fetchall()  # Nebo cursor.reset()

            if result:
                mute_end_time = result[0]
                if datetime.now() < mute_end_time:
                    return True
                else:
                    cursor.execute(
                        "DELETE FROM muted_users WHERE user_id = %s", (user_id,)
                    )
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
            cursor.execute(
                "INSERT INTO muted_users (user_id, mute_end) VALUES (%s, %s)",
                (user_id, mute_end_time),
            )
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
                reason = (
                    " ".join(parts[3:]) if len(parts) > 3 else ""
                )  # Získání důvodu umlčení
                print(
                    f"Muting user {user_id} for {duration_minutes} minutes with reason: {reason}"
                )
                mute_user(user_id, duration_minutes, reason)

                # Notify the Chat
                if page is not None and hasattr(page, 'pubsub'):
                    page.pubsub.send_all(
                        Message(
                            user_name="Zib",
                            user_role="Bot",
                            text=f"Uživatel s ID : {user_id} byl umlčen na {duration_minutes} minut. Důvod: {reason}",
                            message_type="system",
                            page=page,
                        )
                    )
                else:
                    print("Error: Current page does not have pubsub attribute.")

            except ValueError:
                chat.controls.append(
                    ChatMessage(
                        Message(
                            user_name="Zib",
                            text="Neplatné ID uživatele nebo délka umlčení. Použijte správný formát !Mute <User_ID> <Duration_in_minutes> [<Reason>].",
                            message_type="chat_message",
                            user_role="Bot",
                            page=page,
                        )
                    )
                )

        else:
            message = Message(
                user_name="Zib",
                text="Neplatný příkaz! Použijte formát !Mute <User_ID> <Duration_in_minutes> [<Reason>].",
                message_type="chat_message",
                user_role="Bot",
                page=page,
            )

            mydb.commit()
            chat_message = ChatMessage(message)
            chat.controls.append(chat_message)
        page.update()

    def show_all_mute_user(message, page):
        # Přečtěte uživatele z databáze
        cursor.execute(
            "SELECT user_id, muted_by, mute_start, mute_end, reason FROM muted_users ORDER BY id DESC LIMIT 1000 "
        )
        result = cursor.fetchall()
        # Zformátujte seznam uživatelů
        users_text = "Všechny zabanované uživatele:\n"
        for row in result:
            users_text += (
                f"ID : {row[0]} Od koho: {row[1]}, Kdy začal: {row[2]}, Kdy skončil: {row[3]}, Proč : {row[4]} \n"
            )
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
        user_id = page.session.get('user_id')

        cursor.execute(
            "INSERT INTO zib (user_id, message, created_at) VALUES (%s, %s, NOW())",
            (user_id, users_text)
        )
        page.update()

    def handle_unmute_command(message, page):
        parts = message.text.split(" ")

        if len(parts) >= 2:  # Zkontroluje, zda bylo zadáno ID uživatele
            try:
                user_id = int(parts[1].strip())

                # Odstranění uživatele z tabulky banned_users
                cursor.execute("DELETE FROM muted_users WHERE user_id = %s", (user_id,))
                mydb.commit()

                # Notify the Chat
                if page is not None and hasattr(page, 'pubsub'):
                    page.pubsub.send_all(
                        Message(
                            user_name="Zib",
                            user_role="Bot",
                            text=f"Uživatel s ID : {user_id} byl odmlčen.",
                            message_type="system",
                            page=page,
                        )
                    )
                else:
                    print("Error: Current page does not have pubsub attribute.")

            except ValueError:
                chat.controls.append(
                    ChatMessage(
                        Message(
                            user_name="Zib",
                            text="Neplatné ID uživatele. Použijte správný formát !unmute <User_ID>.",
                            message_type="chat_message",
                            user_role="Bot",
                            page=page,
                        )
                    )
                )
                page.update()
        else:
            message = Message(
                user_name="Zib",
                text="Neplatný příkaz! Použijte formát !unmute <User_ID>.",
                message_type="chat_message",
                user_role="Bot",
                page=page,
            )

            chat_message = ChatMessage(message)
            chat.controls.append(chat_message)
        page.update()

    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------

    def handle_warn_command(message, page):
        parts = message.text.split(" ", 1)

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
        cursor.execute(
            "SELECT id, user_name FROM user WHERE user_name = %s LIMIT 1", (user_name,)
        )
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
        cursor.execute(
            "INSERT INTO warnings (user_id, warning_date, warned_by) VALUES (%s, NOW(), %s)",
            (user_id, page.session.get("user_id")),
        )
        mydb.commit()

        if page is not None and hasattr(page, 'pubsub'):
            page.pubsub.send_all(
                Message(
                    user_name="Zib",
                    user_role="Bot",
                    text=f"Uživatel {user_name} byl varován",
                    message_type="system",
                    page=page,
                )
            )
        else:
            print("Error: Current page does not have pubsub attribute.")
        page.update()

    def show_all_warn_user(message, page):
        # Přečtěte uživatele z databáze
        cursor.execute(
            "SELECT user_id, warned_by, warning_date, reason FROM warnings ORDER BY id DESC LIMIT 1000 "
        )
        result = cursor.fetchall()
        # Zformátujte seznam uživatelů
        users_text = "Všechny zabanované uživatele:\n"
        for row in result:
            users_text += (
                f"ID : {row[0]} Od koho: {row[1]}, Kdy začal: {row[2]}, Proč : {row[3]} \n"
            )
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
        user_id = page.session.get('user_id')

        cursor.execute(
            "INSERT INTO zib (user_id, message, created_at) VALUES (%s, %s, NOW())",
            (user_id, users_text)
        )
        page.update()

    def handle_unwarn_command(message, page):
        parts = message.text.split(" ")

        if len(parts) >= 2:  # Zkontroluje, zda bylo zadáno ID uživatele
            try:
                user_id = int(parts[1].strip())

                # Odstranění uživatele z tabulky banned_users
                cursor.execute("DELETE FROM warnings WHERE user_id = %s", (user_id,))
                mydb.commit()

                # Notify the Chat
                if page is not None and hasattr(page, 'pubsub'):
                    page.pubsub.send_all(
                        Message(
                            user_name="Zib",
                            user_role="Bot",
                            text=f"Uživatel s ID : {user_id} bylo zrušeno varováni.",
                            message_type="system",
                            page=page,
                        )
                    )
                else:
                    print("Error: Current page does not have pubsub attribute.")

            except ValueError:
                chat.controls.append(
                    ChatMessage(
                        Message(
                            user_name="Zib",
                            text="Neplatné ID uživatele. Použijte správný formát !unwarn <User_ID>.",
                            message_type="chat_message",
                            user_role="Bot",
                            page=page,
                        )
                    )
                )
                page.update()
        else:
            message = Message(
                user_name="Zib",
                text="Neplatný příkaz! Použijte formát !unwarn <User_ID>.",
                message_type="chat_message",
                user_role="Bot",
                page=page,
            )

            chat_message = ChatMessage(message)
            chat.controls.append(chat_message)
        page.update()

    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
    def is_ban(user_id):
        try:
            cursor.execute(
                "SELECT ban_end FROM banned_users WHERE user_id = %s", (user_id,)
            )
            result = cursor.fetchone()

            if result:
                banned_end_time = result[0]
                if banned_end_time is None or datetime.now() < banned_end_time:
                    return True
                else:
                    cursor.execute(
                        "DELETE FROM banned_users WHERE user_id = %s", (user_id,)
                    )
                    mydb.commit()

            return False
        except mysql.connector.Error as err:
            print("Error during checking ban status:", err)
            return False

    def ban_user(user_id, duration_minutes, reason=""):
        try:
            if duration_minutes == -1:
                banned_end_time = None  # Nekonečný ban
            else:
                banned_end_time = datetime.now() + timedelta(minutes=duration_minutes)

            print(f"{user_id} {banned_end_time}")
            cursor.execute(
                "INSERT INTO banned_users (user_id, ban_end) VALUES (%s, %s)",
                (user_id, banned_end_time),
            )
            mydb.commit()
            print(f"Uživatel {user_id} byl zabanován na {duration_minutes} minut.")

        except mysql.connector.Error as err:
            print("Chyba při banování uživatele:", err)

    def handle_ban_command(message, page):
        parts = message.text.split(" ")

        if len(parts) >= 2:  # Zkontroluje, zda jsou zadané alespoň ID uživatele a délka
            try:
                user_id = int(parts[1].strip())
                if len(parts) == 2:
                    duration_minutes = -1  # Nekonečný ban, pokud není uvedena délka
                    reason = ""
                else:
                    duration_minutes = int(parts[2].strip())
                    reason = (
                        " ".join(parts[3:]) if len(parts) > 3 else ""
                    )  # Získání důvodu banování

                print(
                    f"Ban user {user_id} for {duration_minutes} minutes with reason: {reason}"
                )
                ban_user(user_id, duration_minutes, reason)

                # Notify the Chat
                if page is not None and hasattr(page, 'pubsub'):
                    page.pubsub.send_all(
                        Message(
                            user_name="Zib",
                            user_role="Bot",
                            text=f"Uživatel s ID : {user_id} byl zabanován na {duration_minutes} minut. Důvod: {reason}" if duration_minutes != -1 else f"Uživatel s ID : {user_id} byl zabanován na neomezenou dobu. Důvod: {reason}",
                            message_type="system",
                            page=page,
                        )
                    )
                else:
                    print("Error: Current page does not have pubsub attribute.")

            except ValueError:
                message = Message(
                    user_name="Zib",
                    user_role="Bot",
                    text="Neplatné ID uživatele nebo délka banování. Použijte správný formát !ban <User_ID> <Duration_in_minutes> [<Reason>].",
                    message_type="system",
                    page=page,
                )
                chat_message = ChatMessage(message)
                page.controls.append(chat_message)

        else:
            message = Message(
                user_name="Zib",
                text="Neplatný příkaz! Použijte formát !ban <User_ID> <Duration_in_minutes> [<Reason>].",
                message_type="chat_message",
                user_role="Bot",
                page=page,
            )
            chat_message = ChatMessage(message)
            page.controls.append(chat_message)
        page.update()  # Aktualizace stránky

    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def show_all_ban_user(message, page):
        # Přečtěte uživatele z databáze
        cursor.execute(
            "SELECT user_id, banned_by, ban_start, ban_end, reason FROM banned_users ORDER BY id DESC LIMIT 1000 "
        )
        result = cursor.fetchall()
        # Zformátujte seznam uživatelů
        users_text = "Všechny zabanované uživatele:\n"
        for row in result:
            users_text += (
                f"ID : {row[0]} Od koho: {row[1]}, Kdy začal: {row[2]}, Kdy skončil: {row[3]}, Proč : {row[4]} \n"
            )
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
        user_id = page.session.get('user_id')

        cursor.execute(
            "INSERT INTO zib (user_id, message, created_at) VALUES (%s, %s, NOW())",
            (user_id, users_text)
        )
        page.update()

    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def handle_unban_command(message, page):
        parts = message.text.split(" ")

        if len(parts) >= 2:  # Zkontroluje, zda bylo zadáno ID uživatele
            try:
                user_id = int(parts[1].strip())

                # Odstranění uživatele z tabulky banned_users
                cursor.execute("DELETE FROM banned_users WHERE user_id = %s", (user_id,))
                mydb.commit()

                # Notify the Chat
                if page is not None and hasattr(page, 'pubsub'):
                    page.pubsub.send_all(
                        Message(
                            user_name="Zib",
                            user_role="Bot",
                            text=f"Uživatel s ID : {user_id} byl odbanován.",
                            message_type="system",
                            page=page,
                        )
                    )
                else:
                    print("Error: Current page does not have pubsub attribute.")

            except ValueError:
                chat.controls.append(
                    ChatMessage(
                        Message(
                            user_name="Zib",
                            text="Neplatné ID uživatele. Použijte správný formát !unban <User_ID>.",
                            message_type="chat_message",
                            user_role="Bot",
                            page=page,
                        )
                    )
                )
                page.update()
        else:
            message = Message(
                user_name="Zib",
                text="Neplatný příkaz! Použijte formát !unban <User_ID>.",
                message_type="chat_message",
                user_role="Bot",
                page=page,
            )

            chat_message = ChatMessage(message)
            chat.controls.append(chat_message)
        page.update()

    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def search_command(msg, page):
        if len(msg.text.split()) < 2:
            # Pokud uživatel neposkytl žádné hledané výrazy
            message = Message(
                user_name="Zib",
                text=f"Nebyl zadán žádný hledaný výraz.",
                message_type="chat_message",
                user_role="Bot",
                page=page,
            )
            chat_message = ChatMessage(message)
            chat.controls.append(chat_message)

            return

        # Získání hledaného výrazu ze zprávy
        search_query = " ".join(msg.text.split()[1:])

        # Vytvoření URL pro vyhledávání na webu
        search_url = f"https://www.google.com/search?q={search_query}"

        try:
            webbrowser.open_new_tab(search_url)
            test9 = f"Vyhledávání pro '*{search_query}*' bylo úspěšné! Zde je váš odkaz: '{search_url}'"

            message = Message(
                user_name="Zib",
                text=test9,
                message_type="chat_message",
                user_role="Bot",
                page=page,
            )

            user_id = page.session.get('user_id')

            cursor.execute(
                "INSERT INTO zib (user_id, message, created_at) VALUES (%s, %s, NOW())",
                (user_id, test9)
            )
            mydb.commit()

            chat_message = ChatMessage(message)
            chat.controls.append(chat_message)

        except Exception as e:
            test8 = f"Při vyhledávání pro '{search_query}' došlo k chybě: {str(e)}"

            message = Message(
                user_name="Zib",
                text=test8,
                message_type="chat_message",
                user_role="Bot",
                page=page,
            )

            user_id = page.session.get('user_id')

            cursor.execute(
                "INSERT INTO zib (user_id, message, created_at) VALUES (%s, %s, NOW())",
                (user_id, test8)
            )
            mydb.commit()

            chat_message = ChatMessage(message)
            chat.controls.append(chat_message)

    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------

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

        cursor.execute(
            "SELECT message, user_id FROM chat WHERE message LIKE %s ORDER BY id DESC LIMIT 100",
            ("%" + search_query + "%",),
        )
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

    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
    def get_weather(city):
        # API klíč pro OpenWeatherMap (registrace zdarma)
        api_key = '3a1f746d01fd5e2d1321351e0cd51874'

        # URL pro získání aktuálního počasí (zde je zvolen endpoint pro aktuální počasí)
        url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'

        try:
            # Zasílání požadavku na API
            response = requests.get(url)
            data = response.json()

            # Zpracování odpovědi
            if data['cod'] == 200:
                weather_description = data['weather'][0]['description']
                temperature = data['main']['temp']
                humidity = data['main']['humidity']
                wind_speed = data['wind']['speed']
                return f"Aktuální počasí v {city}: {weather_description}, teplota: {temperature} °C, vlhkost: {humidity} %, rychlost větru: {wind_speed} m/s"
            else:
                return f"Nepodařilo se získat data. Chybový kód: {data['cod']}"
        except Exception as e:
            return f"Chyba při získávání dat: {str(e)}"

    def weather_command(msg, page):
        if len(msg.text.split()) < 2:
            # If the user didn't provide a city
            message = Message(
                user_name="Zib",
                text=f"Prosím, řeknete město/vesnici. Např : !we Písek.",
                message_type="chat_message",
                user_role="Bot",
                page=page,
            )
            chat_message = ChatMessage(message)
            chat.controls.append(chat_message)

            return

        # Get the city from the message
        city = " ".join(msg.text.split()[1:])

        try:
            weather_response = get_weather(city)
            message = Message(
                user_name="Zib",
                text=weather_response,
                message_type="chat_message",
                user_role="Bot",
                page=page,
            )

            user_id = page.session.get('user_id')

            cursor.execute(
                "INSERT INTO zib (user_id, message, created_at) VALUES (%s, %s, NOW())",
                (user_id, weather_response)
            )
            mydb.commit()

            chat_message = ChatMessage(message)
            chat.controls.append(chat_message)

        except Exception as e:
            error_message = f"Error getting weather for '{city}': {str(e)}"

            message = Message(
                user_name="Zib",
                text=error_message,
                message_type="chat_message",
                user_role="Bot",
                page=page,
            )

            user_id = page.session.get('user_id')

            cursor.execute(
                "INSERT INTO zib (user_id, message, created_at) VALUES (%s, %s, NOW())",
                (user_id, error_message)
            )
            mydb.commit()

            chat_message = ChatMessage(message)
            chat.controls.append(chat_message)

    # -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def login_user(user_id):
        cursor.execute("SELECT message_count FROM user WHERE id = %s", (user_id,))
        result = cursor.fetchone()
        if result:
            return result[0]  # Vrátí aktuální počet zpráv uživatele
        else:
            return 0

    def update_message_count(user_id):
        cursor.execute("UPDATE user SET message_count = message_count + 1 WHERE id = %s", (user_id,))
        mydb.commit()

    # --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def on_user_message_submit(e):
        user_message_text = user_message_input.value  # Získání textu zprávy od uživatele
        user_name = page.session.get("user_name")  # Získání jména uživatele ze session
        message = Message(
            user_name=user_name,
            user_id=page.session.get("user_id"),
            text=user_message_text,
            message_type="chat_message",
            user_role="User",
            page=page,
        )
        user_message_input.value = ""  # Vyčištění vstupního pole
        page.update()

    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------

    command_list = {
        "!help": handle_help,
        "!mute": handle_mute_command,
        "!message": show_messages,
        "!users": lambda msg, pg: (
            show_all_users(msg, pg)
            if len(msg.text.split()) == 1
            else show_user_details(msg, pg)
        ),
        "!warn": handle_warn_command,
        "!cl": handle_calculator,
        "!s": search_command,
        "!m": search_messages,
        "!we": weather_command,
        "!ban": handle_ban_command,
        "!user_ban": show_all_ban_user,
        "!unban": handle_unban_command,
        "!user_warn": show_all_warn_user,
        "!unwarn": handle_unwarn_command,
        "!user_mute": show_all_mute_user,
        "!unmute": handle_unmute_command,
        # "!sou": handle_private_message_command,
    }

    user_permissions = ["Majitel", "Spolu Majitel", "Admin/ka", "Helper", "Učitel/ka", "Test", "Ředitel/ka",
                        "Zástupkyně", "Assisten/ka", "Kamarád", None]
    full_permissions = ["Majitel", "Spolu Majitel", "Admin/ka", "Helper", "Učitel/ka", "Test", "Ředitel/ka",
                        "Zástupkyně", "Assisten/ka", "Kamarád", ]

    command_permissions = {
        "!help": user_permissions,
        "!cl": user_permissions,
        "!s": user_permissions,
        "!mute": full_permissions,
        "!message": full_permissions,
        "!users": full_permissions,
        "!warn": full_permissions,
        "!m": user_permissions,
        "!we": user_permissions,
        "!ban": full_permissions,
        "!user_ban": full_permissions,
        "!unban": full_permissions,
        "!user_warn": full_permissions,
        "!unwarn": full_permissions,
        "!user_mute": full_permissions,
        "!unmute": full_permissions,
        # "!sou": user_permissions,
    }

    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------

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
            command_list[command](
                Message(
                    user_name=page.session.get("user_name"),
                    text=message_text,
                    message_type="command",
                    user_role=user_role,
                    page=page,
                ),
                page,
            )
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
                user_name="Zib",
                user_role="Bot",
                text="Chyba při ukládání zprávy, identifikátor uživatele není k dispozici.",
                message_type="system",
                page=page,
            )

            chat_message = ChatMessage(message)
            chat.controls.append(chat_message)
            return

        update_message_count(user_id)

        print("Odesílání zprávy:", message_text, "Uživatel:", user_id)

        message_text_lower = message_text.lower().strip()
        if message_text_lower.startswith("!help") or message_text_lower.startswith(
                "!calculate"
        ):
            parts = message_text_lower.split(" ", 1)
            command = parts[0]
            process_command(command, user_role, message_text, page)

            if command in command_list:
                print(f"Calling {command}")
                command_list[command](
                    Message(
                        user_name=page.session.get("user_name"),
                        text=message_text_lower,
                        user_id=page.session.get("user_id"),
                        message_type="command",
                        user_role=page.session.get("user_role"),
                        page=page,
                    ),
                    page,
                )  # Volání správné funkce z command_list

            else:
                print(f"Unknown command: {command}")
                ChatMessage(
                    Message(
                        user_name="Zib",
                        text=f"Příkaz '{command}' neexistuje. Zkuste jiný.",
                        message_type="chat_message",
                        user_id=page.session.get("user_id"),
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
            message = Message(
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
            update_ui_for_mute_status(user_id)

        ban_text = "Nemůžeš posílat zprávy, jen je sledovat. Protože jseš zabanovaný (jsi zlobil)"

        if is_ban(user_id):
            message = Message(
                user_name="Zib",
                text=ban_text,
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
        update_ui_for_ban_status(user_id)  # Aktualizujte UI, pokud je umlčen
        # return

        if message_text:
            page.pubsub.send_all(
                Message(
                    user_name=f"{page.session.get('user_name')} {page.session.get('user_class')}",
                    text=message_text,
                    message_type="chat_message",
                    user_role=page.session.get("user_role"),
                    user_profile_picture=page.session.get("profile_picture"),
                    user_id=page.session.get("user_id"),
                    page=page,
                )
            )
            print(cursor)
            print(message_text, user_id)
            local_cursor.execute(
                "INSERT INTO chat (message, user_id) VALUES (%s, %s)",
                (message_text, user_id),
            )

            # Aktualizace stavu online uživatele a času poslední aktivity
            local_cursor.execute(
                "UPDATE online_users SET is_online = 1, last_activity = NOW() WHERE user_id = %s",
                (user_id,)
            )

            # mydb.commit()
            mydb.commit()

        message_count = login_user(user_id)
        if message_count == 10:
            message = Message(
                user_name="Zib",
                text="Gratulujeme, jste dosáhl milníku 10 zpráv!",
                message_type="chat_message",
                user_role="Bot",
                page=page,
            )
            chat_message = ChatMessage(message)
            chat.controls.append(chat_message)

        # Vymazat pole pro zprávu
        update_message_count(user_id)
        new_message.value = ""
        new_message.focus()

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def session_handler(page):
        global chat, user_message_input

        # Nastavení UI a chatové komponenty
        chat = ft.Column()
        user_message_input = ft.TextField(
            label="Vaše zpráva", on_submit=on_user_message_submit
        )

        page.add(chat)
        page.add(user_message_input)

        page.update()

    # --------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def on_message(message: Message, page: ft.Page):
        chat_message = ChatMessage(message)
        chat.controls.append(chat_message)
        page.update()
        text_password.on_submit = lambda e: join_chat_click(e)
        page.update()
        # Create a new ChatMessage instance with the required arguments

    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
    def nav_change(index):
        main_body.controls.clear()
        if index < len(page_map):
            main_body.controls.append(page_map[index])
        else:
            main_body.controls.append(
                ft.Column(
                    [
                        ft.Text(
                            f"HACKER!!! dělám jsi srandu :D, našel jsi chybu takovou, Tohle ->. {index} je index, jestli máš tam 1 nebo 2 nebo jakýkoliv číslo tak to je jaký číslo má například pravidla. Klikni někam jinam než jsi se kliknul, a budeš zahráněn. Když tak, mi to pravidlo nahlaš."
                        )
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    expand=True,
                )
            )
        page.update()

    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------

    def update_online_users_text(page):
        global online_users
        online_users_text.value = f"Počet uživatelů online: {len(online_users)}"
        online_users_text.update()

    def remove_user_from_online(user_name, page):
        if user_name in online_users:
            del online_users[user_name]
            update_online_users_text(page)  # Aktualizujte text o online uživatelích
            print(f"Uživatel '{user_name}' byl odebrán z online_users.")
        else:
            print(f"Uživatel '{user_name}' nebyl nalezen v online_users.")

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
                label="Pravidla",
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
                label="Nastavení",
            ),
            ft.NavigationDrawerDestination(
                icon_content=ft.Icon(ft.icons.BOOKMARKS),
                selected_icon_content=ft.Icon(ft.icons.BOOKMARKS),
                label="Recenze",
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

    main_body = ft.Column(
        [Pravidla(page)],
        alignment=ft.MainAxisAlignment.START,
        expand=True,
        scroll=ft.ScrollMode.AUTO,
    )
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
        size=11,
    )

    page.dialog = ft.AlertDialog(
        open=True,
        modal=True,
        title=ft.Text("Vítej!"),
        content=ft.Column(
            [text_username, text_password, text_1], width=340, height=145, tight=True
        ),
        actions=[
            ft.ElevatedButton(text="Připojit se", on_click=join_chat_click),
            ft.ElevatedButton(text="Registrovat účet", on_click=create_account),
        ],
        actions_alignment="end",
    )

    online_users_text = ft.Text(
        f"Počet uživatelů online: {len(online_users)}", color=ft.colors.WHITE, size=12
    )

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
                ft.Column(
                    [
                        main_body,
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
                    ]
                )
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
                ft.IconButton(
                    icon=ft.icons.MESSAGE,
                    tooltip="Soukromý chat",
                    on_click=soukromy,

                ),
                ft.IconButton(
                    icon=ft.icons.UPLOAD_FILE,
                    tooltip="Nefuknční, ale pracuje se nad tím",
                    on_click=lambda _: beta_pick_files(

                    )
                ),
            ]
        ),
    )


# ----------------------------------------------------------------------------------------------------------------------------------------------------------------

ft.app(port=8550, target=main, view=ft.WEB_BROWSER)
