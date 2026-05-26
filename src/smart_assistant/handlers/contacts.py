"""
Contact command handlers — pure business logic layer.

Responsibility:
    Implements every contact-related operation as a pure function.
    Functions receive an AddressBook and plain string arguments; they
    return a (status, payload) tuple that cli.py consumes and passes to
    the renderer.  No print(), input(), or rich calls are permitted here.

Functions:
    handle_add_contact(book, name, phones, email, birthday, address)
        -> tuple[str, Record | str]

    handle_show_contacts(book)
        -> tuple[str, list[Record]]

    handle_find_contact(book, query)
        -> tuple[str, list[Record]]

    handle_edit_contact(book, name, field, old_value, new_value)
        -> tuple[str, Record | str]
        Supported field values: "name", "phone", "add-phone",
        "remove-phone", "email", "birthday", "address"

    handle_delete_contact(book, name)
        -> tuple[str, str]

    handle_upcoming_birthdays(book, days_str)
        -> tuple[str, list[tuple[Record, int]] | str]

Return status values:
    "ok"        — operation succeeded; payload is the result data
    "error"     — operation failed due to invalid input; payload is str message
    "not_found" — named entity does not exist; payload is str message
    "empty"     — collection has no items; payload is ""

Validation rules:
    days parameter for birthdays must parse to int in 1–365 (inclusive).
    All field validation is delegated to model constructors (ValueError caught here).

Dependencies (internal):
    smart_assistant.models.contact (Record, AddressBook)

External libs:
    none

Assignee:
"""

from __future__ import annotations

from typing import Optional

from smart_assistant.models.contact import AddressBook, Record


def handle_add_contact(
    book: AddressBook,
    name: str,
    phones: Optional[list[str]] = None,
    email: Optional[str] = None,
    birthday: Optional[str] = None,
    address: Optional[str] = None,
) -> tuple[str, Record | str]:
    """
    Create and store a new contact.

    Returns
    -------
    ("ok", record)     — contact created successfully
    ("error", message) — validation failed or name already exists
    """
    try:
        record = Record(
            name,
            phones=phones or [],
            email=email or None,
            birthday=birthday or None,
            address=address or None,
        )
        book.add(record)
        return "ok", record
    except (ValueError, KeyError) as exc:
        return "error", str(exc)


def handle_show_contacts(book: AddressBook) -> tuple[str, list[Record]]:
    """
    Return all contacts sorted alphabetically.

    Returns
    -------
    ("ok", list[Record])  — at least one contact exists
    ("empty", [])         — no contacts in the book
    """
    records = book.all_records()
    if not records:
        return "empty", []
    return "ok", records


def handle_find_contact(
    book: AddressBook, query: str
) -> tuple[str, list[Record]]:
    """
    Search all contact fields for *query*.

    Returns
    -------
    ("ok", list[Record])  — matches found
    ("empty", [])         — no matches
    """
    if not query.strip():
        return "error", "Search query cannot be empty."  # type: ignore[return-value]
    results = book.search(query.strip())
    if not results:
        return "empty", []
    return "ok", results


def handle_edit_contact(
    book: AddressBook,
    name: str,
    field: str,
    old_value: str = "",
    new_value: str = "",
) -> tuple[str, Record | str]:
    """
    Edit a single field of an existing contact.

    Parameters
    ----------
    field : str
        One of: "name", "phone" (edit existing), "add-phone", "remove-phone",
        "email", "birthday", "address"
    old_value : str
        Used only for "phone" (the old phone to replace).
    new_value : str
        The replacement value (or the phone to add/remove).

    Returns
    -------
    ("ok", record)          — edit succeeded
    ("not_found", message)  — contact or phone not found
    ("error", message)      — validation failed
    """
    try:
        record = book.find(name)
    except KeyError as exc:
        return "not_found", str(exc)

    try:
        f = field.lower().strip()
        if f == "name":
            old_key = record.name.value.lower()
            record.edit_name(new_value)
            # Update the AddressBook key
            del book.data[old_key]
            book.data[record.name.value.lower()] = record
        elif f == "add-phone":
            record.add_phone(new_value)
        elif f == "remove-phone":
            record.remove_phone(new_value)
        elif f == "phone":
            record.edit_phone(old_value, new_value)
        elif f == "email":
            if new_value.strip():
                record.edit_email(new_value)
            else:
                record.clear_email()
        elif f == "birthday":
            if new_value.strip():
                record.edit_birthday(new_value)
            else:
                record.clear_birthday()
        elif f == "address":
            if new_value.strip():
                record.edit_address(new_value)
            else:
                record.clear_address()
        else:
            return "error", f"Unknown field '{field}'. Valid fields: name, phone, add-phone, remove-phone, email, birthday, address."
    except KeyError as exc:
        return "not_found", str(exc)
    except ValueError as exc:
        return "error", str(exc)

    return "ok", record


def handle_delete_contact(
    book: AddressBook, name: str
) -> tuple[str, str]:
    """
    Delete a contact by name.

    Returns
    -------
    ("ok", name)            — deleted successfully
    ("not_found", message)  — contact does not exist
    """
    try:
        book.delete(name)
        return "ok", name
    except KeyError as exc:
        return "not_found", str(exc)


def handle_upcoming_birthdays(
    book: AddressBook, days_str: str
) -> tuple[str, list[tuple[Record, int]] | str]:
    """
    List contacts with a birthday in the next *days_str* days.

    Parameters
    ----------
    days_str : str
        Number of days as a string; validated to be an integer in 1–365.

    Returns
    -------
    ("ok", list[(record, days_remaining)])  — results found
    ("empty", [])                           — no birthdays in window
    ("error", message)                      — invalid days value
    """
    try:
        days = int(days_str)
    except (ValueError, TypeError):
        return "error", f"'{days_str}' is not a valid number. Please enter a whole number."  # type: ignore[return-value]

    if not (1 <= days <= 365):
        return "error", "Days must be between 1 and 365."  # type: ignore[return-value]

    results = book.upcoming_birthdays(days)
    if not results:
        return "empty", []
    return "ok", results
