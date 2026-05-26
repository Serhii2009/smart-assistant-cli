"""
Module: handlers.py
Responsibility: Pure business-logic functions for all contact and note commands;
                no I/O, no rendering — accepts domain objects, returns status tuples.

Functions:
    Contact handlers:
        handle_add_contact(book, name, phones, email, birthday, address)
            -> tuple[str, Record | str]
        handle_show_contacts(book)
            -> tuple[str, list[Record]]
        handle_find_contact(book, query)
            -> tuple[str, list[Record]]
        handle_edit_contact(book, name, field, old_value, new_value)
            -> tuple[str, Record | str]
        handle_delete_contact(book, name)
            -> tuple[str, str]
        handle_upcoming_birthdays(book, days_str)
            -> tuple[str, list[tuple[Record, int]] | str]

    Note handlers:
        handle_add_note(notebook, title, body)
            -> tuple[str, Note | str]
        handle_show_notes(notebook)
            -> tuple[str, list[Note]]
        handle_find_note(notebook, query)
            -> tuple[str, list[Note]]
        handle_edit_note(notebook, title, new_title, new_body)
            -> tuple[str, Note | str]
        handle_delete_note(notebook, title)
            -> tuple[str, str]
        handle_add_tag(notebook, title, tag)
            -> tuple[str, Note | str]
        handle_remove_tag(notebook, title, tag)
            -> tuple[str, Note | str]
        handle_find_by_tag(notebook, tag)
            -> tuple[str, list[Note]]
        handle_sort_by_tags(notebook)
            -> tuple[str, list[Note]]

    Return status values:
        "ok"        — success; payload is result data
        "error"     — validation or logic failure; payload is message string
        "not_found" — named entity missing; payload is message string
        "empty"     — result set is empty; payload is []

Trello tasks:
    Store contacts
    Search contacts
    Edit and delete contacts
    Upcoming birthdays
    Input validation
    Store notes
    Search notes
    Edit and delete notes
    Tags on notes
    Search and sort by tags
    Data persistence

Dependencies (internal):
    notii.contact
    notii.note

External libs:
    none

Assignee:
"""

