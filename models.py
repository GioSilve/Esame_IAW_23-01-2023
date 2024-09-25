from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, username, name, surname, type):
        self.id = id
        self.username = username
        self.name = name
        self.surname = surname
        self.type = type
