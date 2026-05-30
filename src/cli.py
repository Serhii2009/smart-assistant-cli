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

from repository import (
    load_address_book,
    save_address_book,
    load_notebook,
    save_notebook,
)
from handlers import handle_upcoming_birthdays
from renderer import (
    render_welcome,
    render_help,
    render_birthdays_table,
    render_error,
    render_empty,
)


COMMANDS = [
    "/help",
    "/birthdays",
    "/exit",
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
]


def _ask(session, label, required=False):
    while True:
        value = session.prompt(f"{label}: ").strip()

        if value or not required:
            return value

        render_error(f"{label} is required.")


def _dispatch(command, book, notebook, session):
    if command == "/help":
        render_help(COMMAND_HELP)
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
