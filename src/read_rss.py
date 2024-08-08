import sys
import json
import re
from lib.util.decor import arrest
from dataclasses import dataclass, asdict, field

VALID_RECORD = re.compile(r"^[a-zA-Z][a-zA-Z0-9]*\thttp:\/\/[^\t]*\.[a-zA-Z]*$")
FORMAT_ERROR = "Invalid input format. Should be 2 tab delimited columns: feed name (starting with a letter, then alphanumerics) and feed URL."


@dataclass(slots=True)
class FeedRecord:
    source: str
    url: str

    def __str__(self) -> str:
        return json.dumps(asdict(self))


@dataclass(slots=True)
class Article:
    flavor: str = "art"
    source: str
    title: str
    summary: str
    link: str
    published: str
    published_parsed: str
    tags: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        return json.dumps(asdict(self))


class ReadRss(BaseException):
    def __init__(self):
        pass

    @arrest([ValueError], "Invalid feed entry in input.")
    def validate_feed(self, line) -> FeedRecord:
        if VALID_RECORD.fullmatch(line):
            source, url = line.split()
            if not (source and url):
                raise ValueError(FORMAT_ERROR)
            return FeedRecord(source, url)
        raise ValueError(FORMAT_ERROR)

    def read(self):
        for i, line in enumerate(sys.stdin, start=1):
            feed_rec = self.validate_feed(line.strip())
            print(f"{i}: {feed_rec}")


if __name__ == "__main__":
    processor = ReadRss()
    processor.read()
