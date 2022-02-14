import bcrypt
from sys import path
path.append('..')
from core import my_salt
from data import User
from data.UserRepository import UserRepository


class UserService:
    """
    UserService implements create and retrieve operations on Users through the use of a UserRepository.
    It's implemented as a singleton.
    """
    _instance = None

    def __new__(cls, user_repository: UserRepository):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
            cls.__init__(cls._instance, user_repository)
        return cls._instance

    def __init__(self, user_repository: UserRepository):
        self.user_repo = user_repository

    # Create a new user.
    # Password is encrypted when saved.
    def create(self, user: User) -> None:
        if type(user.password) is str:
            user.password = bcrypt.hashpw(user.password.encode(), my_salt)
        else:
            raise Exception("password must be of type string")

        self.user_repo.create(user)

    # Retrieve an User by username.
    def find_by_username(self, username):
        return self.user_repo.find_by_username(username)
