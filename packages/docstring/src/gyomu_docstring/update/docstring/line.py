from typing import Literal

from pydantic import BaseModel


class DocstringText(BaseModel):
    text: str
    type: Literal["text"] = "text"


class DocstringBlank(BaseModel):
    type: Literal["blank"] = "blank"


class DocstringSectionItem(BaseModel):
    text: str
    type: Literal["section"] = "section"


type DocstringLine = DocstringText | DocstringSectionItem | DocstringBlank
