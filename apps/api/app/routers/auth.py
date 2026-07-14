from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..database import get_session
from ..models import User
from ..schemas import LoginRequest, LoginResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.token == payload.token, User.is_active == True)).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid demo token")
    return LoginResponse(access_token=user.token, role=user.role.value)
