import functools, logging, pprint

import config


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
            logger.info(f"{fn_name} RT value: {pprint.pformat(rt)}")
        except Exception as e:
            logger.error(f"{fn_name} failed with args: {args}")
            logger.error(f"{fn_name} failed with kwds: {kwds}")
            raise DebugError(f"failed with exception:", str(e), error=e)

        return rt

    if config.DEVELOPMENT_MODE in config.DEV_BASIC | config.DEV_DEBUG:
        return inner
    return fn


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
