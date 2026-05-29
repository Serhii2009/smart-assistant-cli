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

from collections import UserDict
import re
from fields import Name, Phone, Birthday, Email, Address

# Note and NoteBook are defined in note.py — not imported here.
# Record does not own notes; notes are managed separately by NoteBook.

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones: list[Phone] = []
        self.birthday = None 
        self.email  = None 
        self.address = None 
        
    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"
    
    def add_phone(self, phone):
        # Check for duplicates before adding
        normalised = re.sub(r"[\s\-().]+", "", phone.strip())
        if any(re.sub(r"[\s\-().]+", "", p.value) == normalised for p in self.phones):
            raise ValueError(f"Phone '{phone}' is already in this contact.")
        self.phones.append(Phone(phone)) 

    def edit_phone(self, old_phone, new_phone):
        for i, p in enumerate(self.phones):
            if p.value == old_phone:
                self.phones[i] = Phone(new_phone)
                return
        raise KeyError(f"Phone '{old_phone}' not found.")  # raise instead of silent fail
                    
    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p  # return the Phone object, not p.value
    
    def remove_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                return
        raise KeyError(f"Phone '{phone}' not found.")  # raise instead of silent fail

    def edit_name(self, new_name):
        pass

    def edit_email(self, value):
        pass

    def edit_birthday(self, value):
        pass

    def edit_address(self, value):
        pass

    def days_to_birthday():
        pass

    def matches_query(query):
        pass


class AddressBook(UserDict):
    
    def add_record(self, record: Record):
        self.data[record.name.value.lower()] = record  # lowercase key for case-insensitive lookup
    
    def find(self, name):
        record = self.data.get(name.strip().lower())
        if record is None:
            raise KeyError(f"Contact '{name}' not found.")  # raise instead of returning None silently
        return record
         
    def delete(self, name):
        key = name.strip().lower()
        if key not in self.data:
            raise KeyError(f"Contact '{name}' not found.")  # consistent error handling
        del self.data[key]

    def upcoming_birthdays(self, days):
        pass  # to be implemented — loop self.data.values(), check r.birthday.days_until <= days

    def rename(self, old, new):
        pass 

    def search(self, query):
        pass

    def all_records(self):
        for name, record in self.data.items():
            print(record)