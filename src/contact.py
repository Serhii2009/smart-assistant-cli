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
from collections import UserDict
import re
from fields import Name, Phone, Birthday, Email, Address, Note

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones: list[Phone] = []
        self.birthday = None 
        self.email  = None 
        self.address = None 
        self.notes = []
        
    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"
    
    def add_phone(self, phone):
        self.phones.append(Phone(phone)) 

    def edit_phone(self, old_phone, new_phone):
         for p in self.phones:
            if p.value == old_phone:
                 index = self.phones.index(p)
                 self.phones[index] = Phone(new_phone)
                    
    def find_phone(self, phone):
          for p in self.phones:
               if p.value == phone:
                    return p.value
    
    def remove_phone(self, phone):
          for p in self.phones:
               if p.value == phone:
                     self.phones.remove(p)
           
    def add_birthday(self, value):
        self.birthday = Birthday(value)

    def add_email(self, value):
        self.email = Email(value)

    def add_address(self, value):
        self.address = Address(value)

    def add_note(self, note):
         self.notes.append(Note(note)) 

    def show_note(self):
          for p in self.notes:
                return '; '.join(p.value for p in self.notes)



class AddressBook(UserDict):
    
    def add_record(self, info: Record):
        self.data[info.name.value] = info
    
    def find(self, name):
         return self.data.get(name)    
         
    def delete(self, name):
          if self.data[name]:
            del self.data[name]
            return "Record has been deleted"
          else:
              return "No such name in the book"

    def get_upcoming_birthdays(self, days):
         pass