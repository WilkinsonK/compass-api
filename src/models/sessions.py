from uuid import UUID

from fastapi import HTTPException, Request
from sqlalchemy.exc import IntegrityError

import common, config
from models import digest, orm, pyd


def create_new_session(user: pyd.users.UserM, request: Request):
    pyd_session = pyd.users.UserSessionM\
    (
        id=common.new_session_token(user.id),
        owner_id=user.id,
        ipaddress=request.client.host,
        created_at=common.current_timestamp(),
        updated_on=common.current_timestamp(),
        invalid_on=common.future_timestamp(**config.SECURITY_SESSION_TTL),
    )
    user.user_sessions.append(pyd_session)
    user = digest.consume_user2orm(user)

    values = digest.consume_orm_object(user)
    for field in ("user_contacts", "user_sessions", "service_tickets"):
        values.pop(field)

    stmt = (orm.update(user.__class__)
            .where(user.__class__.id == user.id)
            .values(values))

    # TODO: Need to update at the user level.
    with orm.orm_session() as session:
        try:
            session.add\
            (digest.consume_pyd2orm(pyd_session, orm.users.UserSession))
            session.execute(stmt)
        except IntegrityError as e:
            session.rollback()
            raise e from HTTPException\
            (
                status_code=409,
                detail="Session already exists."
            )
        session.commit()

    return pyd_session


def validate_user_sessions(
        user: pyd.users.UserM,
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
    user = digest.consume_user2orm(user)
    session_cls = orm.users.UserSession
    bad_orm_sessions = [] # Just the session ids

    sel_stmt = (orm
            .select(session_cls)
            .where(session_cls.owner_id == user.id))
    del_stmt = orm.delete(session_cls)

    if session_id:
        sel_stmt = sel_stmt.where\
        (
            session_cls.id == common.parse_uuid(session_id),
            session_cls.ipaddress == request.client.host
        )

    with orm.orm_session() as session:
        for orm_session in session.scalars(sel_stmt):
            if orm_session.invalid_on <= common.current_timestamp():
                bad_orm_sessions.append(orm_session.id)
                continue

        for session_id in bad_orm_sessions:
            session.execute(
                del_stmt.where(orm.users.UserSession.id == session_id))
        session.commit()
