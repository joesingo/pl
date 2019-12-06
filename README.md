# pl

A simple tool for managing a library of papers (**p**aper **l**ibrary).

`pl` manages a collection of PDFs and citations in BibTeX format. It supports
fuzzy search (provided by [fzf](https://github.com/junegunn/fzf)) for opening
papers in a PDF reader or exporting their BibTeX citation.

## Installation

Using Python 3, simply install with pip. To get started, create a config file
at `~/.config/plconf.yaml` in YAML format:

```yaml
storage_dir: /path/to/keep/papers
```

This is the only required configuration setting. See the [configuration
section](#configuration) for other keys that can be set here.

## Usage

`pl` supports importing papers, opening papers, and exporting citations.
Throughout this section, `$storage_dir` denotes the path set in the config file
above.

### Importing

```
pl import <pdf> <bib>
```

This copies the given PDF to `$storage_dir/pdf/<title>.pdf`, where `<title>` is
the title of the paper (obtained from the BibTeX), sanitised to make it a
sensible filename. The BibTeX file is copied to `$storage_dir/bib/<title>.bib`.

### Opening and exporting

Papers are selected for opening/exporting by fuzzy search delegated to
[fzf](https://github.com/junegunn/fzf). The search query is matched against the
`title` and `author` fields of the BibTeX citation.

To search and then open the selected paper:
```
pl open
```

The command to open the PDF comes from the `open_command` config setting. The
default is `xdg-open`, i.e. uses the default PDF viewer for your system (on
many Linux distros at least).

Exporting is similar:
```
pl export
```

In this case the BibTeX citation is printed to stdout.

### Reimporting

If changes are made to the BibTeX entry for a paper after importing, it is
possible for the filename and search key to become out of date (e.g. if the
`title` field is changed, search is still performed against the old title).

To fix this, all papers can be reimported as follows:

``
pl reimport
```

## Configuration

The config file is in [YAML](https://yaml.org/) format. The recognised keys are

- `storage_dir` (required): path under which to store all `pl` files, including
  PDFs and BibTeX files.
- `search_command`: command used to invoke the fuzzy search (default: `fzf`)
- `open_command`: command used to open PDF files (default: `xdg-open`)
