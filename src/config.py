"""Global configuration for this project."""

import enum, os, pathlib

import dotenv

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

DEVELOPMENT_MODE = DevMode[os.getenv("DEVELOPMENT_MODE", "DISABLED").upper()]
APPLICATION_ROOT = pathlib.Path(__file__).parents[1]

# Database ORM related settings
ORM_USERNAME = os.getenv("ORM_USERNAME", None)
ORM_PASSWORD = os.getenv("ORM_PASSWORD", None)
ORM_HOSTNAME = os.getenv("ORM_HOSTNAME", None)
ORM_DATABASE = os.getenv("ORM_DATABASE", None)

# Logging related settings
LOGGING_CONFIG = os.getenv("COMPASS_LOG_CONFIG", None)
