from flask import request, session

from core.Authorization import Authorizer, AuthError
from core.UserService import UserService
from data import OpCode, Case, User
from data.PermissionRepository import PermissionRepository
from data.UserRepository import UserRepository


class DefaultAuthorizer(Authorizer):

    def authorize(self, op_code: OpCode, case: Case = None):
        current_user: User = get_user()

        if current_user is None:
            raise AuthError

        # User with high authorization level.
        if op_code == OpCode.CREATE and current_user.auth_level == 1:
            return True

        # The current user is the owner of the entity
        if case is not None and current_user == case.createdBy:
            return True

        # the current user has permission for the requested operation
        if case is not None:
            permission = PermissionRepository.verify(case.get_id(), op_code, current_user.user_id)
            if permission is not None:
                return True

        raise AuthError


def get_user():
    username = session['user_auth'][0]
    user_service = UserService(UserRepository())
    return user_service.find_by_username(username)
