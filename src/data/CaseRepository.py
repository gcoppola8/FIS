from data import *


class CaseRepository:
    """
    CaseRepository is responsible to access databases to create and retrieve Case.
    It abstracts the usage of sqlalchemy, exposing simple methods.
    """

    # Limit of page size.
    PAGE_LIMIT = 1000

    # Find a not deleted case by id.
    def find_by_id(self, case_id: int) -> Case:
        return session.query(Case).filter_by(case_id=case_id, deleted=False).first()

    # Find a list of not deleted cases with limit to 1000.
    def find_all(self) -> list[Case]:
        return session.query(Case).filter_by(deleted=False).limit(self.PAGE_LIMIT).all()

    # Find a list of not deleted cases with pagination.
    def find_all(self, page_number: int, page_size: int) -> list[Case]:
        offset = (page_number - 1) * page_size
        return session.query(Case).filter_by(deleted=False).offset(offset).limit(page_size).all()

    # Search cases.
    def search(self):
        pass

    # Delete a case by id, removing from the database.
    def delete_by_id(self, case_id: int) -> None:
        session.begin()
        case_to_delete = self.find_by_id(case_id)
        session.delete(case_to_delete)
        session.commit()

    # Save a case into the database.
    def save(self, case: Case) -> int:
        inserted_id = case.case_id
        session.begin()
        if case.case_id is None:
            session.add(case)
            session.flush()
            inserted_id = case.case_id
        else:  # Existing case, just updating it.
            case.updatedOn = datetime.now()
            session.merge(case)
        session.commit()
        return inserted_id
