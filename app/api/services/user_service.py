from sqlmodel import Session, select

from app.core.security import hash_password
from app.db import session
from app.models.organization import Organization
from app.models.user import User


class UserService:

    def get_user_by_email(
        self,
        email: str,
        session: Session
    ) -> User | None:

        statement = select(User).where(User.email == email)
        user = session.exec(statement).first()

        return user


    def get_user_by_id(
        self,
        user_id: str,
        session: Session
    ) -> User | None:

        return session.get(User, user_id)


    def get_organization(
        self,
        org_id: int,
        session: Session
    ) -> Organization | None:

        return session.get(Organization, org_id)


    def user_exists(
        self,
        email: str,
        session: Session
    ) -> bool:

        user = self.get_user_by_email(
            email=email,
            session=session
        )

        return user is not None


    def organization_exists(
        self,
        org_id: int,
        session: Session
    ) -> bool:

        organization = self.get_organization(
            org_id=org_id,
            session=session
        )

        return organization is not None
    
    def create_user(
        self,
        name: str,
        email: str,
        password: str,
        org_id: int,
        session: Session
        ) -> User:

        new_user = User(
        name=name,
        email=email,
        hashed_password=hash_password(password),
        org_id=org_id
    )

        session.add(new_user)
        session.flush()
        session.refresh(new_user)

        return new_user