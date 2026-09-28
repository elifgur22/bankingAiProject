from sqlalchemy.orm import Session

from app.domain.account import Account


class AccountRepository:

    def save(self, db: Session, account: Account) -> Account:
        db.add(account)
        db.flush()
        db.refresh(account)

        return account

    def find_by_id(self, db: Session, account_id: int) -> Account | None:
        return (
            db.query(Account)
            .filter(Account.id == account_id)
            .first()
        )

    def find_by_account_number(
            self,
            db: Session,
            account_number: str
    ) -> Account | None:

        return (
            db.query(Account)
            .filter(Account.account_number == account_number)
            .first()
        )

    def find_by_customer_id(
            self,
            db: Session,
            customer_id: int
    ) -> list[Account]:

        return (
            db.query(Account)
            .filter(Account.customer_id == customer_id)
            .order_by(Account.id)
            .all()
        )
