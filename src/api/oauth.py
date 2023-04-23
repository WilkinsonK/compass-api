import base64
import typing

from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# Only import the Pydantic `models` at this level.
# Any interactions with the orm should happen at
# the txllayer.
import api.txllayer, common, config, models
from api.app import api_main

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
RA = typing.TypeVar("RA")
RequiresAuth = typing.Annotated[RA, Depends(oauth2_scheme)]
RequiresAuthForm = typing.Annotated[OAuth2PasswordRequestForm, Depends()]


def user_can_request_session(user: models.users.UserM):
    """
    Validates the number of sessions a User has.
    """

    return ((len(user.user_sessions) + 1) <= config.SECURITY_MAX_SESSIONS)


async def authenticate_user_form(
        form: RequiresAuthForm,
        request: Request,
        *,
        hash_package: common.HashPackage | None = None):
    """
    Given input from a password request form,
    perform a user lookup to see if any users
    match.
    """

    users = api.txllayer.do_user_lookup\
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
    api.txllayer.validate_sessions(users[0])
    if not user_can_request_session(users[0]):
        raise HTTPException\
        (
            status_code=403, # Forbidden
            detail="Too many active sessions."
        )

    session = api.txllayer.create_new_session(users[0], request)
    return session


async def get_current_user(token: RequiresAuth[bytes]):
    token = common.decode_token(token)
    users = api.txllayer.do_user_lookup(session_id=token)
    if not users:
        raise HTTPException\
        (
            status_code=400,
            detail="Invalid authentication credentials.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    status = models.users.UserStatusEnum(users[0].status)
    enabled = models.users.UserStatusEnum.ENABLED
    if status is not enabled:
        raise HTTPException\
        (
            status_code=403,
            detail="Not allowed to access this service.",
        )
    
    if not users[0].is_active:
        raise HTTPException\
        (
            status_code=401,
            detail="Not active user.",
        )

    return users[0]


RequiresCurrentUser =\
    typing.Annotated[models.users.UserM, Depends(get_current_user)]


@api_main.post("/token")
async def login(
    form_data: RequiresAuthForm, request: Request):
    """Attempt to authenticate as some user."""

    session = await authenticate_user_form(form_data, request)
    return\
    {
        "acces_token": common.encode_token(session.id),
        "token_type": "bearer"
    }
