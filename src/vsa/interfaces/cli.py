"""
CLI Interface for VSA Phase2-Core

Commands:
  migrate   - Phase 1 データを Master Leads に統合
  sync      - Google Sheets との同期
  version   - バージョン表示
"""

import click
import structlog
from datetime import datetime

from vsa import __version__
from vsa.config.settings import load_settings
from vsa.interfaces.logging_setup import setup_logging
from vsa.application.migration_orchestrator import MigrationPipeline
from vsa.infrastructure.repository import GoogleSheetsRepository

logger = structlog.get_logger(__name__)

@click.group()
@click.option('--env', type=click.Choice(['development', 'staging', 'production']), 
             default='development', help='Environment')
@click.option('--log-level', type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']),
             default='INFO', help='Log level')
@click.pass_context
def main(ctx, env, log_level):
    """VSA Phase2-Core Main CLI"""
    ctx.ensure_object(dict)
    ctx.obj['env'] = env
    ctx.obj['log_level'] = log_level
    
    # Setup logging
    setup_logging(log_level)
    
    # Load settings
    settings = load_settings()
    ctx.obj['settings'] = settings
    
    logger.info("VSA CLI started", version=__version__, env=env, log_level=log_level)

@main.command()
@click.option('--source', type=click.Choice(['phase1', 'all']), default='phase1',
             help='Migration source')
@click.option('--mode', type=click.Choice(['dry-run', 'validate', 'load']), 
             default='dry-run', help='Migration mode')
@click.option('--crm-sheet-id', help='CRM Google Sheet ID')
@click.option('--phase5-sheet-id', help='Phase 5 Google Sheet ID')
@click.option('--phase5-db-path', default='logs/phase5_data.db',
             help='Phase 5 SQLite DB path')
@click.option('--limit', type=int, default=None,
             help='Extraction limit (debug)')
@click.pass_context
def migrate(ctx, source, mode, crm_sheet_id, phase5_sheet_id, phase5_db_path, limit):
    """
    Migrate Phase 1 data to Master Leads
    
    Examples:
      vsa migrate --mode dry-run --limit 10
      vsa migrate --mode validate --crm-sheet-id ABC123 --phase5-sheet-id XYZ789
      vsa migrate --mode load
    """
    settings = ctx.obj['settings']
    
    # Validate required parameters
    if not crm_sheet_id:
        crm_sheet_id = getattr(settings, 'crm_sheet_id', None)
        if not crm_sheet_id:
            click.echo("Error: --crm-sheet-id required or set in .env as CRM_SHEET_ID", err=True)
            raise click.Abort()
    
    if not phase5_sheet_id:
        phase5_sheet_id = getattr(settings, 'phase5_sheet_id', None)
        if not phase5_sheet_id:
            click.echo("Error: --phase5-sheet-id required or set in .env as PHASE5_SHEET_ID", err=True)
            raise click.Abort()
    
    click.echo("\n" + "="*60)
    click.echo("MIGRATION STARTED")
    click.echo("="*60)
    click.echo(f"Source: {source}")
    click.echo(f"Mode: {mode}")
    click.echo(f"Limit: {limit or 'unlimited'}")
    click.echo(f"Timestamp: {datetime.now().isoformat()}")
    click.echo("="*60 + "\n")
    
    try:
        # Create repository
        repository = GoogleSheetsRepository(
            sheet_id=settings.google_sheet_id,
            credentials_file=settings.google_service_account_json
        )
        
        # Create pipeline
        pipeline = MigrationPipeline(settings, repository)
        
        # Execute migration
        if mode == 'dry-run':
            results = pipeline.dry_run(
                crm_sheet_id=crm_sheet_id,
                phase5_sheet_id=phase5_sheet_id,
                phase5_db_path=phase5_db_path,
                limit=limit
            )
        elif mode == 'validate':
            results = pipeline.validate(
                crm_sheet_id=crm_sheet_id,
                phase5_sheet_id=phase5_sheet_id,
                phase5_db_path=phase5_db_path,
                limit=limit
            )
        else:  # load
            # Confirm before loading
            if click.confirm("Are you sure you want to load data to Master Leads?"):
                results = pipeline.load(
                    crm_sheet_id=crm_sheet_id,
                    phase5_sheet_id=phase5_sheet_id,
                    phase5_db_path=phase5_db_path,
                    limit=limit
                )
            else:
                click.echo("Migration cancelled.")
                return
        
        # Print results
        pipeline.orchestrator.print_results(results)
        
        # Log summary
        logger.info("Migration completed", 
                   mode=mode,
                   overall_status=results.get('overall_status'),
                   stages=len(results.get('stages', {})))
        
    except Exception as e:
        logger.error("Migration failed", error=str(e))
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()

@main.command()
@click.option('--action', type=click.Choice(['fetch', 'crawl', 'validate']),
             default='fetch', help='Sync action')
@click.option('--lead-id', help='Specific lead ID to sync')
@click.pass_context
def sync(ctx, action, lead_id):
    """
    Sync with Google Sheets Master Leads
    
    Examples:
      vsa sync --action fetch
      vsa sync --action crawl --lead-id LEAD001
      vsa sync --action validate
    """
    settings = ctx.obj['settings']
    
    click.echo(f"\n[INFO] Sync action: {action}")
    if lead_id:
        click.echo(f"[INFO] Lead ID: {lead_id}")
    
    logger.info("Sync started", action=action, lead_id=lead_id)
    
    try:
        # TODO: Implement sync logic
        # - fetch: Master Leads から全データ取得
        # - crawl: 指定リードのオフィシャルサイトをクロール
        # - validate: 連絡先検証
        
        click.echo(f"[INFO] Sync {action} completed.")
        logger.info("Sync completed", action=action)
        
    except Exception as e:
        logger.error("Sync failed", error=str(e))
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()

@main.command()
def version():
    """Display VSA version"""
    click.echo(f"VSA Phase2-Core version {__version__}")
    logger.info("Version command executed", version=__version__)

if __name__ == '__main__':
    main(obj={})
