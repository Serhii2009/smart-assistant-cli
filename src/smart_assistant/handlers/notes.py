"""
Note command handlers — pure business logic layer.

Responsibility:
    Implements every note-related operation as a pure function.
    Mirrors the structure of handlers/contacts.py.
    No print(), input(), or rich calls are permitted here.

Functions:
    handle_add_note(notebook, title, body)
        -> tuple[str, Note | str]

    handle_show_notes(notebook)
        -> tuple[str, list[Note]]

    handle_find_note(notebook, query)
        -> tuple[str, list[Note]]

    handle_edit_note(notebook, title, new_title, new_body)
        -> tuple[str, Note | str]

    handle_delete_note(notebook, title)
        -> tuple[str, str]

    handle_add_tag(notebook, title, tag)
        -> tuple[str, Note | str]

    handle_remove_tag(notebook, title, tag)
        -> tuple[str, Note | str]

    handle_find_by_tag(notebook, tag)
        -> tuple[str, list[Note]]

    handle_sort_by_tags(notebook)
        -> tuple[str, list[Note]]

Return status values:
    "ok"        — operation succeeded
    "error"     — validation failure; payload is error message string
    "not_found" — named entity not found; payload is message string
    "empty"     — result set is empty; payload is []

Dependencies (internal):
    smart_assistant.models.note (Note, NoteBook)

External libs:
    none

Assignee:
"""

from __future__ import annotations

from typing import Optional

from smart_assistant.models.note import Note, NoteBook


def handle_add_note(
    notebook: NoteBook,
    title: str,
    body: str = "",
) -> tuple[str, Note | str]:
    """
    Create and store a new note.

    Returns
    -------
    ("ok", note)       — created successfully
    ("error", message) — title empty, too long, or already exists
    """
    try:
        note = notebook.add(title, body)
        return "ok", note
    except ValueError as exc:
        return "error", str(exc)


def handle_show_notes(notebook: NoteBook) -> tuple[str, list[Note]]:
    """
    Return all notes sorted newest-first.

    Returns
    -------
    ("ok", list[Note])  — at least one note exists
    ("empty", [])       — no notes
    """
    notes = notebook.all()
    if not notes:
        return "empty", []
    return "ok", notes


def handle_find_note(
    notebook: NoteBook, query: str
) -> tuple[str, list[Note]]:
    """
    Full-text search across note titles and bodies.

    Returns
    -------
    ("ok", list[Note])  — matches found
    ("empty", [])       — no matches
    ("error", message)  — empty query
    """
    if not query.strip():
        return "error", "Search query cannot be empty."  # type: ignore[return-value]
    results = notebook.search(query.strip())
    if not results:
        return "empty", []
    return "ok", results


def handle_edit_note(
    notebook: NoteBook,
    title: str,
    new_title: Optional[str] = None,
    new_body: Optional[str] = None,
) -> tuple[str, Note | str]:
    """
    Edit a note's title and/or body.

    Returns
    -------
    ("ok", note)            — edit succeeded
    ("not_found", message)  — note does not exist
    ("error", message)      — new_title conflicts or validation fails
    """
    if new_title is None and new_body is None:
        return "error", "Provide at least a new title or new body."
    try:
        note = notebook.edit(title, new_title=new_title, new_body=new_body)
        return "ok", note
    except KeyError as exc:
        return "not_found", str(exc)
    except ValueError as exc:
        return "error", str(exc)


def handle_delete_note(
    notebook: NoteBook, title: str
) -> tuple[str, str]:
    """
    Delete a note by title.

    Returns
    -------
    ("ok", title)           — deleted successfully
    ("not_found", message)  — note does not exist
    """
    try:
        notebook.delete(title)
        return "ok", title
    except KeyError as exc:
        return "not_found", str(exc)


def handle_add_tag(
    notebook: NoteBook, title: str, tag: str
) -> tuple[str, Note | str]:
    """
    Attach a tag to a note.

    Returns
    -------
    ("ok", note)            — tag added
    ("not_found", message)  — note not found
    ("error", message)      — invalid tag or already attached
    """
    try:
        note = notebook.get(title)
    except KeyError as exc:
        return "not_found", str(exc)
    try:
        note.add_tag(tag)
        return "ok", note
    except ValueError as exc:
        return "error", str(exc)


def handle_remove_tag(
    notebook: NoteBook, title: str, tag: str
) -> tuple[str, Note | str]:
    """
    Remove a tag from a note.

    Returns
    -------
    ("ok", note)            — tag removed
    ("not_found", message)  — note or tag not found
    ("error", message)      — other error
    """
    try:
        note = notebook.get(title)
    except KeyError as exc:
        return "not_found", str(exc)
    try:
        note.remove_tag(tag)
        return "ok", note
    except KeyError as exc:
        return "not_found", str(exc)


def handle_find_by_tag(
    notebook: NoteBook, tag: str
) -> tuple[str, list[Note]]:
    """
    Return all notes carrying the given tag.

    Returns
    -------
    ("ok", list[Note])  — notes found
    ("empty", [])       — no notes have this tag
    ("error", message)  — empty tag string
    """
    if not tag.strip():
        return "error", "Tag cannot be empty."  # type: ignore[return-value]
    results = notebook.search_by_tag(tag.strip())
    if not results:
        return "empty", []
    return "ok", results


def handle_sort_by_tags(notebook: NoteBook) -> tuple[str, list[Note]]:
    """
    Return all notes sorted alphabetically by their first tag.

    Returns
    -------
    ("ok", list[Note])  — sorted list (untagged notes at end)
    ("empty", [])       — no notes at all
    """
    notes = notebook.sort_by_tags()
    if not notes:
        return "empty", []
    return "ok", notes
