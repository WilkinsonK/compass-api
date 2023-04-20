import click
import uvicorn


@click.group()
def main():
    """Manage the Compass API"""


@main.command()
@click.option(
    "--host",
    type=str,
    default="127.0.0.1",
    help="Bind socket to this host.",
    show_default=True,
)
@click.option(
    "--port",
    type=int,
    default=8000,
    help="Bind socket to this port.",
    show_default=True,
)
def start(*, host: str, port: str):
    """Starts the API server instance."""
    uvicorn.run("api:app", host=host, port=port)
