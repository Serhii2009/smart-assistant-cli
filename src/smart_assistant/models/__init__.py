"""
Models package — re-exports all public domain types.

Responsibility:
    Provides a single import surface so the rest of the codebase can use
    ``from smart_assistant.models import Record, AddressBook, Note, NoteBook``
    without knowing the internal file structure.

    This file must not contain business logic.

Assignee:
"""

from smart_assistant.models.contact import AddressBook, Record
from smart_assistant.models.fields import Address, Birthday, Email, Field, Name, Phone, Tag
from smart_assistant.models.note import Note, NoteBook

__all__ = [
    # fields
    "Field",
    "Name",
    "Phone",
    "Email",
    "Birthday",
    "Address",
    "Tag",
    # contacts
    "Record",
    "AddressBook",
    # notes
    "Note",
    "NoteBook",
]
