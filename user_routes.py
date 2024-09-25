from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..models import user_models
from ..schemas import user_schemas
from ..database import database
from ..dependencies.user_oauth2 import get_current_user
from .logout import logout_check

router = APIRouter(prefix="/word-wiz", tags=["Users"])


# GET ALL USERS
@router.get("/users", response_model=List[user_schemas.ShowUser])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(database.get_db),
    current_user=Depends(get_current_user),
):
    logout_check(id=current_user)
    users = db.query(user_models.User).offset(skip).limit(limit).all()
    return users


# GET USERS BY USER_ID
@router.get("/users/{user_id}", response_model=user_schemas.ShowUser)
def read_user(
    user_id: int,
    db: Session = Depends(database.get_db),
    current_user=Depends(get_current_user),
):
    logout_check(id=current_user)
    db_user = db.query(user_models.User).filter(
        user_models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


# protected but wrong


# EDIT USERS BY USER_ID
@router.put(
    "/update-users/",
    response_model=user_schemas.ShowUser,
    summary="Update the current login user",
    description="Update the current login user",
    response_description="The updated user details.",
    responses={404: {"description": "User not found"}},
)
def update_user(
    user: user_schemas.UpdateUser,
    db: Session = Depends(database.get_db),
    current_user=Depends(get_current_user),
):
    db_user = (
        db.query(user_models.User).filter(
            user_models.User.id == current_user).first()
    )
    logout_check(id=current_user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Update the user's information
    for field, value in vars(user).items():
        setattr(db_user, field, value)

    db.commit()
    db.refresh(db_user)
    return db_user


# DELETE USERS BY USER_ID
@router.delete(
    "/delete-users/",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Delete the current login user",
    description="Delete the current login user from the database",
    responses={202: {"description": "User  deleted successfully"}},
)
def delete_user(
    db: Session = Depends(database.get_db), current_user=Depends(
        get_current_user)
):
    db_user = (
        db.query(user_models.User).filter(
            user_models.User.id == current_user).first()
    )
    logout_check(id=current_user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {f"User with id {current_user} deleted successfully"}
