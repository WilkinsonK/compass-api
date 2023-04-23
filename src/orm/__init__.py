"""
Management tools and objects for database ORM.
"""

from datetime import datetime

from sqlalchemy.exc import IntegrityError

import common, config, orm
from orm import bases, messages, tickets, users
from orm.engine import orm_engine, orm_session, select, update, delete

__all__ = (
(
    "messages",
    "tickets",
    "users",
    "initialize",
    "orm_engine",
    "orm_session",
    "select",
    "update",
    "delete"
))


def initialize():
    """
    Creates all the tables for the database.
    """

    orm.bases.BaseObject.metadata.create_all(orm_engine())

    members = lambda e: [m for m in e.__members__]
    enum_pairs =\
    (
        (orm.users.UserRole, orm.users.UserRoleEnum),
        (orm.users.UserStatus, orm.users.UserStatusEnum),
        (orm.tickets.TicketKind, orm.tickets.TicketKindEnum),
        (orm.tickets.TicketStatus, orm.tickets.TicketStatusEnum)
    )

    record_buffer = []

    # Create all enumerators records instances.
    for otype, etype in enum_pairs:
        record_buffer.extend([otype(name=value) for value in members(etype)])

        # Initialize Enumeration objects.
        # TODO: automate the below.
        with orm_session() as session:
            try:
                session.add_all(record_buffer)
                session.commit()
            except IntegrityError:
                session.rollback()

        # Refresh the record buffer.
        record_buffer.clear()

    # Builds the initial administrator instance.
    init_time = common.current_timestamp()
    admin_inst = orm.users.User\
    (
        id=config.APPLICATION_UUID,
        role="administrator",
        status="enabled",
        is_active=True,
        hashed_password=config.APPLICATION_PASSWORD,
        user_contacts=orm.users.UserContact
        (
            owner_id=config.APPLICATION_UUID,
            username=config.APPLICATION_USERNAME,
            first_name="",
            last_name="",
            phone_number="",
            user_email_addresses=[],
            created_at=init_time,
            updated_on=init_time
        ),
        user_sessions=[],
        service_tickets=[],
        created_at=init_time,
        updated_on=init_time
    )

    with orm_session() as session:
        try:
            session.add(admin_inst)
            session.commit()
        except IntegrityError:
            session.rollback()
