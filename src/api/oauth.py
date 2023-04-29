import typing

from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# Only import the Pydantic `models` at this level.
# Any interactions with the orm should happen at
# the txllayer.
import common, config, models, txllayer
from api.app import api_main

RA = typing.TypeVar("RA")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def decode_token(token: typing.Annotated[RA, Depends(oauth2_scheme)]):
    return common.decode_token(token)


RequiresAuth = typing.Annotated[RA, Depends(decode_token)]
RequiresAuthForm = typing.Annotated[OAuth2PasswordRequestForm, Depends()]


def user_can_request_session(user: models.users.UserM):
    """
    Validates the number of sessions a User has.
    """

    return ((len(user.user_sessions) + 1) <= config.SECURITY_MAX_SESSIONS)


def authenticate_user_form(
        form: RequiresAuthForm,
        request: Request,
        *,
        hash_package: common.HashPackage | None = None):
    """
    Given input from a password request form,
    perform a user lookup to see if any users
    match.
    """

    users = txllayer.do_user_lookup\
    (
        form.username,
        common.rotate_password_hash(form.password, *(hash_package or [])),
        expects_unique=True
    )

    if not users:
        raise HTTPException\
        (
            status_code=401,
            detail="Incorrect username or password."
        )

    # If we were to add a new session, would this
    # cause us an issue?
    txllayer.validate_user_sessions(users[0])
    if not user_can_request_session(users[0]):
        raise HTTPException\
        (
            status_code=403, # Forbidden
            detail="Too many active sessions."
        )

    session = txllayer.create_new_session(users[0], request)
    return session


@api_main.post("/token")
async def login(
    form_data: RequiresAuthForm, request: Request):
    """Attempt to authenticate as some user."""

    session = authenticate_user_form(form_data, request)
    return\
    {
        "access_token": common.encode_token(session.id),
        "expires_on": session.invalid_on,
        "token_type": "bearer"
    }
