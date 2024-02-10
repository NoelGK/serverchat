import os
from dataclasses import dataclass
import bcrypt

from src.database import upload_user, get_user


@dataclass
class User:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.chat_id = None

    def save_user(self):
        salt, hassed_password = self._hash_password()
        upload_user(self.username, hassed_password, salt)

    def find_user(self):
        saved_user = get_user(self.username)
        user_exists = saved_user is not None
        return user_exists

    def check_password(self, entered_password):
        user_hassed_password, user_salt = self._get_user_credentials()

        entered_hassed_password = bcrypt.hashpw(entered_password.encode('utf-8'), user_salt)
        if entered_hassed_password == user_hassed_password:
            return True

        return False

    def _hash_password(self):
        # Define a salt
        salt = bcrypt.gensalt()
        hassed_password = bcrypt.hashpw(self.password.encode('utf-8'), salt)

        return salt, hassed_password

    def _get_user_credentials(self):
        _, hassed_pw, salt = get_user(self.username)
        return hassed_pw, salt



if __name__ == '__main__':
    pass
