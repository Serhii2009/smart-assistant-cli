"""
Module: note.py
Responsibility: Defines the Note (single text note with tags and timestamps)
                and NoteBook (collection of notes) domain classes.

Classes:
    Note     — a titled text note with optional keyword tags and timestamps
    NoteBook — dict-backed collection of Note objects with search and tag ops

Functions:
    (none at module level)

Trello tasks:
    Store notes
    Search notes
    Edit and delete notes
    Tags on notes
    Search and sort by tags

Dependencies (internal):
    notii.fields

External libs:
    none (stdlib only: datetime)

Assignee:
"""

from __future__ import annotations

from collections import UserDict
from datetime import datetime


class Note:
    def __init__(self, title: str, body: str):
        self.title = self._validate_title(title)
        self.body = self._validate_body(body)
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def _validate_title(self, title: str) -> str:
        cleaned = title.strip()

        if not cleaned:
            raise ValueError("Note title cannot be empty.")

        if len(cleaned) > 100:
            raise ValueError("Note title cannot be longer than 100 characters.")

        return cleaned

    def _validate_body(self, body: str) -> str:
        cleaned = body.strip()

        if not cleaned:
            raise ValueError("Note body cannot be empty.")

        return cleaned

    def edit(self, new_title: str | None = None, new_body: str | None = None):
        if new_title is not None and new_title.strip():
            self.title = self._validate_title(new_title)

        if new_body is not None and new_body.strip():
            self.body = self._validate_body(new_body)

        self.updated_at = datetime.now()

    def matches_query(self, query: str) -> bool:
        q = query.lower().strip()

        return q in self.title.lower() or q in self.body.lower()

    def to_dict(self):
        return {
            "title": self.title,
            "body": self.body,
            "created_at": self.created_at.strftime("%d.%m.%Y %H:%M"),
            "updated_at": self.updated_at.strftime("%d.%m.%Y %H:%M"),
        }

    def __str__(self):
        return f"{self.title}\n{self.body}"


class NoteBook(UserDict):
    def _key(self, title: str) -> str:
        return title.strip().lower()

    def add(self, note: Note):
        key = self._key(note.title)

        if key in self.data:
            raise ValueError(f"A note titled '{note.title}' already exists.")

        self.data[key] = note

    def find(self, title: str) -> Note:
        key = self._key(title)

        if key not in self.data:
            raise KeyError(f"Note '{title}' not found.")

        return self.data[key]

    def delete(self, title: str):
        key = self._key(title)

        if key not in self.data:
            raise KeyError(f"Note '{title}' not found.")

        del self.data[key]

    def edit(
        self, title: str, new_title: str | None = None, new_body: str | None = None
    ):
        note = self.find(title)

        old_key = self._key(note.title)
        new_key = self._key(new_title) if new_title and new_title.strip() else old_key

        if new_key != old_key and new_key in self.data:
            raise ValueError(f"A note titled '{new_title}' already exists.")

        note.edit(new_title, new_body)

        if new_key != old_key:
            del self.data[old_key]
            self.data[new_key] = note

        return note

    def search(self, query: str):
        return [note for note in self.data.values() if note.matches_query(query)]

    def all_notes(self):
        return sorted(
            self.data.values(), key=lambda note: note.updated_at, reverse=True
        )
