"""
Module: cli.py
Responsibility: Owns the application lifecycle — startup, interactive REPL loop
                with /command autocomplete, command dispatch, and graceful shutdown.
                Every command collects its required inputs through individual
                prompted input lines; no arguments are ever typed on the same
                line as the command.

Functions:
    run()                          — main entry point; loads data, runs REPL, saves on exit
    _dispatch(command, book, ...)  — routes parsed command to handler + renderer
    _ask(session, label, required) — prompts for a single field value (yellow label)
    _prompt_contact_fields(session)— interactive contact field collection
    _prompt_note_fields(session)   — interactive note field collection
    _prompt_edit_contact(session, name) — interactive edit field selection
    _prompt_edit_note(session, title)   — interactive note edit

Constants:
    COMMANDS     — list of /command strings driving autocomplete
    COMMAND_HELP — list[dict] with command + description for /help

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
    notii.handlers
    notii.repository
    notii.renderer
    notii.contact
    notii.note

External libs:
    prompt_toolkit>=3.0.0

Assignee:
"""

"""
Module: cli.py
Responsibility: Owns the application lifecycle — startup, interactive REPL loop
                with /command autocomplete, command dispatch, and graceful shutdown.
                Every command collects its required inputs through individual
                prompted input lines; no arguments are ever typed on the same
                line as the command.

Functions:
    run()                          — main entry point; loads data, runs REPL, saves on exit
    _dispatch(command, book, ...)  — routes parsed command to handler + renderer
    _ask(session, label, required) — prompts for a single field value (yellow label)
    _prompt_contact_fields(session)— interactive contact field collection
    _prompt_note_fields(session)   — interactive note field collection
    _prompt_edit_contact(session, name) — interactive edit field selection
    _prompt_edit_note(session, title)   — interactive note edit

Constants:
    COMMANDS     — list of /command strings driving autocomplete
    COMMAND_HELP — list[dict] with command + description for /help

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
    notii.handlers
    notii.repository
    notii.renderer
    notii.contact
    notii.note

External libs:
    prompt_toolkit>=3.0.0

Assignee:
"""

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter

from .repository import (
    load_address_book,
    save_address_book,
    load_notebook,
    save_notebook,
)

from .handlers import (
    handle_add_note,
    handle_show_notes,
    handle_find_note,
    handle_edit_note,
    handle_delete_note,
    handle_upcoming_birthdays,
)
from .renderer import (
    render_welcome,
    render_help,
    render_birthdays_table,
    render_error,
    render_empty,
    render_notes_table,
    render_note_detail,
    render_success,
    render_not_found,
)


COMMANDS = [
    "/help",
    "/birthdays",
    "/exit",
    "/add-note",
    "/show-notes",
    "/find-note",
    "/edit-note",
    "/delete-note",
]


COMMAND_HELP = [
    {
        "command": "/birthdays",
        "description": "Show contacts whose birthday is within N days from today",
    },
    {
        "command": "/exit",
        "description": "Save data and exit",
    },
    {"command": "/add-note", "description": "Add a new text note"},
    {"command": "/show-notes", "description": "Show all notes"},
    {"command": "/find-note", "description": "Search notes by title or body"},
    {"command": "/edit-note", "description": "Edit note title or body"},
    {"command": "/delete-note", "description": "Delete note by title"},
]


def _ask(session, label, required=False):
    while True:
        value = session.prompt(f"{label}: ").strip()

        if value or not required:
            return value

        render_error(f"{label} is required.")


def _prompt_note_fields(session):
    title = _ask(session, "Note title", required=True)
    body = _ask(session, "Note body", required=True)

    return title, body


def _prompt_edit_note(session, title):
    new_title = _ask(session, "New note title", required=False)
    new_body = _ask(session, "New note body", required=False)

    return new_title, new_body


def _dispatch(command, book, notebook, session):
    if command == "/help":
        render_help(COMMAND_HELP)
        return

    if command == "/add-note":
        title, body = _prompt_note_fields(session)

        status, payload = handle_add_note(notebook, title, body)

        if status == "ok":
            render_success(f"Note '{payload.title}' was added.")
        else:
            render_error(payload)

        return

    if command == "/show-notes":
        status, payload = handle_show_notes(notebook)

        if status == "ok":
            render_notes_table(payload)
        elif status == "empty":
            render_empty("notes")
        else:
            render_error(payload)

        return

    if command == "/find-note":
        query = _ask(session, "Search query", required=True)

        status, payload = handle_find_note(notebook, query)

        if status == "ok":
            render_notes_table(payload)
        elif status == "empty":
            render_empty("notes")
        else:
            render_error(payload)

        return

    if command == "/edit-note":
        title = _ask(session, "Note title", required=True)
        new_title, new_body = _prompt_edit_note(session, title)

        status, payload = handle_edit_note(notebook, title, new_title, new_body)

        if status == "ok":
            render_success(f"Note '{payload.title}' was updated.")
            render_note_detail(payload.to_dict())
        elif status == "not_found":
            render_not_found("note", title)
        else:
            render_error(payload)

        return

    if command == "/delete-note":
        title = _ask(session, "Note title", required=True)

        status, payload = handle_delete_note(notebook, title)

        if status == "ok":
            render_success(payload)
        elif status == "not_found":
            render_not_found("note", title)
        else:
            render_error(payload)

        return

    if command == "/birthdays":
        days_str = _ask(session, "Days", required=True)

        status, payload = handle_upcoming_birthdays(book, days_str)

        if status == "ok":
            render_birthdays_table(payload)
        elif status == "empty":
            render_empty("birthdays")
        else:
            render_error(payload)

        return

    render_error(f"Unknown command: {command}")


def run():
    book = load_address_book()
    notebook = load_notebook()

    session = PromptSession()
    completer = WordCompleter(COMMANDS, ignore_case=True)

    render_welcome()

    while True:
        command = session.prompt("> ", completer=completer).strip()

        if command == "/exit":
            save_address_book(book)
            save_notebook(notebook)
            break

        _dispatch(command, book, notebook, session)
