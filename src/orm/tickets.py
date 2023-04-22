import enum

from sqlalchemy import ForeignKey, String

from orm.bases import declared_attr, mapped_column, relationship
from orm.bases import BaseObject, EnumMixIn, HistoricalMixIn, IdMixIn
from orm.bases import UserOwnerMixIn


# Dummy types. We replace these in other object
# files.


# --------------------------------------------- #
# Ticket Objects.
# --------------------------------------------- #
class TicketKind(EnumMixIn, BaseObject):
    __tablename__ = "ticket_kinds"
    # Kinds:
    # INCIDENT
    # SERVICE


class TicketKindEnum(enum.StrEnum):
    INCIDENT = enum.auto()
    SERVICE = enum.auto()


class TicketStatus(EnumMixIn, BaseObject):
    __tablename__ = "ticket_status"
    # Kinds:
    # UNASSIGNED
    # ASSIGNED
    # BLOCKED
    # TESTED
    # SCHEDULED
    # COMPLETED


class TicketStatusEnum(enum.StrEnum):
    UNASSIGNED = enum.auto()
    ASSIGNED = enum.auto()
    BLOCKED = enum.auto()
    TESTED = enum.auto()
    SCHEDULED = enum.auto()
    COMPLETED = enum.auto()


class ServiceTicket(IdMixIn, HistoricalMixIn, UserOwnerMixIn, BaseObject):
    __tablename__ = "service_tickets"

    @declared_attr
    def short_description(cls):
        return mapped_column("short_description", String(64))

    @declared_attr
    def long_description(cls):
        return mapped_column("long_description", String(512))

    @declared_attr
    def kind(cls):
        return mapped_column("kind", ForeignKey("ticket_kinds.name"))

    @declared_attr
    def status(cls):
        return mapped_column("status", ForeignKey("ticket_status.name"))

    # Object relationships
    @declared_attr
    def messages(cls):
        return relationship\
        (
            "Message",
            collection_class=list,
            back_populates="service_tickets",
            cascade="all, delete-orphan"
        )
