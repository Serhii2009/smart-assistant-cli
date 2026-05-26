"""
Module: __init__.py
Responsibility: Package initialiser — exposes the version string read from
                installed package metadata so it stays in sync with pyproject.toml.

Constants:
    __version__ : str  — package version; falls back to "0.0.0-dev" when
                         running from source before installation

Trello tasks:
    (none — infrastructure only)

Dependencies (internal):
    none

External libs:
    none (stdlib only: importlib.metadata)

Assignee: Serhii Kravchenko
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__: str = version("notii")
except PackageNotFoundError:
    __version__ = "0.0.0-dev"

__all__ = ["__version__"]
