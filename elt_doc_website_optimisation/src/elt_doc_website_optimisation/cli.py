"""Command-line interface for ELT Doc Website Optimisation."""

import sys
from pathlib import Path

import click

from .assessment import AssessmentOrchestrator
from .config_loader import load_config
from .enhance_report import enhance_report


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """ELT Doc Website Optimisation - Website assessment tool."""
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
        config = Path(__file__).parent.parent.parent / "assessments" / "cnltd_assessment.yaml"

    if not config.exists():
        click.echo(f"Error: Config file not found: {config}", err=True)
        sys.exit(1)

    click.echo(f"Using config: {config}")

    try:
        orchestrator = AssessmentOrchestrator(config)
        output_path = orchestrator.run()
        click.echo(f"\n✓ Assessment complete!")
        click.echo(f"Report saved to: {output_path}")
        click.echo(f"\n💡 Tip: Run 'enhance' command to create client-ready version:")
        click.echo(f"   uv run elt-doc-website-optimisation enhance {output_path}")
    except Exception as e:
        click.echo(f"Error during assessment: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("input_doc", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output", "-o",
    type=click.Path(path_type=Path),
    default=None,
    help="Output path for enhanced report",
)
@click.option(
    "--prompt", "-p",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Path to prompt template (default: prompts/report_enhancement.txt)",
)
def enhance(input_doc: Path, output: Path | None, prompt: Path | None):
    """Prepare assessment report for LLM enhancement.
    
    This command extracts structured data from the Python-generated report
    and creates a prompt for LLM-based enhancement.
    
    After running this, submit the generated prompt to your LLM API to produce
    the final client-ready document.
    """
    if output is None:
        output = input_doc.parent / "enhanced_report.docx"
    
    if prompt is None:
        prompt = Path(__file__).parent.parent.parent / "prompts" / "report_enhancement.txt"

    try:
        prompt_path = enhance_report(input_doc, output, prompt)
        click.echo(f"\n✓ Enhancement prompt created!")
        click.echo(f"Prompt file: {prompt_path}")
        click.echo(f"\nNext steps:")
        click.echo(f"1. Review the prompt file")
        click.echo(f"2. Submit to your LLM API (Claude, GPT-4, etc.)")
        click.echo(f"3. LLM will generate: {output}")
    except Exception as e:
        click.echo(f"Error during enhancement preparation: {e}", err=True)
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
        config = Path(__file__).parent.parent.parent / "assessments" / "cnltd_assessment.yaml"

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
            click.echo(f"      Path: {req.full_path}")
        click.echo(f"\nCredentials: {'Configured' if cfg.credentials else 'Not configured'}")
        if cfg.credentials:
            click.echo(f"  Username: {cfg.credentials.username}")
        click.echo(f"\nOutput: {cfg.output_path}")
    except Exception as e:
        click.echo(f"Error loading config: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
