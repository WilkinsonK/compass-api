import base64, datetime, secrets, sys, uuid
import typing

from datetime import datetime as datetime_t # This is proxied from here.
from uuid import UUID as UUID_t # This is proxied from here.

HashAlgorithm = typing.Callable[[str | bytes], bytes]
HashPackage = typing.Iterable[HashAlgorithm]


def basic_password_hash(password: str | bytes) -> bytes:
    if isinstance(password, bytes):
        return password
    return password.encode()


def current_timestamp():
    """Gets the current timestamp."""

    return datetime.datetime.now()


def decode_token(token: str):
    """Make token consumable by the ORM."""

    return base64.urlsafe_b64decode(token)


def encode_token(token: bytes):
    """Make token consumable by the user."""

    return base64.urlsafe_b64encode(token)


def future_timestamp(
        *,
        days: float | None = None,
        seconds: float | None = None,
        microseconds: float | None = None,
        milliseconds: float | None = None,
        minutes: float | None = None,
        hours: float | None = None,
        weeks: float | None = None):
    """
    Gets a timestamp at some time in the future.
    """

    delta = datetime.timedelta\
    (
        days=days or 0.0,
        seconds=seconds or 0.0,
        microseconds=microseconds or 0.0,
        milliseconds=milliseconds or 0.0,
        minutes=minutes or 0.0,
        hours=hours or 0.0,
        weeks=weeks or 0.0
    )

    return current_timestamp() + delta


def new_session_token(_uuid: uuid.UUID | None = None):
    """
    Generates a new token for a user session.
    """

    token = secrets.token_urlsafe(128 if not _uuid else 71)
    if _uuid:
        token = b":".join([_uuid.hex.encode(), token.encode()])
    return token


def new_uuid():
    """
    Generates a new UUID for an object or model.
    """

    return uuid.uuid4()


def parse_uuid(value: str | bytes | uuid.UUID):
    """Parses the given value as a UUID."""

    if isinstance(value, str):
        return uuid.UUID(value)
    if isinstance(value, bytes):
        return uuid.UUID(bytes=value)
    return value


def rotate_password_hash(
        password: str | bytes,
        *hashes: HashAlgorithm) -> bytes:
    """
    Iterates over a sequence of hashing
    algorithms on a single string (password)
    value and returns its result in bytes.
    """

    hashes += (basic_password_hash,)
    for phash in hashes:
        password = phash(password)
    return password


def sanitize_dict(
        mapping: dict[str, typing.Any],
        blacklist: typing.Iterable[str],
        *,
        nested_char: str | None = None):
    """Remove target fields from a mapping."""

    nested_char = nested_char or "."
    for field in blacklist:
        parent, *child = field.split(nested_char, maxsplit=1)
        if child:
            sanitize_dict(mapping[parent], child)
            continue
        mapping.pop(field)

    return mapping


def unsigned(value: int):
    """
    Ensures the passed value does not go below 0.
    Instead, similates integer overflow and loop
    back around to the next largest value
    relative
    to the given value.

    i.e. `-1 == maxsize - 1`
      or `-5 == maxsize - 5`
    and etc.
    """

    if value < 0:
        return sys.maxsize + value
    return value


def validate_dependant_args(**kwds):
    """
    Verifies that if any of the values passed are
    truthy that, then, all values are truthy.
    """

    if not (any(kwds.values()) and not all(kwds.values())):
        return
    present = [name for name, v in kwds.items() if v]
    missing = [name for name, v in kwds.items() if not v]

    raise ValueError\
        (f"{missing} must be included if value(s) {present} are passed")
