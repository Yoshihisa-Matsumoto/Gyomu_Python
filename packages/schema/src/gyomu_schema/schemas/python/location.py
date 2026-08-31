from pydantic import BaseModel


class SourceLocation(BaseModel):
    start_line: int
    start_column: int
    end_line: int
    end_column: int
