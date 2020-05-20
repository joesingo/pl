class SearchFailureError(Exception):
    """
    The user's search was cancelled or returned an invalid option
    """

class EmptyLibraryError(Exception):
    """
    There are no papers in the library
    """

class InvalidBibTeXError(Exception):
    """
    There was an error parsing the BibTeX contents
    """

class SciHubError(Exception):
    """
    There was a problem downloading a PDF from SciHub
    """
