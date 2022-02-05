from data.PermissionRepository import PermissionRepository
from data import User, Case, OpCode


class Authorizer:
    """
    An interface of an authorizer. Different implementations can authorize users with different parameters and logic.
    """
    def authorize(self, op_code: OpCode, case: Case):
        return True


class AuthError(Exception):
    """
    Standard exception to use in case of authorization violation.
    """
    def __str__(self) -> str:
        return "Authorization exception"
