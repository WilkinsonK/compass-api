import enum, typing

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from orm.bases import BaseObject, EnumObject, HistoricalObject
from orm.bases import UUID, UUID_t


# Dummy types. We replace these in other object
# files.
Message = typing.NewType("Message", object)
User = typing.NewType("User", object)


# --------------------------------------------- #
# Ticket Objects.
# --------------------------------------------- #
class TicketKind(EnumObject, BaseObject):
    __tablename__ = "ticket_kinds"
    # Kinds:
    # INCIDENT
    # SERVICE


class TicketKindEnum(enum.StrEnum):
    INCIDENT = enum.auto()
    SERVICE = enum.auto()


class TicketStatus(EnumObject, BaseObject):
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


class ServiceTicket(HistoricalObject, BaseObject):
    __tablename__ = "service_tickets"

    id: Mapped[UUID_t] = mapped_column(UUID(), primary_key=True)
    owner_id: Mapped[UUID_t] = mapped_column(ForeignKey("users.id"))
    short_description: Mapped[str] = mapped_column(String(64))
    long_description:  Mapped[str] = mapped_column(String(512))
    kind:   Mapped[str] = mapped_column(ForeignKey("ticket_kinds.name"))
    status: Mapped[str] = mapped_column(ForeignKey("ticket_status.name"))

    # Object relationships
    users: Mapped["User"] = relationship\
        (back_populates="service_tickets")
    messages: Mapped[list["Message"]] = relationship\
        (back_populates="service_tickets", cascade="all, delete-orphan")
