import typing
from datetime import datetime as datetime_t
from uuid import UUID as UUID_t

from sqlalchemy import DateTime, ForeignKey, String, UUID
from sqlalchemy.orm import MappedAsDataclass, DeclarativeBase, Mapped
from sqlalchemy.orm import MappedColumn, mapped_column, relationship
from sqlalchemy.ext.declarative import declared_attr

import config

if config.DEVELOPMENT_MODE:
    from sqlalchemy import Uuid as UUID

MappedUUID = Mapped[UUID_t]
MappedUUIDColumn = MappedColumn[UUID_t]
MappedStr = Mapped[str]


class BaseObject(MappedAsDataclass, DeclarativeBase):

    def __repr__(self):
        fields = self.__annotations__.keys()
        fields = " ".join([f"{f}={getattr(self, f)}" for f in fields])
        return f"{self.__class__.__name__}[{fields}]"
    

class EnumMixIn(object):

    name: MappedStr = mapped_column("name", String(16), primary_key=True)

    def __repr__(self):
        return "ENUM:" + super().__repr__()


class HistoricalMixIn(object):
    created_at: Mapped[datetime_t] = mapped_column\
    (
        "created_on",
        DateTime(False),
    )

    updated_on: Mapped[datetime_t] = mapped_column\
    (
        "updated_on",
        DateTime(False)
    )


class IdMixIn(object):
    id: MappedUUID = mapped_column("id", UUID(True), primary_key=True)


class UserOwnerMixIn(object):

    @declared_attr
    def owner_id(cls) -> UUID_t:
        return mapped_column("owner_id", ForeignKey("users.id"))
    
    @declared_attr
    def users(cls):
        return relationship("User", back_populates=cls.__tablename__)
