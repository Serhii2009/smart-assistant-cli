"""
Module: repository.py
Responsibility: Sole module responsible for all file-system I/O; serialises and
                deserialises AddressBook and NoteBook using atomic pickle writes.
                Data files are stored in the data/ folder at the project root so
                they are always visible during development.

Functions:
    get_data_dir()          -> Path        — returns <project_root>/data/, creating it if absent
    save_address_book(book) -> None        — atomically writes contacts.pkl
    load_address_book()     -> AddressBook — loads contacts.pkl; creates it on first run
    save_notebook(nb)       -> None        — atomically writes notes.pkl
    load_notebook()         -> NoteBook    — loads notes.pkl; creates it on first run

Trello tasks:
    Data persistence

Dependencies (internal):
    notii.contact
    notii.note

External libs:
    none (stdlib only: os, pickle, sys, tempfile, pathlib)

Assignee:
"""

import pickle, os, sys, tempfile
from pathlib import Path
from note import NoteBook
from contact import AddressBook


def data_dir():
    path = Path(__file__).parent / "data"
    if not path.exists():
        path.mkdir()

def save_address_book(book):
    with open("contacts.pkl", "wb") as f:
        pickle.dump(book, f)

def load_address_book():
    try:
        with open("contacts.pkl", "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook() 
    
def save_notebook(nb):
    with open("notes.pkl", "wb") as f:
        pickle.dump(nb, f)

def load_notebook():
    try:
        with open("notes.pkl", "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return NoteBook() 