from pathlib import Path
import re
import shutil
import sys

import yaml

from pl.exceptions import (
    EmptyLibraryError,
    InvalidBibTeXError,
    SearchFailureError,
)
from pl.config import Config
from pl.utils import run_cmd

def search_wrapper(f):
    """
    Decorator to add error handling to functions using Library.search()
    """
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except SearchFailureError:
            print("nothing to do")
        except EmptyLibraryError:
            print("library is empty")
    return inner

class Library:
    def __init__(self, config_path=None):
        self.config = Config.from_path(config_path)
        try:
            self.config.storage_dir = Path(self.config.storage_dir).expanduser()
        except AttributeError:
            raise ValueError(f"required key 'storage_dir' missing from config")

        self.pdf_dir = self.config.storage_dir / "pdf"
        self.bib_dir = self.config.storage_dir / "bib"
        for p in (self.pdf_dir, self.bib_dir):
            p.mkdir(exist_ok=True)

        # Load state
        self.state_file = self.config.storage_dir / "state.yaml"
        try:
            with self.state_file.open() as f:
                self.state = yaml.safe_load(f)
        except FileNotFoundError:
            self.state = {
                "index_to_id": {}
            }
            self.write_state()

    def write_state(self):
        with self.state_file.open("w") as f:
            yaml.dump(self.state, stream=f)

    def get_pdf_path(self, paper_id):
        return self.pdf_dir / f"{paper_id}.pdf"

    def get_bib_path(self, paper_id):
        return self.bib_dir / f"{paper_id}.bib"

    def import_paper(self, pdf_in, bib_in):
        with bib_in.open() as f:
            entries = self.parse_bibtex(f, required_keys=("title", "author"))
        reg = re.compile(r"[{}\"]")
        title = reg.sub("", entries["title"].strip())
        author = reg.sub("", entries["author"].strip())

        index_string = f"{title} - {author}"
        paper_id = re.sub(r"[^a-zA-Z0-9- ]", "", title.lower()).replace(" ", "_")

        # TODO: check we are not going to overwrite anything
        shutil.copy(str(pdf_in), str(self.get_pdf_path(paper_id)))
        shutil.copy(str(bib_in), str(self.get_bib_path(paper_id)))

        self.state["index_to_id"][index_string] = paper_id
        self.write_state()
        print(f"added '{index_string}'")

    def parse_bibtex(self, f, required_keys=None):
        entries = {}
        entry_regex = re.compile(r"[^@}]")
        for line in f:
            line = line.strip()
            if not entry_regex.match(line):
                continue
            if line.endswith(","):
                line = line[:-1]
            try:
                key, value = map(str.strip, line.split("=", maxsplit=1))
            except ValueError:
                print(f"did not recognise line '{line}'", file=sys.stderr)
                continue
            entries[key.lower()] = value
        # Check required keys
        for key in required_keys or []:
            if key not in entries:
                raise InvalidBibTeXError(f"required key '{key}' missing")
        return entries

    @search_wrapper
    def open_paper(self):
        pdf_path = self.get_pdf_path(self.search())
        cmd = f"{self.config.open_command} {pdf_path}"
        run_cmd(cmd, fork=True)

    @search_wrapper
    def export_citation(self):
        print(self.get_bib_path(self.search()).read_text())

    def search(self):
        """
        Run interactive search and return the selected paper ID
        """
        index_strs = "\n".join(self.state["index_to_id"].keys())
        if not index_strs:
            raise EmptyLibraryError
        index_str = run_cmd(
            self.config.search_command,
            input=bytes(index_strs, "utf-8")
        )
        mapping = self.state["index_to_id"]
        if not index_str or index_str not in mapping:
            raise SearchFailureError
        return mapping[index_str]
