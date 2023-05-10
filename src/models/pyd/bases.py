import typing

from pydantic import Field

from common import datetime_t, UUID_t
from models.bases import PYDBase

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


class HistoricalModel(PYDBase):
    created_at: DateTimeField
    updated_on: DateTimeField
