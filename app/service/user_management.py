from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.cruds.users.users_crud import find_by_email, add_user
from app.models.users.users_model import Users


class UserManagementService:
    async def register_user(
            self,
            user: Users,
            db: AsyncSession = Depends(get_db),
    ):
        # Check if user already exists
        existing_user = find_by_email(session=db, email=user.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")

        # Add user
        created_user = add_user(session=db, user=user)
        return created_user

