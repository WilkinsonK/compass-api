from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import MappedColumn, mapped_column, relationship
from sqlalchemy.ext.declarative import declared_attr

import config
from common import datetime_t, UUID_t

if config.DEVELOPMENT_MODE:
    from sqlalchemy import Uuid as UUID
else:
    from sqlalchemy import UUID #type: ignore[assignment]

MappedUUID = Mapped[UUID_t]
MappedUUIDColumn = MappedColumn[UUID_t]
MappedStr = Mapped[str]


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

    @declared_attr #type: ignore[arg-type]
    def owner_id(cls) -> UUID_t:
        return mapped_column("owner_id", ForeignKey("users.id")) #type: ignore[return-value]
    
    @declared_attr
    def users(cls):
        return relationship("User", back_populates=cls.__tablename__)
