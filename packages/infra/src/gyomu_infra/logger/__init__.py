from .factory import LoggerFactory

logger = LoggerFactory.get()
"""Pre-configured logger instance retrieved from the logger factory."""


__all__ = ["logger"]
"""List of public symbols exported by the logger module."""
