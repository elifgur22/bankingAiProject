from sqlalchemy.orm import Session

from app.domain.user import User


class UserRepository:

    def save(self, db: Session, user: User) -> User:
        db.add(user)
        db.flush()
        db.refresh(user)

        return user

    def find_by_username(self, db: Session, username: str) -> User | None:
        return (
            db.query(User)
            .filter(User.username == username)
            .first()
        )
