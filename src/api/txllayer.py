"""
Pydantic2SQLAlchemy translation layer and
interface.
"""

import dataclasses, typing
from uuid import UUID

from fastapi import HTTPException, Request
from sqlalchemy.exc import IntegrityError

import common, config, models, orm


def consume_orm_object(obj: orm.bases.BaseObject):
    """
    Breaks down an ORM object into a python
    mapping.
    """

    return dataclasses.asdict(obj)


def consume_pyd_object(
        obj: models.bases.CompassModel | typing.Any,
        *,
        blacklist: typing.Iterable[str] | None = None) -> dict[str, typing.Any]:
    """
    Breaks down a Pydantic model object into a
    python mapping.
    """

    obj = obj.dict()
    for name, value in obj.items():
        if isinstance(value, models.bases.CompassModel):
            obj[name] = consume_pyd_object(value)
    return common.sanitize_dict(obj, blacklist)


def consume_orm2pyd(
        obj: orm.bases.BaseObject,
        pyd_cls: type[models.bases.CompassModel]):
    """Digests some ORM into a model instance."""

    return pyd_cls(**consume_orm_object(obj))


def consume_pyd2orm(
        obj: models.bases.CompassModel,
        orm_cls: type[orm.bases.BaseObject]):
    """
    Digests some model into an ORM instance.
    """

    return orm_cls(**consume_pyd_object(obj))


def consume_user2orm(user: models.users.UserM):
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
    """Consume some User ORM into User model."""

    return models.users.UserM(**consume_orm_object(user))


def do_user_lookup(
        username: str | None = None,
        hashed_password: bytes | None = None,
        user_id: str | UUID | None = None,
        session_id: bytes = None,
        *,
        expects_unique: bool | None = None):
    """
    Queries the database for users that match
    the given parameters.
    """

    stmt = (
        orm.select(orm.users.User)
            .where(orm.users.UserContact.owner_id == orm.users.User.id))

    # Filtering username and hashed passwords.
    if username:
        stmt = stmt.where(orm.users.UserContact.username == username)
    if hashed_password:
        stmt = stmt.where(orm.users.User.hashed_password == hashed_password)
    if user_id:
        stmt = stmt.where(
            orm.users.User.id == common.parse_uuid(user_id))
    if session_id:
        stmt = stmt.where(orm.users.UserSession.id == session_id)

    users = []
    with orm.orm_session() as session:
        for user in session.scalars(stmt):
            user = consume_orm_object(user)
            users.append(user)

    if len(users) > 1 and expects_unique:
        raise ValueError\
        (
            "Possible collision detected between "
            "users when expecting only one."
        )

    return [models.users.UserM(**user) for user in users]


def create_new_session(user: models.users.UserM, request: Request):
    pyd_session = models.users.UserSessionM\
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

    values = consume_orm_object(user)
    for field in ("user_contacts", "user_sessions", "service_tickets"):
        values.pop(field)

    stmt = (orm.update(user.__class__)
            .where(user.__class__.id == user.id)
            .values(values))

    # TODO: Need to update at the user level.
    with orm.orm_session() as session:
        try:
            session.add(consume_pyd2orm(pyd_session, orm.users.UserSession))
            session.execute(stmt)
        except IntegrityError as e:
            raise e from HTTPException\
            (
                status_code=409,
                detail="Session already exists."
            )
        session.commit()

    return pyd_session


def validate_sessions(
        user: models.users.UserM,
        session_id: str | UUID | None = None,
        request: Request | None = None):
    """
    Validates all sessions available to the given
    user.

    If a `request` is passed, and a specific
    `session_id` is passed too, refresh that
    session.

    Any sessions that have expired are considered
    invalid and are removed.
    """

    common.validate_dependant_args(session_id=session_id, request=request)
    user = consume_user2orm(user)
    session_cls = orm.users.UserSession
    bad_orm_sessions = [] # Just the session ids

    sel_stmt = (orm.select(session_cls)
            .where(session_cls.owner_id == user.id))
    del_stmt = (orm.delete(session_cls)
            .where(session_cls.id in bad_orm_sessions))

    if session_id:
        sel_stmt = sel_stmt.where\
        (
            session_cls.id == session_id,
            session_cls.ipaddress == request.client.host
        )

    with orm.orm_session() as session:
        for orm_session in session.scalars(sel_stmt):
            if orm_session.invalid_on <= common.current_timestamp():
                bad_orm_sessions.append(orm_session.id)
                continue

        session.execute(del_stmt)
        session.commit()
