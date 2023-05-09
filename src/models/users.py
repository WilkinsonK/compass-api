from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

import common, config
from models import digest, orm, pyd


def create_new_user(
    password: str | bytes,
    username: str,
    email_address: str,
    first_name: str | None = None,
    last_name: str | None = None,
    role: orm.users.UserRoleEnum | None = None,
    status: orm.users.UserStatus | None = None):

    init_time = common.current_timestamp()
    user_id = common.new_uuid()
    user_password =\
    (
        password if isinstance(bytes)
        else common.rotate_password_hash(config.SECURITY_PASSWORD_HASHES)
    )

    with orm.orm_session() as session:
        email_addresses = session.scalar\
        (
            orm.select(orm.users.UserEmail)
                .where(orm.users.UserEmail.value == email_address)
        )
        if email_addresses:
            raise HTTPException\
            (
                status_code=409,
                detail=f"User already exists with email {email_address}"
            )

    pyd_user = pyd.users.UserM\
    (
        id=user_id,
        role=(role or pyd.users.UserRoleEnum.AUTHORIZED),
        status=(status or pyd.users.UserStatusEnum.UNVERIFIED),
        is_active=False,
        hashed_password=user_password,
        user_contacts=pyd.users.UserContactM
        (
            owner_id=user_id,
            username=username,
            first_name=(first_name or ""),
            last_name=(last_name or ""),
            user_email_addresses=
            [
                pyd.users.UserEmailM
                (
                    id=common.new_uuid(),
                    owner_id=user_id,
                    value=email_address,
                    created_at=init_time,
                    updated_on=init_time
                )
            ],
            created_at=init_time,
            updated_on=init_time
        ),
        user_sessions=[],
        service_tickets=[],
        created_at=init_time,
        updated_on=init_time
    )

    with orm.orm_session() as session:
        try:
            session.add(digest.consume_user2orm(pyd_user))
            session.commit()
        except IntegrityError as e:
            session.rollback()
            raise e from HTTPException\
            (
                status_code=409,
                detail="User already exists."
            )
        
    return pyd_user


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

    stmt = orm.select(orm.users.User)

    # Filtering username and hashed passwords.
    if username:
        stmt = (stmt
            .join(orm.users.UserContact)
            .where(orm.users.UserContact.username == username))
    if hashed_password:
        stmt = (stmt
            .where(orm.users.User.hashed_password == hashed_password))
    if user_id:
        stmt = (stmt
            .where(orm.users.User.id == common.parse_uuid(user_id)))
    if session_id:
        stmt = (stmt
            .join(orm.users.UserSession)
            .where(orm.users.UserSession.id == session_id))

    users = []
    with orm.orm_session() as session:
        for user in session.scalars(stmt):
            user = digest.consume_orm_object(user)
            users.append(user)

    if len(users) > 1 and expects_unique:
        raise ValueError\
        (
            "Possible collision detected between "
            "users when expecting only one."
        )

    return [pyd.users.UserM(**user) for user in users]
