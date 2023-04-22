import typing

from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

import api.txlayer, common, models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
RA = typing.TypeVar("RA")
RequiresAuth = typing.Annotated[RA, Depends(oauth2_scheme)]
RequiresAuthForm = typing.Annotated[OAuth2PasswordRequestForm, Depends()]


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

    users = api.txlayer.do_user_lookup\
    (
        form.username,
        common.rotate_password_hash(form.password, *(hash_package or []))
    )

    if not users or len(users) > 1:
        raise HTTPException\
        (
            status_code=400,
            detail="Incorrect username or password."
        )

    session = api.txlayer.create_new_session(users[0], request)
    return session


async def get_current_user(token: RequiresAuth[str], request: Request):
    users = api.txlayer.do_user_lookup(user_id=token)
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
            status_code=401,
            detail="User is not enabled",
        )
    
    return users[0]


RequiresCurrentUser =\
    typing.Annotated[models.users.User, Depends(get_current_user)]
