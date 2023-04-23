from api import oauth
from api.app import api_main

@api_main.get("/users/me")
async def read_users_me(
    current_user: oauth.RequiresCurrentUser):
    """Get the current user session."""

    return current_user
