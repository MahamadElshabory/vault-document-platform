from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.db.session import get_db
from app.models import user
from app.schemas.auth import UserSignUp , UserLogin , TokenResponse
from app.models.organization import Organization 
from app.models.user import User
from app.api.services.user_service import UserService
from app.core.security import create_access_token, verify_password 
from app.api.dependencies import get_current_user, require_org_scope


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

user_service = UserService()



@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(
    data: UserSignUp,
    session: Session = Depends(get_db)
):
    if user_service.user_exists(
        email=data.email,
        session=session
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    organization = Organization(
        name=data.organization_name
    )

    session.add(organization)
    session.flush()

    user = user_service.create_user(
        name=data.name,
        email=data.email,
        password=data.password,
        org_id=organization.id,
        session=session
    )

    session.commit()

    session.refresh(organization)
    session.refresh(user)

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "org_id": user.org_id
    }
    
    
@router.post("/login", status_code=status.HTTP_200_OK)
def login(data : UserLogin ,session: Session = Depends(get_db) ):
    
    user = user_service.get_user_by_email(data.email,session)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not verify_password(data.password,user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token = create_access_token(user.id,user.org_id)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer"
    )
          

@router.get("/users/me")
def get_me(current_user : User = Depends(get_current_user)):
    
    return {
        "id" : current_user.id,
        "name" : current_user.name,
        "email" : current_user.email,
        "org_id" : current_user.org_id
    }

@router.get("/organizations/{id}")
def get_organization(id: int , current_user: User = Depends(get_current_user )):

    user = require_org_scope( id, current_user )

    return {
        "message": "Access allowed",
        "organization_id": id
    }
        
    