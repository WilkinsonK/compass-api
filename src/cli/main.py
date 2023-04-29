import click
import uvicorn


@click.group()
def main_cli():
    """Manage the Compass API"""


@main_cli.command()
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
@click.option(
    "--reload",
    is_flag=True,
    default=False,
    help="Enable auto-reload."
)
def start(*, host: str, port: str, reload: bool):
    """Starts the API server instance."""

    uvicorn.run("api:api_main", host=host, port=port, reload=reload)


if __name__ == "__main__":
    exit(main_cli())
