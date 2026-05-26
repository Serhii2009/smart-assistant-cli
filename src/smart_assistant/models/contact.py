"""
Contact domain model: Record and AddressBook.

Responsibility:
    Defines Record (a single contact) which composes Field instances, and
    AddressBook (a UserDict-based collection of Records) which provides
    CRUD, search, and birthday-lookup operations.

    This module does NOT interact with I/O, storage, or rendering.  All
    validation is delegated to the Field constructors in fields.py.

Classes:
    Record:       A single contact entry with name, phones, email,
                  birthday, and address.
    AddressBook:  UserDict[str, Record] providing add/find/delete/search
                  and upcoming_birthdays.

Functions:
    (none at module level — all logic is encapsulated in the classes)

Validation rules:
    Duplicate phone numbers within one Record are rejected (normalised
    comparison).  Duplicate contact names in AddressBook are rejected
    (case-insensitive).

Dependencies (internal):
    smart_assistant.models.fields

External libs:
    none (stdlib only: collections)

Assignee:
"""

from __future__ import annotations

import datetime
from collections import UserDict
from typing import Optional

from smart_assistant.models.fields import Address, Birthday, Email, Name, Phone


class Record:
    """
    Represents a single contact in the address book.

    Attributes
    ----------
    name : Name
        Primary identifier — immutable via the public API (use edit_name).
    phones : list[Phone]
        Zero or more phone numbers.
    email : Email | None
        Optional e-mail address.
    birthday : Birthday | None
        Optional date of birth.
    address : Address | None
        Optional street/postal address.
    """

    def __init__(
        self,
        name: str,
        *,
        phones: Optional[list[str]] = None,
        email: Optional[str] = None,
        birthday: Optional[str] = None,
        address: Optional[str] = None,
    ) -> None:
        self.name = Name(name)
        self.phones: list[Phone] = []
        self.email: Optional[Email] = Email(email) if email else None
        self.birthday: Optional[Birthday] = Birthday(birthday) if birthday else None
        self.address: Optional[Address] = Address(address) if address else None

        for phone in phones or []:
            self.add_phone(phone)

    # ── Phone management ─────────────────────────────────────────────────────

    @staticmethod
    def _normalise_phone(value: str) -> str:
        """Strip formatting characters so phones compare correctly."""
        import re
        return re.sub(r"[\s\-().]+", "", value.strip())

    def add_phone(self, value: str) -> Phone:
        """
        Create and append a Phone.  Raises ValueError if invalid or duplicate.
        """
        phone = Phone(value)  # validation inside Phone
        norm = self._normalise_phone(phone.value)
        if any(self._normalise_phone(p.value) == norm for p in self.phones):
            raise ValueError(f"Phone '{phone.value}' is already in this contact.")
        self.phones.append(phone)
        return phone

    def find_phone(self, value: str) -> Optional[Phone]:
        """Return the matching Phone object or None (normalised comparison)."""
        norm = self._normalise_phone(value)
        for phone in self.phones:
            if self._normalise_phone(phone.value) == norm:
                return phone
        return None

    def edit_phone(self, old_value: str, new_value: str) -> Phone:
        """
        Replace a phone number in-place.

        Raises
        ------
        KeyError  — if old_value is not found
        ValueError — if new_value is invalid or already present
        """
        old_phone = self.find_phone(old_value)
        if old_phone is None:
            raise KeyError(f"Phone '{old_value}' not found in contact '{self.name}'.")
        new_phone = Phone(new_value)  # validate first
        norm_new = self._normalise_phone(new_phone.value)
        # Allow replacing a phone with an equivalent normalised form of itself
        if any(
            self._normalise_phone(p.value) == norm_new and p is not old_phone
            for p in self.phones
        ):
            raise ValueError(f"Phone '{new_phone.value}' is already in this contact.")
        idx = self.phones.index(old_phone)
        self.phones[idx] = new_phone
        return new_phone

    def remove_phone(self, value: str) -> None:
        """
        Remove a phone number.

        Raises
        ------
        KeyError — if the phone is not found
        """
        phone = self.find_phone(value)
        if phone is None:
            raise KeyError(f"Phone '{value}' not found in contact '{self.name}'.")
        self.phones.remove(phone)

    # ── Birthday helpers ─────────────────────────────────────────────────────

    def days_to_birthday(self) -> Optional[int]:
        """Return days until next birthday, or None if no birthday is set."""
        return self.birthday.days_until if self.birthday else None

    # ── Field setters ─────────────────────────────────────────────────────────

    def edit_name(self, new_name: str) -> None:
        """Update the contact's name (validates via Name constructor)."""
        self.name = Name(new_name)

    def edit_email(self, new_email: str) -> None:
        self.email = Email(new_email)

    def clear_email(self) -> None:
        self.email = None

    def edit_birthday(self, new_birthday: str) -> None:
        self.birthday = Birthday(new_birthday)

    def clear_birthday(self) -> None:
        self.birthday = None

    def edit_address(self, new_address: str) -> None:
        self.address = Address(new_address)

    def clear_address(self) -> None:
        self.address = None

    # ── Search ───────────────────────────────────────────────────────────────

    def matches_query(self, query: str) -> bool:
        """Return True if query appears (case-insensitive) in any field."""
        q = query.lower()
        haystack = [
            self.name.value,
            *(p.value for p in self.phones),
            self.email.value if self.email else "",
            self.birthday.value if self.birthday else "",
            self.address.value if self.address else "",
        ]
        return any(q in field.lower() for field in haystack)

    # ── Serialisation for renderer ────────────────────────────────────────────

    def to_dict(self) -> dict[str, str]:
        """Return a flat string dict suitable for the renderer layer."""
        return {
            "name": self.name.value,
            "phones": ", ".join(p.value for p in self.phones) or "—",
            "email": self.email.value if self.email else "—",
            "birthday": self.birthday.value if self.birthday else "—",
            "days_until_birthday": (
                str(self.birthday.days_until) if self.birthday else "—"
            ),
            "address": self.address.value if self.address else "—",
        }

    # ── Dunder ────────────────────────────────────────────────────────────────

    def __str__(self) -> str:
        lines = [f"Name   : {self.name}"]
        if self.phones:
            lines.append("Phones : " + ", ".join(str(p) for p in self.phones))
        if self.email:
            lines.append(f"Email  : {self.email}")
        if self.birthday:
            lines.append(
                f"BD     : {self.birthday}  ({self.birthday.days_until} days)"
            )
        if self.address:
            lines.append(f"Address: {self.address}")
        return "\n".join(lines)

    def __repr__(self) -> str:
        return f"Record(name={self.name!r})"


