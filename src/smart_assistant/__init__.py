"""
Smart Assistant package initializer.

Responsibility:
    Exposes the package version using importlib.metadata so it stays
    synchronised with pyproject.toml without duplication.
    Does not import sub-modules at this level to keep startup fast.

Constants:
    __version__: str  — package version string derived from installed metadata;
                        falls back to "0.0.0-dev" when running from source
                        before the package has been installed.

Dependencies (internal):
    none

External libs:
    importlib.metadata (stdlib, Python 3.8+)

Assignee:
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__: str = version("smart-assistant-cli")
except PackageNotFoundError:
    __version__ = "0.0.0-dev"

__all__ = ["__version__"]
