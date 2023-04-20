"""
Management tools and objects for database ORM.
"""

from orm import bases, messages, tickets, users
from orm.engine import orm_engine, orm_session, select

__all__ = (
(
    "messages",
    "tickets",
    "users",

    "initialize",
    "orm_engine",
    "orm_session",
    "select"
))


def initialize():
    """
    Creates all the tables for the database.
    """

    bases.BaseObject.metadata.create_all(orm_engine())

    members = lambda e: [m for m in e.__members__]
    enum_pairs =\
    (
        (users.UserRole, users.UserRoleEnum),
        (users.UserStatus, users.UserStatusEnum),
        (tickets.TicketKind, tickets.TicketKindEnum),
        (tickets.TicketStatus, tickets.TicketStatusEnum)
    )

    record_buffer = []

    # Create all enumerators records instances.
    for otype, etype in enum_pairs:
        record_buffer.extend([otype(name=value) for value in members(etype)])

        # Initialize Enumeration objects.
        # TODO: automate the below.
        with orm_session() as session:
            session.add_all(record_buffer)
            session.commit()

        # Refresh the record buffer.
        record_buffer.clear()
