import bcrypt

def hash_password(password, salt=None):
    # Hash a password using bcrypt
    if salt is None:
        salt = bcrypt.gensalt()
    else:
        salt = salt.encode('utf-8')

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password, salt