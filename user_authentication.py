# This is the router for authentication (login and signup)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import database
from ..schemas import user_schemas
from ..models import user_models
from ..crud import logout_crud
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from datetime import timedelta
from ..dependencies import user_oauth2
from passlib.context import CryptContext


user_models.database.Base.metadata.create_all(bind=database.engine)
router = APIRouter(prefix="/word-wiz", tags=["Authentication"])

# the token will expire after 24 hours
ACCESS_TOKEN_EXPIRE_HOUR = 24

# encyrpt the user password

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Hash:
    def bcrypt(password: str):
        return pwd_context.hash(password)

    # verify the password
    def verify(hashed_password, plain_password):
        return pwd_context.verify(plain_password, hashed_password)


# function to get user email
def get_user_email(db, email):
    user = db.query(user_models.User).filter(
        user_models.User.email == email).first()
    return user


def is_empty(string):
    return string.strip() == ""


@router.post(
    "/signup",
    status_code=status.HTTP_201_CREATED,
    response_model=user_schemas.ShowUser,
    summary="Enables the User to create a new account(Signup)",
    description="Create a new user and add it to the database",
    response_description='''Returns a successful created.
    message and status code of 201''',
)
def user_signup(user: user_schemas.UserSignUp, db: Session = Depends(
    database.get_db)
                ):

    if (
        is_empty(user.firstname)
        or is_empty(user.surname)
        or is_empty(user.email)
        or is_empty(user.username)
        or is_empty(user.password)
        or is_empty(user.confirm_password)
    ):
        raise HTTPException(
            status_code=400, detail="Please fill in all fields"
            )

    new_user = user_models.User(
        firstname=user.firstname,
        surname=user.surname,
        email=user.email,
        username=user.username,
        password=Hash.bcrypt(user.password),
    )

    # check if the user entered the correct password
    if user.password != user.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    # check if useremail already exist in the database
    existed_user = get_user_email(db, user.email)
    if existed_user:
        raise HTTPException(
            status_code=409, detail="This email already exists"
            )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)


# Create the PersonalInformation entry with the default firstname from User
    new_user_profile = user_models.PersonalInformation(
        firstname=user.firstname,  # Set the firstname from the User table
        lastname=user.surname,
        username=user.username,
        email=user.email,  # This should match the user's email
        user=new_user,  # Establish relationship
    )

    db.add(new_user_profile)
    db.commit()
    db.refresh(new_user_profile)

    return new_user


@router.post(
    "/login",
    summary="Login and generate JWT token with type and user id",
    description='''Authenticate a user by checking the email and password
    against the database. If valid,
    generate and return a JWT access token and type''',
    responses={404: {"description": "Invalid credentials or password"}},
)
def user_login(
    user: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(database.get_db),
):
    """Get the useremail and password check it in the.
    database and create and return a jwt token"""
    # check if the username enter is in the database
    user_details = (
        db.query(user_models.User)
        .filter(user_models.User.email == user.username)
        .first()
    )

    # if the user email is not in the database
    if not user_details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Credentials"
        )

    # verify the password
    if not Hash.verify(user_details.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid password"
        )

    user_id = user_details.id  # current user_id

    # if the useremail is in the database and the password is verified
    # set the time the token will exipre
    access_token_expire = timedelta(
        hours=ACCESS_TOKEN_EXPIRE_HOUR
    )  # then the user will have to login again
    # #generate the jwt token
    # #by passing in the data and the expire token time
    access_token = user_oauth2.create_access_token(
        data={
            "sub": user.username, "id": user_id
            }, expires_delta=access_token_expire
    )
    logout_crud.delete_logged_out_user(user_id=user_id, session=db)
    return {
        "access_token": access_token,
        "type": "bearer",
        "user_id": user_id,
    }
