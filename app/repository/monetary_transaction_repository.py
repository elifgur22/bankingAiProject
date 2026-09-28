from datetime import datetime

from sqlalchemy.orm import Session

from app.domain.monetary_transaction import MonetaryTransaction


class MonetaryTransactionRepository:

    def save(
            self,
            db: Session,
            transaction: MonetaryTransaction
    ) -> MonetaryTransaction:

        db.add(transaction)
        db.flush()
        db.refresh(transaction)

        return transaction

    def save_all(
            self,
            db: Session,
            transactions: list[MonetaryTransaction]
    ) -> list[MonetaryTransaction]:

        db.add_all(transactions)
        db.flush()

        for transaction in transactions:
            db.refresh(transaction)

        return transactions

    def find_by_id(
            self,
            db: Session,
            transaction_id: int
    ) -> MonetaryTransaction | None:

        return (
            db.query(MonetaryTransaction)
            .filter(MonetaryTransaction.id == transaction_id)
            .first()
        )

    def find_reversal_of(
            self,
            db: Session,
            transaction_id: int
    ) -> MonetaryTransaction | None:

        return (
            db.query(MonetaryTransaction)
            .filter(
                MonetaryTransaction.reversal_of_transaction_id
                == transaction_id
            )
            .first()
        )

    def find_by_transfer_reference(
            self,
            db: Session,
            transfer_reference: str
    ) -> list[MonetaryTransaction]:

        return (
            db.query(MonetaryTransaction)
            .filter(
                MonetaryTransaction.transfer_reference == transfer_reference
            )
            .order_by(MonetaryTransaction.id)
            .all()
        )

    def find_by_account_id(
            self,
            db: Session,
            account_id: int,
            transaction_type: str | None = None,
            date_from: datetime | None = None,
            date_to: datetime | None = None,
            limit: int = 50,
            offset: int = 0
    ) -> list[MonetaryTransaction]:

        query = self._history_query(
            db,
            account_id,
            transaction_type,
            date_from,
            date_to
        )

        return (
            query
            .order_by(MonetaryTransaction.id.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

    def count_by_account_id(
            self,
            db: Session,
            account_id: int,
            transaction_type: str | None = None,
            date_from: datetime | None = None,
            date_to: datetime | None = None
    ) -> int:

        return self._history_query(
            db,
            account_id,
            transaction_type,
            date_from,
            date_to
        ).count()

    @staticmethod
    def _history_query(
            db: Session,
            account_id: int,
            transaction_type: str | None,
            date_from: datetime | None,
            date_to: datetime | None
    ):
        query = (
            db.query(MonetaryTransaction)
            .filter(MonetaryTransaction.account_id == account_id)
        )

        if transaction_type is not None:
            query = query.filter(
                MonetaryTransaction.transaction_type == transaction_type
            )

        if date_from is not None:
            query = query.filter(
                MonetaryTransaction.create_time >= date_from
            )

        if date_to is not None:
            query = query.filter(
                MonetaryTransaction.create_time <= date_to
            )

        return query
