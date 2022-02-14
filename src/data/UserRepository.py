from sys import path
path.append('..')
from data import *


class UserRepository:
    """
    UserRepository is responsible to access databases to create and retrieve Users.
    It abstracts the usage of sqlalchemy, exposing simple methods.
    It is implemented as a singleton.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance

    def find_by_id(self, id: int) -> User:
        return session.query(User).get(id)

    def find_by_username(self, username: str) -> User:
        return session.query(User).filter_by(username=username).first()

    def create(self, user: User) -> None:
        session.begin()
        session.merge(user)
        session.commit()
