from sqlalchemy.orm import Session

from app.models.user import UserModel


def get_user_by_email(db: Session, email: str) -> UserModel | None:
    return db.query(UserModel).filter(UserModel.email == email).first()


def create_user(db: Session, email: str, password_hash: str) -> UserModel:
    user = UserModel(email=email, password_hash=password_hash)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
