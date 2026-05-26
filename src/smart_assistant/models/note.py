"""
Note domain model: Note and NoteBook.

Responsibility:
    Defines Note (a titled text note with optional tags and timestamps) and
    NoteBook (a dict-backed collection of Notes) with full CRUD, full-text
    search, and tag-based search/sort.

    This module does NOT interact with I/O, storage, or rendering.

Classes:
    Note:     A single text note with title, body, tags, and timestamps.
    NoteBook: Collection of Note objects — keyed by lower-cased title.

Functions:
    (none at module level)

Validation rules:
    Note title — stripped, non-empty, max 200 chars.
    Note body  — stripped, may be empty (useful for quick title-only notes).
    Tag values — validated by Tag field constructor (see fields.py).
    Duplicate tags within one Note are rejected (case-insensitive).
    Duplicate note titles within NoteBook are rejected (case-insensitive).

Dependencies (internal):
    smart_assistant.models.fields (Tag)

External libs:
    none (stdlib only: datetime)

Assignee:
"""

from __future__ import annotations

import datetime
from typing import Optional

from smart_assistant.models.fields import Tag


class Note:
    """
    A single text note.

    Attributes
    ----------
    title : str
        Human-readable identifier — unique within a NoteBook.
    body : str
        Main content of the note.
    tags : list[Tag]
        Zero or more keyword tags.
    created_at : datetime.datetime
        UTC timestamp recorded at construction.
    updated_at : datetime.datetime
        UTC timestamp updated on every edit.
    """

    def __init__(self, title: str, body: str = "") -> None:
        self.title: str = self._validate_title(title)
        self.body: str = body.strip()
        self.tags: list[Tag] = []
        now = datetime.datetime.utcnow()
        self.created_at: datetime.datetime = now
        self.updated_at: datetime.datetime = now

    # ── Validation ────────────────────────────────────────────────────────────

    @staticmethod
    def _validate_title(value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Note title cannot be empty.")
        if len(cleaned) > 200:
            raise ValueError("Note title must be 200 characters or fewer.")
        return cleaned

    # ── Tag management ────────────────────────────────────────────────────────

    def add_tag(self, value: str) -> Tag:
        """
        Create and append a Tag.

        Raises
        ------
        ValueError — if tag is invalid or already attached to this note
        """
        tag = Tag(value)
        if self.has_tag(tag.value):
            raise ValueError(
                f"Tag '{tag.value}' is already attached to this note."
            )
        self.tags.append(tag)
        self.updated_at = datetime.datetime.utcnow()
        return tag

    def remove_tag(self, value: str) -> None:
        """
        Remove a tag from the note (case-insensitive match on bare value).

        Raises
        ------
        KeyError — if tag is not found
        """
        stripped = value.strip().lstrip("#").lower()
        for tag in self.tags:
            if tag.value.lower() == stripped:
                self.tags.remove(tag)
                self.updated_at = datetime.datetime.utcnow()
                return
        raise KeyError(f"Tag '{value}' not found on note '{self.title}'.")

    def has_tag(self, value: str) -> bool:
        """Case-insensitive check whether this note carries the given tag."""
        stripped = value.strip().lstrip("#").lower()
        return any(t.value.lower() == stripped for t in self.tags)

    # ── Editing ───────────────────────────────────────────────────────────────

    def edit_title(self, new_title: str) -> None:
        self.title = self._validate_title(new_title)
        self.updated_at = datetime.datetime.utcnow()

    def edit_body(self, new_body: str) -> None:
        self.body = new_body.strip()
        self.updated_at = datetime.datetime.utcnow()

    # ── Search ────────────────────────────────────────────────────────────────

    def matches_query(self, query: str) -> bool:
        """Return True if *query* appears (case-insensitive) in title or body."""
        q = query.lower()
        return q in self.title.lower() or q in self.body.lower()

    # ── Serialisation ────────────────────────────────────────────────────────

    def to_dict(self) -> dict[str, str]:
        """Return a flat string dict for the renderer layer."""
        return {
            "title": self.title,
            "body": self.body,
            "body_preview": (self.body[:60] + "…") if len(self.body) > 60 else self.body,
            "tags": " ".join(str(t) for t in self.tags) or "—",
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M"),
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M"),
        }

    # ── Dunder ────────────────────────────────────────────────────────────────

    def __str__(self) -> str:
        tags_str = " ".join(str(t) for t in self.tags)
        return (
            f"Title  : {self.title}\n"
            f"Tags   : {tags_str or '(none)'}\n"
            f"Created: {self.created_at:%Y-%m-%d %H:%M}\n"
            f"Body   :\n{self.body}"
        )

    def __repr__(self) -> str:
        return f"Note(title={self.title!r})"


# ──────────────────────────────────────────────────────────────────────────────


class NoteBook:
    """
    A case-insensitive dictionary of Note objects keyed by lower-cased title.

    All public methods accept the note title in any case.
    """

    def __init__(self) -> None:
        self._data: dict[str, Note] = {}

    # ── CRUD ─────────────────────────────────────────────────────────────────

    def add(self, title: str, body: str = "") -> Note:
        """
        Create and store a new Note.

        Raises
        ------
        ValueError — if a note with the same title already exists
        """
        key = title.strip().lower()
        if key in self._data:
            raise ValueError(
                f"A note titled '{title}' already exists. "
                "Use edit-note to modify it."
            )
        note = Note(title, body)
        self._data[key] = note
        return note

    def get(self, title: str) -> Note:
        """
        Return the Note for *title*.

        Raises
        ------
        KeyError — if not found
        """
        note = self._data.get(title.strip().lower())
        if note is None:
            raise KeyError(f"Note '{title}' not found.")
        return note

    def delete(self, title: str) -> None:
        """
        Delete a note by title.

        Raises
        ------
        KeyError — if not found
        """
        key = title.strip().lower()
        if key not in self._data:
            raise KeyError(f"Note '{title}' not found.")
        del self._data[key]

    def edit(
        self,
        title: str,
        new_title: Optional[str] = None,
        new_body: Optional[str] = None,
    ) -> Note:
        """
        Edit a note's title and/or body.

        At least one of new_title or new_body must be provided.

        Raises
        ------
        KeyError   — if *title* is not found
        ValueError — if *new_title* conflicts with an existing note
        """
        note = self.get(title)  # raises KeyError if missing

        if new_title is not None:
            new_key = new_title.strip().lower()
            old_key = title.strip().lower()
            if new_key in self._data and new_key != old_key:
                raise ValueError(
                    f"A note titled '{new_title}' already exists."
                )
            # Rename: remove old key, update note, add new key
            del self._data[old_key]
            note.edit_title(new_title)
            self._data[new_key] = note

        if new_body is not None:
            note.edit_body(new_body)

        return note

    # ── Search ────────────────────────────────────────────────────────────────

    def search(self, query: str) -> list[Note]:
        """Full-text search across title and body, sorted newest-first."""
        return sorted(
            (n for n in self._data.values() if n.matches_query(query)),
            key=lambda n: n.created_at,
            reverse=True,
        )

    def search_by_tag(self, tag: str) -> list[Note]:
        """Return notes that carry *tag* (case-insensitive), newest-first."""
        return sorted(
            (n for n in self._data.values() if n.has_tag(tag)),
            key=lambda n: n.created_at,
            reverse=True,
        )

    def sort_by_tags(self) -> list[Note]:
        """
        Return all notes sorted alphabetically by their first tag.
        Notes without tags are placed at the end.
        """

        def sort_key(note: Note) -> tuple[int, str]:
            if note.tags:
                return (0, note.tags[0].value.lower())
            return (1, "")

        return sorted(self._data.values(), key=sort_key)

    def all(self) -> list[Note]:
        """All notes sorted newest-first."""
        return sorted(
            self._data.values(), key=lambda n: n.created_at, reverse=True
        )

    def __len__(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:
        return f"NoteBook({len(self._data)} notes)"
