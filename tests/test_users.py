from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models.user import UserModel
from app.security.passwords import hash_password, verify_password


def test_user_model_stores_hashed_password_that_can_be_verified() -> None:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    password_hash = hash_password("correct horse battery staple")

    db = TestingSessionLocal()
    try:
        user = UserModel(email="buyer@example.com", password_hash=password_hash)
        db.add(user)
        db.commit()
        db.refresh(user)

        saved_user = db.query(UserModel).filter(UserModel.email == "buyer@example.com").one()
    finally:
        db.close()

    assert saved_user.id is not None
    assert saved_user.email == "buyer@example.com"
    assert saved_user.password_hash != "correct horse battery staple"
    assert verify_password("correct horse battery staple", saved_user.password_hash)
    assert not verify_password("wrong password", saved_user.password_hash)


def test_verify_password_returns_false_for_malformed_hashes() -> None:
    malformed_hashes = [
        "not-a-password-hash",
        "pbkdf2_sha999$1$00$00",
        "pbkdf2_sha256$-1$00$00",
        "not_pbkdf2$1$00$00",
    ]

    for malformed_hash in malformed_hashes:
        assert not verify_password("password", malformed_hash)
