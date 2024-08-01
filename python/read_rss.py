#!env python3
from lib.rss import rss_feed
from lib.decor import arrest, log_error
import json
import fileinput

"""Embed RSS feed in JSON"""


def truncurl(string: str) -> str:
    """Get rid of trailing stuff from article urls like promo and source_id tracking E.g. ?src=rss&campaign=foo"""
    if "#" in string:
        index = string.index("#")
        return string[:index]
    if "?" in string:
        index = string.index("?")
        return string[:index]
    else:
        return string


@arrest([KeyError], "Missing url in feed record.")
def feedrec(feed):
    """Print RSS feed record"""
    if "url" not in feed or feed["url"] == "":
        raise ValueError(f"Feed URL missing or empty.\n{feed}")
    else:
        rec = {
            "type": "rss",
            "source_id": "",
            "title": "",
            "description": "",
            "url": "",
        }
        for k in rec.keys():
            if k in feed:
                rec[k] = feed[k]
        print(json.dumps(rec))


@arrest([KeyError], "Missing link in article record.")
def artrec(feed):
    """Print article record"""
    for art in feed["items"]:
        if "link" not in art or art["link"] == "":
            raise ValueError(f"Article URL missing or empty.\n{art}")
        else:
            rec = {
                "type": "art",
                "source_id": feed["source_id"],
                "title": art["title"],
                "summary": "",
                "link": truncurl(art["link"]),
                "published": art["published"],
                "published_parsed": art["published_parsed"],
            }
            if "summary" in art:
                rec["summary"] = art["summary"]
            if "tags" in art:
                rec["tags"] = [tag["term"] for tag in art["tags"]]
            print(json.dumps(rec))


@arrest([ValueError], "Couldn't get feed.")
def proc(source_id: str, url: str):
    """Main processing"""
    feed = rss_feed(url)
    feed["source_id"] = source_id
    feedrec(feed)
    artrec(feed)


@arrest([TypeError, ValueError], "Invalid feed entry in input.")
def valid(line):
    """Feed url line input validation. Line is tab delim <source_id>\t<RSS url>"""
    source_id, url = line.split()
    source_id = str(source_id)
    if type(source_id) is not str:
        raise TypeError(f"Feed id type: {type(source_id)} must be string.")
    if "http" != url[:4]:
        raise ValueError(f"Feed URL: {url} must be of form http.")
    return source_id, url


@arrest([TypeError], "I love trash -- Oscar T. Grouch.")
def read():
    """Read lines from stdin. Should be source_id and url on lines."""
    ln = 0
    for line in fileinput.input():
        try:
            ln += 1
            source_id, url = valid(line.strip())
            proc(source_id, url)
        except Exception as e:
            log_error(f"stdin line: {ln} type: {type(e)} val: {e}\n[{line}]")


if __name__ == "__main__":
    read()
