import base64, datetime, functools, logging, secrets, sys, uuid
import typing

HashAlgorithm = typing.Callable[[str | bytes], bytes]
HashPackage = typing.Iterable[HashAlgorithm]


def basic_password_hash(password: str | bytes) -> bytes:
    if isinstance(password, bytes):
        return password
    return password.encode()


def current_timestamp():
    """Gets the current timestamp."""

    return datetime.datetime.now()


def debug(fn):
    """
    Wraps some function with a logger. Reraises
    exceptions with additional information.
    """

    logger = logging.getLogger("uvicorn.error")

    @functools.wraps(fn)
    def inner(*args, **kwds):
        fn_name = fn.__qualname__
        try:
            rt = fn(*args, **kwds)
            logger.info(f"{fn_name} RT value: {rt!r}")
        except Exception as e:
            logger.error(f"{fn_name} failed with args: {args}")
            logger.error(f"{fn_name} failed with kwds: {kwds}")
            raise DebugError(f"failed with exception:", str(e), error=e)

        return rt
    
    return inner


@debug
def decode_token(token: str):
    """Make token consumable by the ORM."""

    return base64.urlsafe_b64decode(token)


@debug
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


class DebugError(Exception):
    
    def __init__(
            self,
            *values: str,
            sep: str | None = None,
            error: Exception | None = None):
        self.message = (sep or " ").join(values)
        self.exception = error

        if error:
            raise error from self

    def __str__(self):
        return self.message
