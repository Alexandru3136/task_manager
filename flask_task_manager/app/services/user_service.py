from app.models.user import User

class UserService:
    def add_user(self, user):
        # Logic to add user to the database
        pass

    def get_all_users(self):
        # Logic to retrieve all users from the database
        return User.query.all()
