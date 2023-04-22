"""Global configuration for this project."""

import enum, os, pathlib, uuid

import dotenv

import common

__version__ = (0, 0, 0)

# Load environment from .env file if there is one.
dotenv.load_dotenv()


# General purpose settings.
class DevMode(enum.IntFlag):
    """
    Determines how this application behaves.

    DISABLED: run as production mode without any
    auxiliary features running.

    BASIC: run with some features running/changed
    to be compatible on local machine.

    DEBUG: run same as BASIC mode but with
    with addtional output and metrics.
    """

    DISABLED = enum.auto()
    BASIC = enum.auto()
    DEBUG = enum.auto()


DEV_DISABLED = DevMode.DISABLED
DEV_BASIC = DevMode.BASIC
DEV_DEBUG = DevMode.DEBUG

DEVELOPMENT_MODE =\
    DevMode[os.getenv("COMPASS_DEVELOPMENT_MODE", "DISABLED").upper()]

SECURITY_PASSWORD_HASHES = ()
SECURITY_SESSION_TTL = {"minutes": 30}

# Application specific constants. These are not
# meant to change at runtime in prodution.
APPLICATION_ROOT = pathlib.Path(__file__).parents[1]
APPLICATION_UUID =\
    uuid.UUID(bytes=os.getenv("COMPASS_UUID", "0000000000000000").encode())
APPLICATION_PASSWORD =\
    common.rotate_password_hash(b"asdf1234", *SECURITY_PASSWORD_HASHES)
APPLICATION_USERNAME = "CompassAdmin"

# Database ORM related settings
ORM_USERNAME = os.getenv("COMPASS_ORM_USERNAME", None)
ORM_PASSWORD = os.getenv("COMPASS_ORM_PASSWORD", None)
ORM_HOSTNAME = os.getenv("COMPASS_ORM_HOSTNAME", None)
ORM_DATABASE = os.getenv("COMPASS_ORM_DATABASE", None)

# Logging related settings
LOGGING_CONFIG = os.getenv("COMPASS_LOG_CONFIG", None)
