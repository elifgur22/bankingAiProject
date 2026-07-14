from sqlalchemy.orm import Session

from app.domain.monetary_transaction import MonetaryTransaction


class MonetaryTransactionRepository:

    def save(
            self,
            db: Session,
            transaction: MonetaryTransaction
    ) -> MonetaryTransaction:

        db.add(transaction)
        db.commit()
        db.refresh(transaction)

        return transaction