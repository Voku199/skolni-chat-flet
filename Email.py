import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import tkinter as tk
from tkinter import messagebox


# Funkce pro odesílání emailů
def send_emails(to_email, subject, body, count):
    from_email = "skolnichat.zib@gmail.com"
    from_password = "vfqf cefz tjuh txor"  # Nahraď skutečným heslem specifickým pro aplikaci

    try:
        # Připojení k SMTP serveru a odeslání emailů
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, from_password)

        for i in range(count):
            # Vytvoření emailu
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            text = msg.as_string()
            server.sendmail(from_email, to_email, text)

        server.quit()
        return True
    except Exception as e:
        print(f"Chyba při odesílání emailů: {e}")
        return False


# Funkce pro generování ověřovacího kódu
def generate_verification_code():
    return str(random.randint(100000, 999999))


# Globální proměnné
verification_code = None


# Funkce pro zpracování kliknutí na tlačítko "Ověřit"
def on_verify():
    user_email = email_entry.get()
    if not user_email:
        messagebox.showerror("Chyba", "Zadejte váš email")
        return

    global verification_code
    verification_code = generate_verification_code()
    email_subject = "Ověřovací kód"
    email_body = f"Váš ověřovací kód je: {verification_code} Zavolej mi prosím :( Budu smutnej, -Vojta"

    if send_emails(user_email, email_subject, email_body, 10):
        messagebox.showinfo("Úspěch", f"Bylo odesláno 10 emailů na {user_email}")
        show_code_entry()
    else:
        messagebox.showerror("Chyba", "Nepodařilo se odeslat email")


# Funkce pro zobrazení vstupního pole pro ověřovací kód
def show_code_entry():
    code_label.pack(pady=10)
    code_entry.pack(pady=5)
    submit_button.pack(pady=20)


# Funkce pro zpracování kliknutí na tlačítko "Odeslat kód"
def on_submit_code():
    entered_code = code_entry.get()
    if entered_code == verification_code:
        messagebox.showinfo("Úspěch", "Váš účet byl ověřen!")
    else:
        messagebox.showerror("Chyba", "Nesprávný ověřovací kód. Zkuste to znovu.")


# Nastavení GUI
root = tk.Tk()
root.title("Ověření emailu")

tk.Label(root, text="Zadejte váš email:").pack(pady=10)
email_entry = tk.Entry(root, width=30)
email_entry.pack(pady=5)

verify_button = tk.Button(root, text="Ověřit (10 emailů)", command=on_verify)
verify_button.pack(pady=20)

code_label = tk.Label(root, text="Zadejte ověřovací kód:")
code_entry = tk.Entry(root, width=30)
submit_button = tk.Button(root, text="Odeslat kód", command=on_submit_code)

root.mainloop()
