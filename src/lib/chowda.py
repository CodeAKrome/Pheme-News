from bs4 import BeautifulSoup
import html
import re

"""HTML processing functions"""


def ps(doc: str) -> str:
    """Return the text content of paragraph html tags"""
    soup = BeautifulSoup(doc, "html.parser")
    paragraphs = soup.find_all("p")
    result = []
    for p in paragraphs:
        # Replace HTML entities with UTF-8 entities
        text = html.unescape(str(p))
        # Remove any remaining HTML tags
        text = BeautifulSoup(text, "html.parser").get_text()
        result.append(text)
    return " ".join(result)


def html2txt(htmlstr: str) -> str:
    """Convert HTML to plain text"""
    # Replace HTML entities with their UTF-8 counterparts
    utf8_string = html.unescape(htmlstr)
    # Remove remaining HTML markup
    utf8_string = re.sub("\n", "", utf8_string)
    return re.sub("<[^<]+?>", "", utf8_string)
