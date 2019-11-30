"""
Read from stdin a library exported from Zotero in BibTeX format, and import
into pl.

Last tested at commit 1544a7a247449bf07ea6dffe46925ce08a9a9304. This script
will probably not be supported for subsequent versions of pl
"""
from pathlib import Path
import sys

import bibtexparser

from pl import Library, InvalidBibTeXError

def process_paper(library, bibtex):
    entries = library.parse_bibtex(bibtex.split("\n"), ("title",))
    if "file" not in entries:
        print(f"no file for title '{entries['title']}'", file=sys.stderr)
        return

    parts = entries["file"].split(":")
    path = parts[1]

    tmp = Path("/tmp/t.bib")
    with tmp.open("w") as f:
        f.write(bibtex)
    try:
        library.import_paper(Path(path), tmp)
    except InvalidBibTeXError:
        print(f"failed to import '{entries['title']}'")
        return

def main():
    library = Library()

    buf = ""
    for line in sys.stdin.readlines():
        if line != "\n":
            buf += line
            continue
        if buf:
            process_paper(library, buf)
        buf = ""

if __name__ == "__main__":
    main()
