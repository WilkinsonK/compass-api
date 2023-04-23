from fastapi import FastAPI

import config, orm


STARTUP_TASKS =\
(
    lambda: orm.initialize(),
)

api_main = FastAPI\
(
    debug=(config.DEVELOPMENT_MODE is config.DEV_DEBUG),
    on_startup=STARTUP_TASKS
)


@api_main.get("/")
async def root():
    return {"message": "OK"}
