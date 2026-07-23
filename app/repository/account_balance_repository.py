from sqlalchemy.orm import Session

from app.domain.account_balance import AccountBalance


class AccountBalanceRepository:

    def find_by_account_id(
            self,
            db: Session,
            account_id: int
    ) -> type[AccountBalance] | None:

        return (
            db.query(AccountBalance)
            .filter(AccountBalance.account_id == account_id)
            .first()
        )

    def save(
            self,
            db: Session,
            account_balance: AccountBalance
    ) -> AccountBalance:

        db.add(account_balance)
        db.commit()
        db.refresh(account_balance)

        return account_balance