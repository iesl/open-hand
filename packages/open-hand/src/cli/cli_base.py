from click.core import Context
import click
from click.core import Context
from lib.predef.config import setenv


@click.group()
@click.option("--remote", "-x", is_flag=True, help="run command on server")
@click.option("--env", type=click.Choice(["test", "dev", "prod"]), default="dev", help="Check that config is valid")
@click.pass_context
def cli(ctx: Context, remote: bool, env: str):
    print(f"Env set to {env}")
    setenv(env)
    ctx.ensure_object(dict)
    ctx.obj["remote"] = remote
