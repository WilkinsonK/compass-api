import typing
from uuid import UUID as UUID_t

from datetime import datetime as datetime_t
from pydantic import BaseConfig , BaseModel, Field

__all__ = (
    "CompassModel",
    "HistoricalModel",
    "Field"
)

T = typing.TypeVar("T")
UUIDField = typing.Annotated[UUID_t, Field()]
DateTimeField = typing.Annotated[datetime_t, Field()]


def VarCharField(_type: type[T], size: int, **kwds):
    return typing.Annotated[_type, Field(max_length=size, **kwds)]


class CompassModel(BaseModel):

    class Config(BaseConfig):
        orm_mode = True
        use_enum_values = True


class HistoricalModel(CompassModel):
    created_at: DateTimeField
    updated_on: DateTimeField
