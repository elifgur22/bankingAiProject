from sqlalchemy.orm import Session
from app.domain.account import Account
from app.domain.account_balance import AccountBalance


class AccountRepository:

    def save(self, db: Session, account: Account):
        db.add(account)
        db.commit()
        db.refresh(account)

        return account

    def save_account_balance(self, db : Session, account_balance: AccountBalance):
        db.add(account_balance)
        db.commit()
        db.refresh(account_balance)

        return account_balance

