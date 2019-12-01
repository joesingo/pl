import sys

from pl.library import Library

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
