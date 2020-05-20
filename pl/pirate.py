import requests
from bs4 import BeautifulSoup
from paperfinder import get_publisher, get_bibtex

from pl.exceptions import SciHubError
from pl.secrets import SCIHUB_COOKIES

SCIHUB_BASE_URL = "https://sci-hub.se"

def get_pdf_url(doi):
    url = f"{SCIHUB_BASE_URL}/{doi}"
    resp = requests.get(url, cookies=SCIHUB_COOKIES)
    doc = BeautifulSoup(resp.content, features="html.parser")
    for tag in doc.findAll("a", attrs={"href": "#"}):
        if tag.text == "⇣ save":
            # the href of the <a> is "location.href='{url}'"
            oncl = tag.get("onclick")
            print(oncl)
            prefix = "location.href=\'"
            n = len(prefix)
            assert oncl[:n] == prefix
            assert oncl[-1] == "\'"
            pdf_url = oncl[n:-1]
            # sometimes the url is missing the "http:" prefix...
            if not pdf_url.startswith("http:") and not pdf_url.startswith("https:"):
                pdf_url = "http:" + pdf_url
            return pdf_url

    raise SciHubError("could not find SciHub download link")

def get_pdf(doi):
    resp = requests.get(get_pdf_url(doi), cookies=SCIHUB_COOKIES)
    return resp.content

def get_pdf_bib(url):
    """
    Return `(pdf, bibtex)` where `pdf` is a bytes object and `bibtex` is a
    string
    """
    # Let any paperfinder exceptions bubble
    pub = get_publisher(url)
    doi = pub.get_doi(url)
    bibtex = get_bibtex(doi)

    return get_pdf(doi), bibtex
