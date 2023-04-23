from fastapi import FastAPI, Request

import api.oauth, common, config, orm


STARTUP_TASKS =\
(
    lambda: orm.initialize(),
)

app = FastAPI\
(
    debug=(config.DEVELOPMENT_MODE is config.DEV_DEBUG),
    on_startup=STARTUP_TASKS
)


@app.get("/")
async def root():
    return {"message": "OK"}


@app.post("/token")
async def login(
    form_data: api.oauth.RequiresAuthForm, request: Request):
    """Attempt to authenticate as some user."""

    session = await api.oauth.authenticate_user_form(form_data, request)
    return\
    {
        "acces_token": common.encode_token(session.id),
        "token_type": "bearer"
    }


@app.get("/users/me")
async def read_users_me(
    current_user: api.oauth.RequiresCurrentUser):
    """Get the current user session."""

    return current_user
