import datetime
from sys import path
path.append('..')
from core.Authorization import Authorizer, AuthError
from data import Case, OpCode
from data.CaseRepository import CaseRepository


class CaseService:
    """
    CaseService implements CRUD operations on Cases through the use of a CaseRepository.
    It supports authorization. To disable Authorization, inject an always-true Authorizer.
    It's implemented as a singleton.
    """
    _instance = None

    def __new__(cls, case_repository: CaseRepository, authorizer: Authorizer):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
            cls.__init__(cls._instance, case_repository, authorizer)
        return cls._instance

    def __init__(self, case_repository: CaseRepository, authorizer: Authorizer):
        self.case_repo = case_repository
        self.authorizer = authorizer

    # Find a case by id.
    def find_by_id(self, case_id: int) -> Case:
        return self.case_repo.find_by_id(case_id)

    # Find a list of cases with support to pagination.
    def find_all(self, page_number: int = 1, page_size: int = 1000) -> list[Case]:
        if page_size is None or page_number is None:
            return self.case_repo.find_all()

        return self.case_repo.find_all(page_number, page_size)

    # Archive a case. It sets deleted=true, and it is not physically removed.
    def archive(self, case: Case):
        self.authorizer.authorize(OpCode.DELETE, case=case)
        case.deleted = True
        case.deletedOn = datetime.datetime.now()
        self.case_repo.save(case)

    # Create a new case.
    def create(self, case: Case):
        self.authorizer.authorize(OpCode.CREATE)
        return self.case_repo.save(case)

    # Update a case.
    def save(self, case: Case):
        self.authorizer.authorize(OpCode.UPDATE)
        return self.case_repo.save(case)

    # Verify permission to create case.
    def authorize_create(self):
        self.authorizer.authorize(OpCode.CREATE)
