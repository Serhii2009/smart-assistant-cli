"""
Persistence layer — all filesystem I/O for Smart Assistant.

Responsibility:
    This is the ONLY module that reads or writes files, imports pickle,
    or knows about the on-disk data directory.  Nothing else in the
    codebase may touch the filesystem directly.

    Provides atomic save/load for AddressBook and NoteBook using the
    write-to-temp-then-rename pattern so a crash mid-write never
    corrupts existing data.

Functions:
    get_data_dir() -> Path
        Returns Path(~/.smart_assistant), creating it on first call.

    save_address_book(book: AddressBook) -> None
        Atomically serialises book to contacts.pkl.

    load_address_book() -> AddressBook
        Deserialises from contacts.pkl; returns a fresh AddressBook on
        missing file or any pickle error (logs warning to stderr).

    save_notebook(notebook: NoteBook) -> None
        Atomically serialises notebook to notes.pkl.

    load_notebook() -> NoteBook
        Deserialises from notes.pkl; returns a fresh NoteBook on any error.

Constants:
    DATA_DIR_NAME : str  — name of the hidden directory in the user's home
    CONTACTS_FILE : str  — pickle filename for contacts
    NOTES_FILE    : str  — pickle filename for notes

Validation rules:
    n/a — storage operates on already-valid domain objects

Dependencies (internal):
    smart_assistant.models.contact (AddressBook)
    smart_assistant.models.note    (NoteBook)

External libs:
    none (stdlib only: os, pickle, sys, tempfile, pathlib)

Assignee:
"""

from __future__ import annotations

import os
import pickle
import sys
import tempfile
from pathlib import Path

from smart_assistant.models.contact import AddressBook
from smart_assistant.models.note import NoteBook

DATA_DIR_NAME: str = ".smart_assistant"
CONTACTS_FILE: str = "contacts.pkl"
NOTES_FILE: str = "notes.pkl"


def get_data_dir() -> Path:
    """
    Return the data directory path, creating it if it does not exist.

    Returns
    -------
    Path
        ~/.smart_assistant/  (platform-specific home is resolved by pathlib)
    """
    data_dir = Path.home() / DATA_DIR_NAME
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def _atomic_save(obj: object, path: Path) -> None:
    """
    Write *obj* to *path* atomically.

    Writes to a temporary file in the same directory, then calls
    os.replace() which is atomic on both POSIX and Windows (same volume).
    """
    dir_ = path.parent
    with tempfile.NamedTemporaryFile(delete=False, dir=dir_, suffix=".tmp") as fh:
        pickle.dump(obj, fh, protocol=pickle.HIGHEST_PROTOCOL)
        tmp_path = fh.name
    os.replace(tmp_path, path)  # atomic rename


def _safe_load(path: Path, fallback_factory):
    """
    Load a pickle file, returning fallback_factory() on any error.
    """
    if not path.exists():
        return fallback_factory()
    try:
        with open(path, "rb") as fh:
            return pickle.load(fh)
    except Exception as exc:  # noqa: BLE001
        print(
            f"[smart-assistant] Warning: could not load '{path.name}': {exc}\n"
            "  Starting with an empty collection.",
            file=sys.stderr,
        )
        return fallback_factory()


# ── Public API ────────────────────────────────────────────────────────────────


def save_address_book(book: AddressBook) -> None:
    """Atomically persist the address book to disk."""
    _atomic_save(book, get_data_dir() / CONTACTS_FILE)


def load_address_book() -> AddressBook:
    """Load the address book from disk, returning a fresh one on any error."""
    return _safe_load(get_data_dir() / CONTACTS_FILE, AddressBook)


def save_notebook(notebook: NoteBook) -> None:
    """Atomically persist the notebook to disk."""
    _atomic_save(notebook, get_data_dir() / NOTES_FILE)


def load_notebook() -> NoteBook:
    """Load the notebook from disk, returning a fresh one on any error."""
    return _safe_load(get_data_dir() / NOTES_FILE, NoteBook)
