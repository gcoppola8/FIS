from sys import path
path.append('..')
from data import *


class PermissionRepository:
    """
    PermissionRepository is responsible to access databases to verify permissions.
    It abstracts the usage of sqlalchemy, exposing simple methods.
    """

    @staticmethod
    def verify(entity_id: Integer, op_code: OpCode, user_id: Integer):
        session.query(Permission).filter_by(entity=entity_id, operation=op_code, user=user_id)
