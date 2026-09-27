from pathlib import Path
from typing import NewType

FullPath = NewType("FullPath", Path)
"""A new type representing a full file system path."""
