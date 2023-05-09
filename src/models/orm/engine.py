import contextlib

import sqlalchemy, sqlalchemy.orm
from sqlalchemy import select, update, delete

import config

__all__ =\
(
    "select",
    "update",
    "orm_engine",
    "orm_session"
)

# Determines the connection_string used in our
# ORM. If in development mode, creates a SQLite
# database; in memory by default but can be made
# persistent if ORM_DATABASE is set.
if config.DEVELOPMENT_MODE in config.DEV_BASIC | config.DEV_DEBUG:
    connection_string = f"sqlite:///" + (config.ORM_DATABASE or ":memory:")
else:
    connection_string = (
    (
        "postgres+psycopg://"
        f"{config.ORM_USERNAME}:{config.ORM_PASSWORD}"
        "@"
        f"{config.ORM_HOSTNAME}/{config.ORM_DATABASE}"
    ))

# For saftey, delete the connection_string and
# the ORM_PASSWORD config value. Since we no
# longer need these values, there's no need to
# hold their reference.
_orm_engine = sqlalchemy.create_engine\
(
    connection_string,
    echo=(config.DEVELOPMENT_MODE is config.DEV_DEBUG),
    future=True
)
del connection_string
del config.ORM_PASSWORD # Drop reference to password.


def orm_engine():
    """
    Get ORM engine used in this application.
    """

    return _orm_engine


@contextlib.contextmanager
def orm_session(**kwds):
    """Opens a session with the ORM engine."""

    with sqlalchemy.orm.Session(orm_engine(), **kwds) as session:
        yield session
