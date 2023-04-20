from fastapi import FastAPI

import config, orm


STARTUP_TASKS =\
(
    lambda: orm.initialize(),
)

app = FastAPI\
(
    debug=(config.DEVELOPMENT_MODE is config.DEV_DEBUG),
    on_startup=STARTUP_TASKS
)
