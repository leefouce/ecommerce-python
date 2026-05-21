from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import UserModel
from app.repositories.users import create_user, get_user_by_email
from app.schemas.user import Token, User, UserCreate, UserLogin
from app.security.auth import get_current_user
from app.security.passwords import hash_password, verify_password
from app.security.tokens import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserCreate, db: Session = Depends(get_db)) -> UserModel:
    existing_user = get_user_by_email(db, payload.email)
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    try:
        return create_user(
            db,
            email=payload.email,
            password_hash=hash_password(payload.password),
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        ) from None


@router.post("/login", response_model=Token)
def login_user(payload: UserLogin, db: Session = Depends(get_db)) -> Token:
    user = get_user_by_email(db, payload.email)
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    return Token(access_token=create_access_token(subject=user.email), token_type="bearer")


@router.get("/me", response_model=User)
def read_current_user(current_user: UserModel = Depends(get_current_user)) -> UserModel:
    return current_user
