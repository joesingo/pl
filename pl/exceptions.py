from click import ClickException

class SearchFailureError(ClickException):
    """
    The user's search was cancelled or returned an invalid option
    """

class EmptyLibraryError(ClickException):
    """
    There are no papers in the library
    """

class InvalidBibTeXError(ClickException):
    """
    There was an error parsing the BibTeX contents
    """

class SciHubError(ClickException):
    """
    There was a problem downloading a PDF from SciHub
    """
