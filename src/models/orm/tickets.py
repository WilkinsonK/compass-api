import enum

from sqlalchemy import ForeignKey, String

from models.bases import ORMBase
from models.orm.bases import mapped_column, relationship
from models.orm.bases import EnumMixIn, HistoricalMixIn, IdMixIn
from models.orm.bases import UserOwnerMixIn, MappedStr


# Dummy types. We replace these in other object
# files.


# --------------------------------------------- #
# Ticket Objects.
# --------------------------------------------- #
class TicketKind(EnumMixIn, ORMBase):
    __tablename__ = "ticket_kinds"
    # Kinds:
    # INCIDENT
    # SERVICE


class TicketKindEnum(enum.StrEnum):
    INCIDENT = enum.auto()
    SERVICE = enum.auto()


class TicketStatus(EnumMixIn, ORMBase):
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


class ServiceTicket(IdMixIn, HistoricalMixIn, UserOwnerMixIn, ORMBase):
    __tablename__ = "service_tickets"

    short_description: MappedStr = mapped_column("short_description", String(64))
    long_description: MappedStr = mapped_column("long_description", String(512))
    kind: MappedStr = mapped_column("kind", ForeignKey("ticket_kinds.name"))
    status: MappedStr = mapped_column("status", ForeignKey("ticket_status.name"))

    # Object relationships
    messages: MappedStr = relationship\
        (
            "Message",
            collection_class=list,
            back_populates="service_tickets",
            cascade="all, delete-orphan"
        )
