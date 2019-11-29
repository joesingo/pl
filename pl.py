#!/usr/bin/env python
from pathlib import Path
import re
import shutil
import sys
import subprocess

import bibtexparser
import yaml

CONFIG_PATH = Path("~/.config/plconf.yaml").expanduser()
SEARCH_CMD = ["fzf"]
OPEN_CMD = ["okular"]

class SearchFailureError(Exception):
    """
    The user's search was cancelled or returned an invalid option
    """

class EmptyLibraryError(Exception):
    """
    There are no papers in the library
    """

def run_cmd(cmd, **kwargs):
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, **kwargs)
    return proc.stdout.decode("utf-8").strip()

def search_cmd(f):
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except SearchFailureError:
            print("nothing to do")
        except EmptyLibraryError:
            print("library is empty")
    return inner

class Library:
    def __init__(self):
        with CONFIG_PATH.open() as f:
            config_dict = yaml.safe_load(f)

        if "storage_dir" not in config_dict:
            raise ValueError(f"Required key 'storage_dir' missing from config")

        self.storage_dir = Path(config_dict["storage_dir"]).expanduser()
        self.pdf_dir = self.storage_dir / "pdf"
        self.bib_dir = self.storage_dir / "bib"
        self.state_file = self.storage_dir / "state.yaml"
        # Make sure required dirs exist
        for p in (self.pdf_dir, self.bib_dir):
            p.mkdir(exist_ok=True)

        # Load state
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
            db = bibtexparser.load(f)
        entries = db.entries_dict
        assert len(entries) == 1
        _, items = entries.popitem()
        assert "title" in items
        assert "author" in items

        reg = re.compile(r"[{}]")
        title = reg.sub("", items["title"].strip())
        author = reg.sub("", items["author"].strip())

        index_string = f"{title} - {author}"
        paper_id = title.lower().replace(" ", "_")

        shutil.copy(str(pdf_in), str(self.get_pdf_path(paper_id)))
        shutil.copy(str(bib_in), str(self.get_bib_path(paper_id)))

        self.state["index_to_id"][index_string] = paper_id
        self.write_state()
        print(f"added '{index_string}'")

    @search_cmd
    def open_paper(self):
        pdf_path = self.get_pdf_path(self.search())
        run_cmd(OPEN_CMD + ["--", pdf_path])  # todo: run in the background

    @search_cmd
    def export_citation(self):
        print(self.get_bib_path(self.search()).read_text())

    def search(self):
        """
        Run interactive search and return the selected paper ID, or raise
        SearchFailureError
        """
        index_strs = "\n".join(self.state["index_to_id"].keys())
        if not index_strs:
            raise EmptyLibraryError
        index_str = run_cmd(SEARCH_CMD, input=bytes(index_strs, "utf-8"))
        mapping = self.state["index_to_id"]
        if not index_str or index_str not in mapping:
            raise SearchFailureError
        return mapping[index_str]

def main():
    argv = sys.argv[1:]
    if len(argv) == 0:
        print("nothing to do")
        return

    library = Library()

    cmd, *args = argv
    if cmd == "import":
        pdf_path, bib_path = map(Path, args)
        library.import_paper(pdf_path, bib_path)
    elif cmd == "open":
        library.open_paper()
    elif cmd == "export":
        library.export_citation()

if __name__ == "__main__":
    main()
