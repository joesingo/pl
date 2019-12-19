from pathlib import Path

import click

from pl.config import Config
from pl.library import Library

@click.group()
@click.option(
    "-c", "--config",
    help=f"Path to config file (default: {Config.DEFAULT_PATH})",
    type=str
)
@click.pass_context
def main(ctx, config=None):
    """Lightweight tool to manage a collection of PDFs and BibTeX citations"""
    ctx.ensure_object(dict)
    config = Path(config) if config else None
    ctx.obj["library"] = Library(config_path=config)

@main.command(name="import")
@click.argument("pdf")
@click.argument("bib")
@click.pass_context
def import_cmd(ctx, pdf, bib):
    """Import a PDF and BibTeX file"""
    ctx.obj["library"].import_paper(Path(pdf), Path(bib))

@main.command(name="qimport", short_help="Quick import a PDF and BibTeX file")
@click.argument("prefix")
@click.pass_context
def quick_import_cmd(ctx, prefix):
    """
    Shortcut for importing a PDF and BibTeX file whose filename differ only
    in the extension (assumed to be .pdf and .bib respectively).

    This is equivalent to `pl import PREFIX.pdf PREFIX.bib`
    """
    ctx.obj["library"].import_paper(Path(f"{prefix}.pdf"), Path(f"{prefix}.bib"))

@main.command(name="export")
@click.pass_context
def export_cmd(ctx):
    """Select a paper with fzf and print its BibTeX citation to stdout"""
    ctx.obj["library"].export_citation()

@main.command(name="open")
@click.pass_context
def open_cmd(ctx):
    """Select a paper with fzf and open it with a PDF viewer"""
    ctx.obj["library"].open_paper()

@main.command(name="reimport")
@click.pass_context
def reimport_cmd(ctx):
    """Reimport all papers in the collection"""
    ctx.obj["library"].reimport_all()

if __name__ == "__main__":
    main()
