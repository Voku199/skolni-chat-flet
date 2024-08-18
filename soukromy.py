import mysql.connector
import flet as ft
import os
from dotenv import load_dotenv

load_dotenv()  # Načtení proměnných z .env souboru

# Seznam přihlášených uživatelů
online_users = {}


# Debugging: Výpis uživatelů
def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST"),
        port=os.environ.get("DB_PORT"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASS"),
        database=os.environ.get("DB_NAME"),
        connection_timeout=30,
    )


# Funkce pro odesílání zpráv
def send_message(sender, receiver, message, user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Kontrola, zda existuje příjemce
    cursor.execute('SELECT * FROM user WHERE user_name = %s', (receiver,))
    if cursor.fetchone() is None:
        print(f"Error: User '{receiver}' does not exist.")
        conn.close()
        return

    # Uložení zprávy do databáze
    cursor.execute('INSERT INTO chat (sender, receiver, message, user_id) VALUES (%s, %s, %s, %s)',
                   (sender, receiver, message, user_id))
    conn.commit()

    # Kontrola, zda je uživatel online
    if receiver in online_users:
        # Zobrazit zprávu od bota
        bot_message = f"Message from {sender}: {message}"
        online_users[receiver].send(bot_message)

    conn.close()
    print("Message sent successfully.")


# Funkce pro načtení zpráv při přihlášení
def on_user_login(user_name):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Načtení nečtených zpráv
    cursor.execute('SELECT sender, message FROM chat WHERE receiver = %s', (user_name,))
    messages = cursor.fetchall()

    # Zobrazení zpráv
    for sender, message in messages:
        bot_message = f"Message from {sender}: {message}"
        online_users[user_name].send(bot_message)

    # Smazání nečtených zpráv
    cursor.execute('DELETE FROM chat WHERE receiver = %s', (user_name,))
    conn.commit()
    conn.close()

    print(f"User {user_name} logged in and received messages.")


def get_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT user_name FROM user')
    users = cursor.fetchall()
    conn.close()
    return [user[0] for user in users]


# Hlavní funkce
def main(page: ft.Page):
    page.title = "Chat Application"

    # Reference pro textová pole
    recipient_ref = ft.Ref[ft.Dropdown]()
    message_ref = ft.Ref[ft.TextField]()

    # Dialog pro zadání uživatele a zprávy
    private_message_dialog = ft.AlertDialog(
        title=ft.Text("Send Private Message"),
        content=ft.Column([
            ft.Dropdown(ref=recipient_ref, label="To:", options=[]),
            ft.TextField(label="Message:", ref=message_ref),
        ]),
        actions=[
            ft.TextButton("Send",
                          on_click=lambda e: send_private_message(e, recipient_ref, message_ref, private_message_dialog,
                                                                  page)),
            ft.TextButton("Cancel", on_click=lambda e: close_dialog(private_message_dialog, page))
        ]
    )

    # Tlačítko pro odesílání soukromých zpráv
    private_message_button = ft.ElevatedButton(
        text="Send Private Message",
        on_click=lambda e: show_private_message_dialog(e, recipient_ref, private_message_dialog, page)
    )

    # Přidání tlačítka a dialogu do stránky
    page.add(
        private_message_button,
        private_message_dialog
    )


def show_private_message_dialog(e, recipient_ref, private_message_dialog, page):
    users = get_users()  # Načtení uživatelů z databáze
    recipient_ref.current.options = [ft.dropdown.Option(user) for user in users]
    private_message_dialog.open = True
    page.update()


def send_private_message(e, recipient_ref, message_ref, private_message_dialog, page):
    recipient = recipient_ref.current.value
    message = message_ref.current.value
    sender = "YourUserName"  # Zde zadej aktuální uživatelské jméno
    user_id = 1  # Zde zadej aktuální uživatelské ID

    if not recipient or not message:
        print("Recipient and message cannot be empty.")
        return

    # Odeslání zprávy
    send_message(sender, recipient, message, user_id)

    # Skrytí dialogu po odeslání zprávy
    private_message_dialog.open = False
    page.update()


def close_dialog(dialog, page):
    dialog.open = False
    page.update()


# Inicializace aplikace
ft.app(target=main)
