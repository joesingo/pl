from pathlib import Path
import tempfile

import click
from paperfinder import get_publisher, get_bibtex

from pl.config import Config
from pl.library import Library
from pl.pirate import get_pdf

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

@main.command(name="rst")
@click.pass_context
def rst_header_cmd(ctx):
    """Select a paper with fzf and print a header for my rST paper notes"""
    # Note: not for public consumption. Would be better to implement a plugin
    # system for users to add custom templates
    ctx.obj["library"].rst_header()

@main.command(
    name="pirate",
    short_help="Find a PDF and citation from a URL or DOI using SciHub"
)
@click.option("-u", "--url", type=str)
@click.option("-d", "--doi", type=str)
@click.pass_context
def pirate_cmd(ctx, url=None, doi=None):
    """
    Use paperfinder library to find a paper's DOI and BibTeX citation, given
    its URL on the publisher's website. Use SciHub to download the PDF, and
    import into the library.
    """
    # Note: possibly also not for public consumption...
    if not url and not doi:
        raise click.ClickException("at least one of URL or DOI must be given")
    if url and doi:
        raise click.ClickException("cannot give both URL and DOI")

    library = ctx.obj["library"]
    if url:
        # Let any paperfinder exceptions bubble
        pub = get_publisher(url)
        doi = pub.get_doi(url)
    bib = get_bibtex(doi)
    pdf = get_pdf(doi)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        name = "pl"

        pdf_path = temp_path / f"{name}.pdf"
        pdf_path.write_bytes(pdf)

        bib_path = temp_path / f"{name}.bib"
        bib_path.write_text(bib)

        library.import_paper(pdf_path, bib_path)

if __name__ == "__main__":
    main()
