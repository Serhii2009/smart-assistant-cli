"""
Module: contact.py
Responsibility: Defines the Record (single contact) and AddressBook (contact
                collection) domain classes with CRUD, search, and birthday lookup.

Classes:
    Record      — a single address book entry composing Field instances
    AddressBook — UserDict[str, Record] with add/find/delete/search/birthdays

Functions:
    (none at module level — all logic lives on the classes)

Trello tasks:
    Store contacts
    Search contacts
    Edit and delete contacts
    Upcoming birthdays
    Data persistence

Dependencies (internal):
    notii.fields

External libs:
    none (stdlib only: collections, re)

Assignee:
"""
