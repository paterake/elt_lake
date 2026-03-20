"""Command-line interface for ELT Doc Assessment."""

import sys
from pathlib import Path

import click

from .assessment import AssessmentOrchestrator
from .config_loader import load_config


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """ELT Doc Assessment - Website optimisation assessment tool."""
    pass


@cli.command()
@click.option(
    "--config", "-c",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Path to assessment config YAML file",
)
def run(config: Path | None):
    """Run website assessment and generate report."""
    # Default config path
    if config is None:
        config = Path(__file__).parent.parent.parent / "config" / "website_optimisation.yaml"

    if not config.exists():
        click.echo(f"Error: Config file not found: {config}", err=True)
        sys.exit(1)

    click.echo(f"Using config: {config}")

    try:
        orchestrator = AssessmentOrchestrator(config)
        output_path = orchestrator.run()
        click.echo(f"\n✓ Assessment complete!")
        click.echo(f"Report saved to: {output_path}")
    except Exception as e:
        click.echo(f"Error during assessment: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option(
    "--config", "-c",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Path to assessment config YAML file",
)
def preview(config: Path | None):
    """Preview assessment configuration."""
    if config is None:
        config = Path(__file__).parent.parent.parent / "config" / "website_optimisation.yaml"

    if not config.exists():
        click.echo(f"Error: Config file not found: {config}", err=True)
        sys.exit(1)

    try:
        cfg = load_config(config)
        click.echo(f"\nAssessment: {cfg.name}")
        click.echo(f"Description: {cfg.description}")
        click.echo(f"\nWebsites to assess ({len(cfg.websites)}):")
        for website in cfg.websites:
            click.echo(f"  - {website.name}: {website.url}")
        click.echo(f"\nInformation URLs ({len(cfg.information_urls)}):")
        for website in cfg.information_urls:
            click.echo(f"  - {website.name}: {website.url}")
        click.echo(f"\nRequirements ({len(cfg.requirements)}):")
        for req in cfg.requirements:
            click.echo(f"  [{req.sequence}] {req.description}")
        click.echo(f"\nCredentials: {'Configured' if cfg.credentials else 'Not configured'}")
        click.echo(f"\nOutput: {cfg.output_path}")
    except Exception as e:
        click.echo(f"Error loading config: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
