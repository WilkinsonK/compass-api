"""
Pydantic2SQLAlchemy translation layer and
interface.
"""

import dataclasses, typing
from uuid import UUID

from fastapi import Request

import common, config, models, orm


def consume_orm_object(obj: orm.bases.BaseObject):
    """
    Breaks down an ORM object into a python
    mapping.
    """

    return dataclasses.asdict(obj)


def consume_pyd_object(
        obj: models.bases.CompassModel | typing.Any) -> dict[str, typing.Any]:
    """
    Breaks down a Pydantic model object into a
    python mapping.
    """

    obj = obj.dict()
    for name, value in obj.items():
        if isinstance(value, models.bases.CompassModel):
            obj[name] = consume_pyd_object(value)
    return obj


def consume_user2orm(user: models.users.User):
    """Consume some User model into User ORM."""

    user = consume_pyd_object(user)
    user["user_contacts"] = orm.users.UserContact(**user["user_contacts"])

    # Iter through sessions and ensure all are
    # consumed into ORM objects.
    for idx, session in enumerate(user["user_sessions"]):
        user["user_sessions"][idx] = orm.users.UserSession(**session)

    # Iter through service_tickets and do the
    # same as sessions.
    for idx, ticket in enumerate(user["service_tickets"]):
        user["service_tickets"][idx] = orm.tickets.ServiceTicket(**ticket)

    return orm.users.User(**user)


def consume_user2pyd(user: orm.users.User):
    """Consume some Users ORM into User model."""

    return models.users.User(**consume_orm_object(user))


def do_user_lookup(
        username: str | None = None,
        hashed_password: bytes | None = None,
        user_id: str | UUID | None = None,
        session_id: str | UUID | None = None):
    """
    Queries the database for users that match
    the given parameters.
    """

    def str_or_uuid(value):
        if isinstance(value, str):
            return UUID(value)
        return value

    stmt = (
        orm.select(orm.users.User)
            .where(orm.users.UserContact.owner_id == orm.users.User.id))

    # Filtering username and hashed passwords.
    if username:
        stmt = stmt.where(orm.users.UserContact.username == username)
    if hashed_password:
        stmt = stmt.where(orm.users.User.hashed_password == hashed_password)
    if user_id:
        stmt = stmt.where(orm.users.User.id == str_or_uuid(user_id))
    if session_id:
        stmt = stmt.where(orm.users.User.id == str_or_uuid(session_id))

    users = []
    with orm.orm_session() as session:
        for user in session.scalars(stmt):
            user = consume_orm_object(user)
            users.append(user)

    return [models.users.User(**user) for user in users]


def create_new_session(user: models.users.User, request: Request):
    pyd_session = models.users.UserSession\
    (
        id=common.new_session_token(user.id),
        owner_id=user.id,
        ipaddress=request.client.host,
        created_at=common.current_timestamp(),
        updated_on=common.current_timestamp(),
        invalid_on=common.future_timestamp(**config.SECURITY_SESSION_TTL),
    )
    user.user_sessions.append(pyd_session)
    user = consume_user2orm(user)

    print(consume_orm_object(user))
    stmt = (
        orm.update(orm.users.User)
            .where(orm.users.User.id == user.id)
            .values(**consume_orm_object(user)))

    with orm.orm_session() as session:
        session.execute(stmt)

    return pyd_session
