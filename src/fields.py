"""
Module: fields.py
Trello task: Task 3 — Validate phone and email

This file defines the typed field classes used across the whole project.
Every field wraps a raw string, validates it, and stores the cleaned result
in self.value.  If the value is invalid, raise ValueError with a message
the user will see.  If valid, store the cleaned string in self.value.

Six field types to implement (each inherits from Field below):

  Name     — non-empty string, max 100 characters
  Phone    — 10–15 digits, optional leading '+'; strip spaces, hyphens,
             dots, and brackets before checking
  Email    — standard user@domain.tld pattern
  Birthday — DD.MM.YYYY format; must be a past date (not in the future)
             also expose:
               .date       → datetime.date (the parsed date object)
               .days_until → int  (days until the next annual celebration
                             from today; 0 if today is the birthday)
  Address  — non-empty string, max 200 characters
  Tag      — letters, digits, underscores '_', and hyphens '-' only;
             max 50 characters; strip a leading '#' if the user typed one;
             __str__ must return '#' + self.value for display

The abstract Field base class is already fully implemented below — do not
change it.  Each subclass only needs to implement validate(value: str) -> str.

Dependencies: abc, re, datetime  (stdlib only)
Assignee: Constantine Kolesnik
"""

from datetime import datetime
import re
from abc import ABC, abstractmethod

# validate() is an abstract method defined in Field base class.
# Each subclass must override it — this is how polymorphism works here.
# ABC means "Abstract Base Class": you cannot instantiate Field directly, only its subclasses.
# @abstractmethod forces every subclass to implement validate() or Python will raise an error at runtime.
# Also, you may add some type hints!

class Field(ABC): # inherit from ABC, not plain object
    def __init__(self, value):
        self.value = self.validate(value)  # validate on creation, not manually

	@abstractmethod
	def validate(self, value: str) -> str:
		"""Return the cleaned value or raise ValueError."""
		
    def __str__(self):
        return str(self.value)


class Name(Field):
	def validate(self, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Name cannot be empty.")
        return cleaned


class Phone(Field):
    def validate(self, value):
		pattern = r"^\+?\d{10,15}$"
		normalised = re.sub(r"[\s\-().]+", "", value.strip())
		if not re.match(pattern, normalised):
			raise ValueError(
				f"Invalid phone: '{value}'. Phone must be E.164-compatible, 10-15 digits, optional leading +"
			)
		return normalised  # store the cleaned version, not the raw input


class Birthday(Field):
    def validate(self, value):
        try:
            self._date = datetime.strptime(value.strip(), "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
		return value.strip()


class Email(Field):
    def validate(self, value):
        pattern = r"\w+@\w+\.\w+"
		cleaned = value.strip()
        if not re.match(pattern, cleaned):
            raise ValueError("Invalid email format.")
        return cleaned  # store cleaned, not re.search().group()


class Address(Field):
    def validate(self, value: str) -> str:
        pass


class Tag(Field):
    def validate(self, value: str) -> str:
        pass
