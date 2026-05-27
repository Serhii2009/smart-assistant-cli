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
from datetime import datetime
import re
from abc import ABC, abstractmethod

#validate() ??? ABC @abstractmethod 
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
		pass


class Phone(Field):
    def __init__(self, value):
            pattern = r"^\+?\d{10,14}$"
            match = re.search(pattern, value)
            if match:
                  self.value = value
            else:
                  raise Exception("Phone must be E.164-compatible, 10-15 digits, optional leading +")
         

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Email(Field):
    def __init__(self, value):
        pattern = r"\w+@\w+\.\w+"
        match = re.search(pattern, value)
        if match:
            self.value = match.group()
        else:
             raise ValueError("Invalid email format.")


class Address(Field):
    pass


class Tag(Field):
    pass
