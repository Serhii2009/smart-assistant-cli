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