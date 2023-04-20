from datetime import datetime as datetime_t
from uuid import UUID as UUID_t

from sqlalchemy import DateTime, Integer, String, UUID, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

import config

if config.DEVELOPMENT_MODE:
    from sqlalchemy import Uuid as UUID


class BaseObject(DeclarativeBase):

    def __repr__(self):
        fields = self.__annotations__.keys()
        fields = " ".join([f"{f}={getattr(self, f)}" for f in fields])
        return f"{self.__class__.__name__}[{fields}]"


class HistoricalObject:
    created_at: Mapped[datetime_t] = mapped_column\
    (
        DateTime(False),
        insert_default=func.current_timestamp(),
        default=None
    )
    updated_on: Mapped[datetime_t] = mapped_column\
    (
        DateTime(False),
        insert_default=func.current_timestamp(),
        default=None
    )


class EnumObject:
    value: Mapped[int] = mapped_column\
    (
        Integer,
        primary_key=True,
        autoincrement=True
    )
    name:  Mapped[str] = mapped_column(String(16))

    def __repr__(self):
        return "ENUM:" + super().__repr__()
