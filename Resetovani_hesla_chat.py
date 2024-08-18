import bcrypt
import mysql.connector
import os

# Připojení k databázi
mydb = mysql.connector.connect(
    host=os.environ["DB_HOST"],
    port=os.environ["DB_PORT"],
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASS"],
    database=os.environ["DB_NAME"]
)
cursor = mydb.cursor()

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed

def reset_password(user_id, new_password):
    hashed_password = hash_password(new_password)
    try:
        cursor.execute("UPDATE user SET password = %s WHERE id = %s", (hashed_password, user_id))
        mydb.commit()
        print("Heslo bylo úspěšně resetováno.")
    except mysql.connector.Error as err:
        print(f"Nastala chyba: {err}")

# Příklad použití
user_id = 1  # ID uživatele, který chce resetovat heslo
new_password = "a"  # Nové heslo zadané uživatelem
reset_password(user_id, new_password)