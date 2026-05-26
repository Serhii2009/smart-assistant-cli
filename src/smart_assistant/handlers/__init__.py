"""
Handlers package initializer.

Responsibility:
    Re-exports all public handler functions from the contacts and notes
    sub-modules so callers can use a single import line.

Assignee:
"""

from smart_assistant.handlers.contacts import (
    handle_add_contact,
    handle_delete_contact,
    handle_edit_contact,
    handle_find_contact,
    handle_show_contacts,
    handle_upcoming_birthdays,
)
from smart_assistant.handlers.notes import (
    handle_add_note,
    handle_add_tag,
    handle_delete_note,
    handle_edit_note,
    handle_find_by_tag,
    handle_find_note,
    handle_remove_tag,
    handle_show_notes,
    handle_sort_by_tags,
)

__all__ = [
    # contacts
    "handle_add_contact",
    "handle_show_contacts",
    "handle_find_contact",
    "handle_edit_contact",
    "handle_delete_contact",
    "handle_upcoming_birthdays",
    # notes
    "handle_add_note",
    "handle_show_notes",
    "handle_find_note",
    "handle_edit_note",
    "handle_delete_note",
    "handle_add_tag",
    "handle_remove_tag",
    "handle_find_by_tag",
    "handle_sort_by_tags",
]
