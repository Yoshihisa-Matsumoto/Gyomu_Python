from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class DocstringText:
    text: str
    type: Literal["text"] = "text"


@dataclass(frozen=True)
class DocstringBlank:
    type: Literal["blank"] = "blank"


@dataclass(frozen=True)
class DocstringSectionItem:
    text: str
    type: Literal["section"] = "section"


type DocstringLine = DocstringText | DocstringSectionItem | DocstringBlank
