from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.declarative import declared_attr

from models.orm.bases import BaseObject, HistoricalMixIn, IdMixIn, MappedUUID

# Dummy types. We replace these in other object
# files.


# --------------------------------------------- #
# Message Objects.
# --------------------------------------------- #
class Message(IdMixIn, HistoricalMixIn, BaseObject):
    __tablename__ = "messages"

    ticket_id: MappedUUID = mapped_column("ticket_id", ForeignKey("service_tickets.id"))
    owner_id: MappedUUID = mapped_column("owner_id", ForeignKey("users.id"))
    content: MappedUUID = mapped_column("content", String(512))

    # Object relationships
    service_tickets: Mapped[list["ServiceTicket"]] = relationship( #type: ignore
        "ServiceTicket",
        collection_class=list,
        back_populates=__tablename__
    )
