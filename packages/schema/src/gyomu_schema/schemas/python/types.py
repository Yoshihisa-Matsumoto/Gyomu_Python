from pathlib import Path
from typing import NewType

DirectoryRelativePath = NewType("DirectoryRelativePath", Path)

ProjectRelativePath = NewType("ProjectRelativePath", Path)

SourceRelativePath = NewType("SourceRelativePath", Path)

PythonPath = NewType("PythonPath", str)

WorkspaceRelativePath = NewType("WorkspaceRelativePath", Path)

SignatureId = NewType("SignatureId", str)

SymbolId = NewType("SymbolId", str)
