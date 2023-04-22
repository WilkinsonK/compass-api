import datetime, secrets, uuid
import typing

HashAlgorithm = typing.Callable[[str | bytes], bytes]
HashPackage = typing.Iterable[HashAlgorithm]


def basic_password_hash(password: str | bytes) -> bytes:
    if isinstance(password, bytes):
        return password
    return password.encode()


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


def new_session_token(_uuid: uuid.UUID | None = None):
    """
    Generates a new token for a user session.
    """

    token = secrets.token_bytes(128 if not _uuid else 111)
    return b":".join([_uuid.bytes, token])


def new_uuid():
    """
    Generates a new UUID for an object or model.
    """

    return uuid.uuid4()


def current_timestamp():
    """Gets the current timestamp."""

    return datetime.datetime.now()


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
        microseconds=microseconds or 0.0,
        milliseconds=milliseconds or 0.0,
        minutes=minutes or 0.0,
        hours=hours or 0.0,
        weeks=weeks or 0.0
    )

    return current_timestamp() + delta
