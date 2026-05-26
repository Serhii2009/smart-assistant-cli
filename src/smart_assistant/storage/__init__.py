"""
Storage package initializer.

Responsibility:
    Re-exports the public persistence API so callers can use
    ``from smart_assistant.storage import save_address_book, load_address_book``
    etc. without knowing the internal module name.

Assignee:
"""

from smart_assistant.storage.repository import (
    get_data_dir,
    load_address_book,
    load_notebook,
    save_address_book,
    save_notebook,
)

__all__ = [
    "get_data_dir",
    "save_address_book",
    "load_address_book",
    "save_notebook",
    "load_notebook",
]