# ──────────────────────────────────────────────────────────────────────────────


class AddressBook(UserDict[str, Record]):
    """
    A case-insensitive dictionary of Record objects.

    Keys are lower-cased contact names.  All public methods use the
    contact's display name (any case) and normalise internally.
    """

    # ── CRUD ─────────────────────────────────────────────────────────────────

    def add(self, record: Record) -> None:
        """
        Add a Record.  Raises ValueError if a contact with the same name
        (case-insensitive) already exists.
        """
        key = record.name.value.lower()
        if key in self.data:
            raise ValueError(
                f"A contact named '{record.name}' already exists. "
                "Use edit-contact to modify it."
            )
        self.data[key] = record

    def find(self, name: str) -> Record:
        """
        Return the Record for *name*.

        Raises
        ------
        KeyError — if no contact matches
        """
        record = self.data.get(name.lower())
        if record is None:
            raise KeyError(f"Contact '{name}' not found.")
        return record

    def delete(self, name: str) -> None:
        """
        Delete a contact by name.

        Raises
        ------
        KeyError — if not found
        """
        key = name.lower()
        if key not in self.data:
            raise KeyError(f"Contact '{name}' not found.")
        del self.data[key]

    def rename(self, old_name: str, new_name: str) -> None:
        """
        Rename a contact (changes both the Record.name and the dict key).

        Raises
        ------
        KeyError   — if old_name is not found
        ValueError — if new_name already exists
        """
        record = self.find(old_name)
        new_key = new_name.strip().lower()
        if new_key in self.data and new_key != old_name.lower():
            raise ValueError(f"A contact named '{new_name}' already exists.")
        del self.data[old_name.lower()]
        record.edit_name(new_name)
        self.data[new_key] = record

    # ── Search ────────────────────────────────────────────────────────────────

    def search(self, query: str) -> list[Record]:
        """Return all records where any field contains *query* (case-insensitive)."""
        return [r for r in self.data.values() if r.matches_query(query)]

    # ── Birthday lookup ───────────────────────────────────────────────────────

    def upcoming_birthdays(self, days: int) -> list[tuple[Record, int]]:
        """
        Return (record, days_remaining) pairs for contacts whose birthday
        falls within *days* days from today, sorted by days_remaining ascending.
        """
        results: list[tuple[Record, int]] = []
        for record in self.data.values():
            remaining = record.days_to_birthday()
            if remaining is not None and 0 <= remaining <= days:
                results.append((record, remaining))
        results.sort(key=lambda x: x[1])
        return results

    # ── Convenience ───────────────────────────────────────────────────────────

    def all_records(self) -> list[Record]:
        """All records sorted alphabetically by name."""
        return sorted(self.data.values(), key=lambda r: r.name.value.lower())
