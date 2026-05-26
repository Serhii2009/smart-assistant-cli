"""
Field class hierarchy — the OOP foundation of Smart Assistant.

Responsibility:
    Defines an abstract base class Field and one concrete subclass for every
    contact/note attribute that requires validation.  Each subclass overrides
    validate() (polymorphism) and raises ValueError with a human-readable
    message when the supplied value is unacceptable.  Nothing outside this
    module should bypass the Field constructor to set raw values.

    This module does NOT interact with I/O, storage, or rendering.

Classes:
    Field(ABC):       Abstract base — stores .value after calling validate()
    Name(Field):      Contact full name — non-empty string, max 100 chars
    Phone(Field):     Phone number — E.164-like, 10-15 digits, optional leading +
    Email(Field):     E-mail address — standard RFC-5321-ish regex
    Birthday(Field):  Date of birth in DD.MM.YYYY — exposes .date and .days_until
    Address(Field):   Street address — non-empty string, max 200 chars
    Tag(Field):       Note tag — alphanumeric + underscore + hyphen, max 50 chars;
                      __str__ prefixes the value with '#'

Validation rules:
    Name    — stripped, len 1–100
    Phone   — strip spaces/dashes/parentheses, then r'^\+?[0-9]{10,15}$'
    Email   — r'^[a-zA-Z0-9._%+\\-]+@[a-zA-Z0-9.\\-]+\\.[a-zA-Z]{2,}$'
    Birthday— strptime('%d.%m.%Y'); leap-year Feb 29 stored as-is
    Address — stripped, len 1–200
    Tag     — r'^[a-zA-Z0-9_-]{1,50}$' (no spaces)

Dependencies (internal):
    none

External libs:
    none (stdlib only: abc, re, datetime)

Assignee:
"""

from __future__ import annotations

import datetime
import re
from abc import ABC, abstractmethod


class Field(ABC):
    """
    Abstract base for all typed contact/note fields.

    Subclasses must implement validate(value) which either returns the
    normalised string to store or raises ValueError.
    """

    def __init__(self, value: str) -> None:
        self.value: str = self.validate(value)

    @abstractmethod
    def validate(self, value: str) -> str:
        """Return normalised value or raise ValueError."""

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value!r})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Field):
            return self.value == other.value
        return NotImplemented

    def __hash__(self) -> int:
        return hash((self.__class__.__name__, self.value))


# ──────────────────────────────────────────────────────────────────────────────
# Concrete field types
# ──────────────────────────────────────────────────────────────────────────────


class Name(Field):
    """Contact full name — non-empty, max 100 characters."""

    def validate(self, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Name cannot be empty.")
        if len(cleaned) > 100:
            raise ValueError("Name must be 100 characters or fewer.")
        return cleaned


class Phone(Field):
    """
    Phone number field.

    Accepts numbers with optional leading '+', spaces, dashes, and
    parentheses which are stripped before validation.  The stored value
    contains only digits and an optional leading '+'.
    """

    _STRIP_CHARS_RE = re.compile(r"[\s\-().]+")
    _VALID_RE = re.compile(r"^\+?[0-9]{10,15}$")

    def validate(self, value: str) -> str:
        normalised = self._STRIP_CHARS_RE.sub("", value.strip())
        if not self._VALID_RE.match(normalised):
            raise ValueError(
                f"Invalid phone number: '{value}'. "
                "Expected 10–15 digits, optionally prefixed with '+'."
            )
        return normalised


class Email(Field):
    """E-mail address — validated with a standard pattern."""

    _VALID_RE = re.compile(
        r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    )

    def validate(self, value: str) -> str:
        cleaned = value.strip()
        if not self._VALID_RE.match(cleaned):
            raise ValueError(
                f"Invalid e-mail address: '{value}'. "
                "Expected format: user@domain.tld"
            )
        return cleaned


class Birthday(Field):
    """
    Birthday stored as DD.MM.YYYY.

    Additional attributes:
        date: datetime.date  — the parsed date object
        days_until: int      — days until next birthday occurrence from today
    """

    _FMT = "%d.%m.%Y"

    def validate(self, value: str) -> str:
        cleaned = value.strip()
        try:
            self._date = datetime.datetime.strptime(cleaned, self._FMT).date()
        except ValueError:
            raise ValueError(
                f"Invalid birthday: '{value}'. "
                "Expected format: DD.MM.YYYY  (e.g. 31.12.1990)"
            )
        return cleaned

    @property
    def date(self) -> datetime.date:
        return self._date

    @property
    def days_until(self) -> int:
        """Days until the next anniversary of this birthday from today."""
        today = datetime.date.today()
        # Handle Feb 29 in non-leap years gracefully
        try:
            next_bday = self._date.replace(year=today.year)
        except ValueError:
            # Feb 29 doesn't exist this year — use Feb 28
            next_bday = datetime.date(today.year, 2, 28)
        if next_bday < today:
            try:
                next_bday = next_bday.replace(year=today.year + 1)
            except ValueError:
                next_bday = datetime.date(today.year + 1, 2, 28)
        return (next_bday - today).days


class Address(Field):
    """Street/postal address — non-empty, max 200 characters."""

    def validate(self, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Address cannot be empty.")
        if len(cleaned) > 200:
            raise ValueError("Address must be 200 characters or fewer.")
        return cleaned


class Tag(Field):
    """
    Note tag — alphanumeric, underscores, and hyphens; no spaces; max 50 chars.

    __str__ returns '#value' for display purposes while .value stores the
    bare tag string for comparison and storage.
    """

    _VALID_RE = re.compile(r"^[a-zA-Z0-9_-]{1,50}$")

    def validate(self, value: str) -> str:
        # Strip a leading '#' if the user typed it
        cleaned = value.strip().lstrip("#")
        if not self._VALID_RE.match(cleaned):
            raise ValueError(
                f"Invalid tag: '{value}'. "
                "Tags must be 1–50 characters of letters, digits, "
                "underscores, or hyphens — no spaces."
            )
        return cleaned

    def __str__(self) -> str:  # override for display
        return f"#{self.value}"
