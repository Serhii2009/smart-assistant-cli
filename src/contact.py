"""
Module: contact.py
Trello tasks: 1, 2, 4, 5

  Task 1 — Store contacts with names, addresses, phones, emails, and birthdays
  Task 2 — Show contacts whose birthday falls within N days from today
  Task 4 — Search contacts in the address book
  Task 5 — Edit and delete contact records

Two classes to implement:

──────────────────────────────────────────────────────
Record  — a single contact entry in the address book.

  Stores:
    name     (Name field)
    phones   (list of Phone fields — a contact can have more than one)
    email    (Email field or None)
    birthday (Birthday field or None)
    address  (Address field or None)

  Phone management:
    add_phone(value)              — add a new phone; reject duplicates
    find_phone(value)             — return matching Phone or None
    edit_phone(old_value, new)    — replace one phone with another
    remove_phone(value)           — delete a phone

  Field setters (one per optional field):
    edit_name(new_name)
    edit_email(value)  /  clear_email()
    edit_birthday(value)  /  clear_birthday()
    edit_address(value)  /  clear_address()

  Helpers:
    days_to_birthday()   — returns Birthday.days_until, or None if no birthday
    matches_query(query) — True if query appears anywhere in the contact
                           (name, phones, email, birthday, address),
                           case-insensitive substring match

  Serialisation:
    to_dict()  — returns a flat dict of plain strings for the renderer.
                 Use '—' for any field that is not set.

──────────────────────────────────────────────────────
AddressBook  — a UserDict of Record objects, keyed by lower-cased name.

  All name lookups are case-insensitive (normalise with .strip().lower()).

  Methods:
    add(record)         — store the record; raise ValueError if name exists
    find(name)          — return Record; raise KeyError if not found
    delete(name)        — remove; raise KeyError if not found
    rename(old, new)    — update name and re-index atomically;
                          raise KeyError if old not found,
                          ValueError if new already exists
    search(query)       — return all records where matches_query is True
    upcoming_birthdays(days)
                        — return [(record, days_remaining)] for contacts
                          whose birthday is within the next *days* days,
                          sorted ascending by days_remaining
    all_records()       — return all records sorted A–Z by name

Dependencies: fields.py (Name, Phone, Email, Birthday, Address)
Assignee: Constantine Kolesnik
"""

from __future__ import annotations

import re
from collections import UserDict
from typing import Optional

from .fields import Name, Phone, Birthday, Email, Address

class Record:

    _STRIP_RE = re.compile(r"[\s\-().]+")

    def __init__(self, name, *, phones=None, email=None, birthday=None, address=None):
        self.name = Name(name)
        self.phones: list[Phone] = []
        self.birthday = Birthday(birthday) if birthday else None
        self.email  = Email(email) if email else None
        self.address = Address(address) if address else None
        for phone in phones or []:
            self.add_phone(phone)

    def __str__(self):
        lines = [f"Name   : {self.name}"]
        if self.phones:
            lines.append("Phones : " + ", ".join(str(p) for p in self.phones))
        if self.email:
            lines.append(f"Email  : {self.email}")
        if self.birthday:
            lines.append(f"BD     : {self.birthday}  ({self.birthday.days_until} days)")
        if self.address:
            lines.append(f"Address: {self.address}")
        return "\n".join(lines)

    def _norm(self, value: str) -> str:
        return self._STRIP_RE.sub("", value.strip())

    def add_phone(self, value):
        phone = Phone(value)
        norm = self._norm(phone.value)
        if any(self._norm(p.value) == norm for p in self.phones):
            raise ValueError(f"Phone '{phone.value}' is already in this contact.")
        self.phones.append(phone)
        return phone

    def find_phone(self, value):
        norm = self._norm(value)
        return next((p for p in self.phones if self._norm(p.value) == norm), None)

    def edit_phone(self, old_value, new_value):
        old = self.find_phone(old_value)
        if old is None:
            raise KeyError(f"Phone '{old_value}' not found in '{self.name}'.")
        new = Phone(new_value)
        norm_new = self._norm(new.value)
        if any(self._norm(p.value) == norm_new and p is not old for p in self.phones):
            raise ValueError(f"Phone '{new.value}' is already in this contact.")
        self.phones[self.phones.index(old)] = new
        return new

    def remove_phone(self, value):
        phone = self.find_phone(value)
        if phone is None:
            raise KeyError(f"Phone '{value}' not found in '{self.name}'.")
        self.phones.remove(phone)

    def edit_name(self, new_name):
        self.name = Name(new_name) # wrap in Name field, not raw string

    def edit_email(self, value):
        self.email = Email(value)

    def clear_email(self):
        self.email = None

    def edit_birthday(self, value):
        self.birthday = Birthday(value)

    def clear_birthday(self):
        self.birthday = None

    def edit_address(self, value):
        self.address = Address(value)

    def clear_address(self):
        self.address = None

    def days_to_birthday(self):
        return self.birthday.days_until if self.birthday else None

    def matches_query(self, query):
        q = query.lower()
        candidates = [
            self.name.value,
            *(p.value for p in self.phones),
            self.email.value if self.email else "",
            self.birthday.value if self.birthday else "",
            self.address.value if self.address else "",
        ]
        return any(q in c.lower() for c in candidates)

    def to_dict(self):
        return {
            "name": self.name.value,
            "phones": ", ".join(p.value for p in self.phones) or "—",
            "email": self.email.value if self.email else "—",
            "birthday": self.birthday.value if self.birthday else "—",
            "days_until_birthday": str(self.birthday.days_until) if self.birthday else "—",
            "address": self.address.value if self.address else "—",
        }


class AddressBook(UserDict):

    def add(self, record: Record):
        key = record.name.value.lower()
        if key in self.data:
            raise ValueError(f"A contact named '{record.name}' already exists.")
        self.data[key] = record

    def find(self, name):
        record = self.data.get(name.strip().lower())
        if record is None:
            raise KeyError(f"Contact '{name}' not found.")
        return record

    def delete(self, name):
        key = name.strip().lower()
        if key not in self.data:
            raise KeyError(f"Contact '{name}' not found.")
        del self.data[key]

    def rename(self, old_name, new_name):
        record = self.find(old_name)
        new_key = new_name.strip().lower()
        if new_key in self.data and new_key != old_name.strip().lower():
            raise ValueError(f"A contact named '{new_name}' already exists.")
        del self.data[old_name.strip().lower()]
        record.edit_name(new_name)
        self.data[new_key] = record

    def search(self, query):
        return [r for r in self.data.values() if r.matches_query(query)]

    def upcoming_birthdays(self, days):
        results = [
            (r, r.days_to_birthday())
            for r in self.data.values()
            if r.days_to_birthday() is not None
        ]
        filtered = [(r, d) for r, d in results if 0 <= d <= days]
        filtered.sort(key=lambda x: x[1])
        return filtered

    def all_records(self):
        return sorted(self.data.values(), key=lambda r: r.name.value.lower())
