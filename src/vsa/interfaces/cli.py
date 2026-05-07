import click
from vsa.config.settings import load_settings
from vsa.interfaces.logging_setup import setup_logging

@click.group()
@click.option("--env", type=click.Choice(["development", "staging", "production"]), default="development")
@click.option("--log-level", type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]), default="INFO")
@click.pass_context
def cli(ctx, env, log_level):
    """Video Sales Automation Phase2-Core CLI."""
    settings = load_settings()
    settings.env = env
    settings.log_level = log_level
    logger = setup_logging(settings)
    ctx.ensure_object(dict)
    ctx.obj["settings"] = settings
    ctx.obj["logger"] = logger

@cli.command()
@click.option("--source", type=click.Choice(["phase1"]), required=True)
@click.option("--mode", type=click.Choice(["dry-run", "validate", "execute"]), default="dry-run")
@click.pass_context
def migrate(ctx, source, mode):
    """Migrate data from legacy systems to Master Leads."""
    logger = ctx.obj["logger"]
    logger.msg("migrate command started", source=source, mode=mode)
    click.echo(f"Migration from {source} in {mode} mode")

@cli.command()
@click.option("--action", type=click.Choice(["fetch", "plan", "crawl"]), required=True)
@click.option("--lead-id", type=str, default=None)
@click.pass_context
def sync(ctx, action, lead_id):
    """Synchronize Master Leads with external sources."""
    logger = ctx.obj["logger"]
    logger.msg("sync command started", action=action, lead_id=lead_id)
    click.echo(f"Sync action: {action}")
    if lead_id:
        click.echo(f"For lead: {lead_id}")

@cli.command()
@click.pass_context
def version(ctx):
    """Show version information"""
    from vsa import __version__
    click.echo(f"VSA Phase2-Core version {__version__}")

def main():
    """Entry point for the CLI"""
    cli()

if __name__ == "__main__":
    main()
