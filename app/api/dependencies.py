from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
# from sqlalchemy.orm import Session
from sqlmodel import Session
from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user( token: str = Depends(oauth2_scheme), db: Session = Depends(get_db) ) -> User:

    decoded_token = decode_token(token)

    if decoded_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    user_id = decoded_token.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user


def require_org_scope(org_id : int , current_user : User = Depends(get_current_user)) -> User :
    
    if current_user.org_id != org_id :
        raise HTTPException(
        status_code=403,
        detail="Access to this organization is forbidden"
    )
        
    return current_user   