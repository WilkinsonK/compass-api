import typing
from fastapi import HTTPException, Depends

# Only import the Pydantic `models` at this level.
# Any interactions with the orm should happen at
# the txllayer.
import models, txllayer
from api import oauth
from api.app import api_main


async def get_current_user(token: oauth.RequiresAuth[bytes]):
    users = txllayer.do_user_lookup\
    (
        session_id=token,
        expects_unique=True
    )

    if not users:
        raise HTTPException\
        (
            status_code=400,
            detail="Invalid authentication credentials.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user = users[0]
    txllayer.validate_user_sessions(user)

    status = models.users.UserStatusEnum(user.status)
    enabled = models.users.UserStatusEnum.ENABLED
    if status is not enabled:
        raise HTTPException\
        (
            status_code=403,
            detail="Not allowed to access this service.",
        )

    if not user.is_active:
        raise HTTPException\
        (
            status_code=401,
            detail="Not active user.",
        )

    blacklist =\
    (
        "user_contacts",
        "hashed_password",
        "user_sessions",
        "service_tickets"
    )
    return txllayer.consume_pyd_object(user, blacklist=blacklist)


RequiresCurrentUser =\
    typing.Annotated[models.users.UserM, Depends(get_current_user)]


@api_main.get("/users/me")
async def read_users_me(
    current_user: RequiresCurrentUser):
    """Get the current user session."""

    return current_user
