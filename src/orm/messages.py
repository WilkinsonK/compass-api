import typing

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from orm.bases import BaseObject, HistoricalObject
from orm.bases import UUID, UUID_t

# Dummy types. We replace these in other object
# files.
ServiceTicket = typing.NewType("ServiceTicket", object)
User = typing.NewType("User", object)


# --------------------------------------------- #
# Message Objects.
# --------------------------------------------- #
class Message(HistoricalObject, BaseObject):
    __tablename__ = "messages"

    id: Mapped[UUID_t] = mapped_column(UUID(), primary_key=True)
    ticket_id: Mapped["ServiceTicket"] = mapped_column\
            (ForeignKey("service_tickets.id"))
    owner_id: Mapped["User"] = mapped_column(ForeignKey("users.id"))
    content: Mapped[str] = mapped_column(String(512))

    # Object relationships
    service_tickets: Mapped["ServiceTicket"] = relationship\
        (back_populates="messages")
