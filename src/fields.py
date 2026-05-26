"""
Module: fields.py
Responsibility: Defines the abstract Field base class and all concrete field
                types used by contacts and notes, each with its own validation logic.

Classes:
    Field    — abstract base; stores .value after calling validate()
    Name     — contact full name; non-empty, max 100 chars
    Phone    — phone number; E.164-compatible, 10-15 digits, optional leading +
    Email    — e-mail address; standard format regex
    Birthday — date of birth in DD.MM.YYYY; exposes .date and .days_until
    Address  — street address; non-empty, max 200 chars
    Tag      — note keyword tag; alphanumeric + underscore/hyphen, max 50 chars

Trello tasks:
    Input validation
    Store contacts
    Tags on notes

Dependencies (internal):
    none

External libs:
    none (stdlib only: abc, re, datetime)

Assignee:
"""
