import typing

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.declarative import declared_attr

from orm.bases import BaseObject, HistoricalMixIn, IdMixIn

# Dummy types. We replace these in other object
# files.


# --------------------------------------------- #
# Message Objects.
# --------------------------------------------- #
class Message(IdMixIn, HistoricalMixIn, BaseObject):
    __tablename__ = "messages"

    @declared_attr
    def ticket_id(cls):
        return mapped_column("ticket_id", ForeignKey("service_tickets.id"))

    @declared_attr
    def owner_id(cls):
        return mapped_column("owner_id", ForeignKey("users.id"))

    @declared_attr
    def content(cls):
        return mapped_column("content", String(512))

    # Object relationships
    @declared_attr
    def service_tickets(cls):
        return relationship\
        (
            "ServiceTicket",
            collection_class=list,
            back_populates=cls.__tablename__
        )
