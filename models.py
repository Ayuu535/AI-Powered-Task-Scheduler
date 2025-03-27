from datetime import datetime
from flask_login import UserMixin

# In-memory storage
users = {}
tasks = {}

class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = None

class Task:
    def __init__(self, id, user_id, title, description, deadline):
        self.id = id
        self.user_id = user_id
        self.title = title
        self.description = description
        self.deadline = deadline
        self.completed = False
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
