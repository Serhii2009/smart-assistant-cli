"""
Module: repository.py
Responsibility: The sole module responsible for all file-system I/O in the
                application.  Serialises and deserialises AddressBook and
                NoteBook objects using atomic pickle writes to the data/
                folder at the project root.  No other module may read or
                write files — all persistence must go through this module.

Trello tasks:
    Task — Data persistence

Functions to implement:

━━━ Path resolution ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    _PROJECT_ROOT (module-level constant)
        Path(__file__).parent.parent
        Because this file lives at <project_root>/src/repository.py:
            Path(__file__)          →  <project_root>/src/repository.py
            .parent                 →  <project_root>/src/
            .parent.parent          →  <project_root>/
        So _PROJECT_ROOT resolves to the repository folder itself, not the
        Python installation directory.

    DATA_DIR_NAME = "data"   (module-level constant)
    CONTACTS_FILE = "contacts.pkl"   (module-level constant)
    NOTES_FILE    = "notes.pkl"      (module-level constant)

    get_data_dir() -> Path
        Returns _PROJECT_ROOT / DATA_DIR_NAME, calling .mkdir(parents=True,
        exist_ok=True) first so the folder is created on the first call.
        The data/ directory is intentionally at the project root so that
        pickle files are visible during development (not hidden in a user
        home directory).

━━━ Internal helpers ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    _atomic_save(obj: object, path: Path) -> None
        Writes obj to path atomically to prevent a partial write from
        corrupting the saved data if the process is interrupted.
        Strategy:
          1. Open a temporary file in the same directory as path (same
             filesystem volume) using tempfile.NamedTemporaryFile(
             delete=False, dir=path.parent, suffix=".tmp").
          2. pickle.dump obj into it with pickle.HIGHEST_PROTOCOL.
          3. Close the temp file.
          4. Call os.replace(tmp_path, path) — this is an atomic rename on
             both POSIX and Windows when source and destination share a volume.
        The caller never sees a partial write; the file is either the old
        complete version or the new complete version.

    _safe_load(path: Path, factory: Callable) -> object
        Loads the pickle file at path and returns the deserialised object.
        If path does not exist, returns factory() (an empty collection).
        If the file exists but cannot be loaded (corrupt, wrong class version,
        etc.), prints a warning to sys.stderr and returns factory() so the
        application starts with an empty collection rather than crashing.
        The warning format is:
            "[notii] Warning: could not load '<filename>': <exception>\n"
            "  Starting with an empty collection."

━━━ Public API ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    save_address_book(book: AddressBook) -> None
        Calls _atomic_save(book, get_data_dir() / CONTACTS_FILE).

    load_address_book() -> AddressBook
        If contacts.pkl does not exist yet, creates an empty AddressBook,
        writes it to disk immediately via _atomic_save (so the data/ file
        becomes visible on first run), and returns it.
        If the file exists, delegates to _safe_load(path, AddressBook).

    save_notebook(notebook: NoteBook) -> None
        Calls _atomic_save(notebook, get_data_dir() / NOTES_FILE).

    load_notebook() -> NoteBook
        Same auto-create-on-first-run behaviour as load_address_book but
        for notes.pkl.

Dependencies (internal):
    notii.contact — AddressBook (for type hints and factory default)
    notii.note    — NoteBook    (for type hints and factory default)

External libs:
    none (stdlib only: os, pickle, sys, tempfile, pathlib)

Assignee: Constantine Kolesnik
"""

import pickle
import os
import sys
import tempfile
from pathlib import Path

from note import NoteBook
from contact import AddressBook

# Constants
_PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR_NAME = "data"
CONTACTS_FILE = "contacts.pkl"
NOTES_FILE = "notes.pkl"

# Internal helpers
def get_data_dir() -> Path:
    data_dir = _PROJECT_ROOT / DATA_DIR_NAME
    data_dir.mkdir(parents=True, exist_ok=True)  # parents=True handles nested paths
    return data_dir

def _atomic_save(obj, path: Path) -> None:
    # Write to temp file first, then rename — prevents corrupt files on crash
    with tempfile.NamedTemporaryFile(
        delete=False, dir=path.parent, suffix=".tmp"
    ) as fh:
        pickle.dump(obj, fh, protocol=pickle.HIGHEST_PROTOCOL)
        tmp_path = fh.name
    os.replace(tmp_path, path)

def _safe_load(path: Path, factory):
    # Returns empty collection instead of crashing on corrupt file
    if not path.exists():
        return factory()
    try:
        with open(path, "rb") as fh:
            return pickle.load(fh)
    except Exception as exc:
        print(
            f"[notii] Warning: could not load '{path.name}': {exc}\n"
            "  Starting with an empty collection.",
            file=sys.stderr,
        )
        return factory()


# Public API
def save_address_book(book: AddressBook) -> None:
    _atomic_save(book, get_data_dir() / CONTACTS_FILE)

def load_address_book() -> AddressBook:
    path = get_data_dir() / CONTACTS_FILE
    if not path.exists():
        book = AddressBook()
        _atomic_save(book, path)  # create file on first run so it's visible
        return book
    return _safe_load(path, AddressBook)
    
def save_notebook(nb: NoteBook) -> None:
    _atomic_save(nb, get_data_dir() / NOTES_FILE)

def load_notebook() -> NoteBook:
    path = get_data_dir() / NOTES_FILE
    if not path.exists():
        nb = NoteBook()
        _atomic_save(nb, path)  # create file on first run so it's visible
        return nb
    return _safe_load(path, NoteBook)
