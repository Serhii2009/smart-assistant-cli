"""
CLI entry point and REPL loop.

Responsibility:
    Owns the application lifecycle: startup banner, interactive REPL loop,
    graceful shutdown with data persistence.  Dispatches parsed commands
    to pure handler functions; passes their results to the renderer.

    This module is the ONLY place that calls both storage (load/save) and
    renderer functions.  It is also the only place that calls input/prompt.

Classes:
    (none — the module is procedural at the top level)

Functions:
    run() -> None
        Main entry point.  Loads data, starts REPL, saves data on exit.

    _dispatch(command, args, book, notebook) -> None
        Routes a parsed command string to the correct handler + renderer call.

    _prompt_contact_fields(session) -> dict
        Interactively collects contact field values using prompt_toolkit.

    _prompt_note_fields(session) -> dict
        Interactively collects title and body for a new note.

Constants:
    COMMANDS     : list[str]  — all recognised command strings (drives autocomplete)
    COMMAND_HELP : list[dict] — {command, description, example} rows for render_help()

Validation rules:
    Input gathering is done here; all value validation is done in models/handlers.
    Empty-string responses to optional prompts are passed as None to handlers.

Dependencies (internal):
    smart_assistant.handlers
    smart_assistant.storage
    smart_assistant.ui

External libs:
    prompt_toolkit>=3.0.0

Assignee:
"""

from __future__ import annotations

from typing import Optional

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory

from smart_assistant.handlers.contacts import (
    handle_add_contact,
    handle_delete_contact,
    handle_edit_contact,
    handle_find_contact,
    handle_show_contacts,
    handle_upcoming_birthdays,
)
from smart_assistant.handlers.notes import (
    handle_add_note,
    handle_add_tag,
    handle_delete_note,
    handle_edit_note,
    handle_find_by_tag,
    handle_find_note,
    handle_remove_tag,
    handle_show_notes,
    handle_sort_by_tags,
)
from smart_assistant.models.contact import AddressBook
from smart_assistant.models.note import NoteBook
from smart_assistant.storage.repository import (
    get_data_dir,
    load_address_book,
    load_notebook,
    save_address_book,
    save_notebook,
)
from smart_assistant.ui.renderer import (
    render_birthdays_table,
    render_contact_detail,
    render_contacts_table,
    render_empty,
    render_error,
    render_help,
    render_not_found,
    render_note_detail,
    render_notes_table,
    render_success,
    render_welcome,
)

# ── Command registry ───────────────────────────────────────────────────────────

COMMANDS: list[str] = [
    "add-contact",
    "show-contacts",
    "find-contact",
    "edit-contact",
    "delete-contact",
    "birthdays",
    "add-note",
    "show-notes",
    "find-note",
    "edit-note",
    "delete-note",
    "add-tag",
    "remove-tag",
    "find-by-tag",
    "sort-by-tags",
    "help",
    "exit",
    "quit",
    "close",
]

COMMAND_HELP: list[dict] = [
    # ── Contacts ───────────────────────────────────────────────────
    {
        "command": "add-contact",
        "description": "Add a new contact (interactive)",
        "example": "add-contact",
    },
    {
        "command": "show-contacts",
        "description": "List all contacts",
        "example": "show-contacts",
    },
    {
        "command": "find-contact <query>",
        "description": "Search contacts by any field",
        "example": "find-contact Alice",
    },
    {
        "command": "edit-contact <name>",
        "description": "Edit a field of an existing contact",
        "example": "edit-contact Alice",
    },
    {
        "command": "delete-contact <name>",
        "description": "Delete a contact",
        "example": "delete-contact Alice",
    },
    {
        "command": "birthdays <days>",
        "description": "Contacts with a birthday in the next N days",
        "example": "birthdays 30",
    },
    # ── Notes ──────────────────────────────────────────────────────
    {
        "command": "add-note",
        "description": "Create a new note (interactive)",
        "example": "add-note",
    },
    {
        "command": "show-notes",
        "description": "List all notes",
        "example": "show-notes",
    },
    {
        "command": "find-note <query>",
        "description": "Search notes by title or body",
        "example": "find-note meeting",
    },
    {
        "command": "edit-note <title>",
        "description": "Edit a note's title or body",
        "example": "edit-note 'My Note'",
    },
    {
        "command": "delete-note <title>",
        "description": "Delete a note",
        "example": "delete-note 'My Note'",
    },
    # ── Tags ───────────────────────────────────────────────────────
    {
        "command": "add-tag <title> <tag>",
        "description": "Attach a tag to a note",
        "example": "add-tag 'My Note' work",
    },
    {
        "command": "remove-tag <title> <tag>",
        "description": "Remove a tag from a note",
        "example": "remove-tag 'My Note' work",
    },
    {
        "command": "find-by-tag <tag>",
        "description": "Find notes by tag",
        "example": "find-by-tag work",
    },
    {
        "command": "sort-by-tags",
        "description": "List notes sorted alphabetically by tag",
        "example": "sort-by-tags",
    },
    # ── System ─────────────────────────────────────────────────────
    {
        "command": "help",
        "description": "Show this help table",
        "example": "help",
    },
    {
        "command": "exit / quit / close",
        "description": "Save data and exit",
        "example": "exit",
    },
]


# ── Input helpers ─────────────────────────────────────────────────────────────


def _ask(session: PromptSession, label: str, required: bool = False) -> str:
    """Prompt for a single value, re-asking if *required* and left blank."""
    while True:
        value = session.prompt(f"  {label}: ").strip()
        if value or not required:
            return value
        render_error(f"'{label}' is required — please enter a value.")


def _prompt_contact_fields(session: PromptSession) -> dict:
    """
    Interactively gather all contact fields.

    Returns a dict with keys: name, phones, email, birthday, address.
    Phone input accepts a comma-separated list; parsed into list[str].
    """
    from smart_assistant.ui.renderer import CONSOLE
    CONSOLE.print("\n[bold cyan]  ── New Contact ──[/bold cyan]")
    name = _ask(session, "Full name", required=True)
    phones_raw = _ask(session, "Phone(s) [comma-separated, or blank]")
    phones = [p.strip() for p in phones_raw.split(",") if p.strip()] if phones_raw else []
    email = _ask(session, "E-mail [or blank]")
    birthday = _ask(session, "Birthday DD.MM.YYYY [or blank]")
    address = _ask(session, "Address [or blank]")
    return {
        "name": name,
        "phones": phones,
        "email": email or None,
        "birthday": birthday or None,
        "address": address or None,
    }


def _prompt_note_fields(session: PromptSession) -> dict:
    """Interactively gather note title and body."""
    from smart_assistant.ui.renderer import CONSOLE
    CONSOLE.print("\n[bold cyan]  ── New Note ──[/bold cyan]")
    title = _ask(session, "Title", required=True)
    CONSOLE.print("  [dim]Body (press Enter twice to finish):[/dim]")
    lines: list[str] = []
    while True:
        try:
            line = session.prompt("  ")
        except KeyboardInterrupt:
            break
        if line == "" and lines and lines[-1] == "":
            break
        lines.append(line)
    body = "\n".join(lines).strip()
    return {"title": title, "body": body}


def _prompt_edit_contact(session: PromptSession, record_name: str) -> dict:
    """Prompt for which field to edit and the new value(s)."""
    from smart_assistant.ui.renderer import CONSOLE
    CONSOLE.print(
        f"\n[bold cyan]  ── Edit Contact: {record_name} ──[/bold cyan]\n"
        "  Fields: [bold]name[/bold]  [bold]add-phone[/bold]  [bold]remove-phone[/bold]  "
        "[bold]phone[/bold] (edit)  [bold]email[/bold]  [bold]birthday[/bold]  [bold]address[/bold]"
    )
    field = _ask(session, "Field to edit", required=True)
    field = field.lower().strip()

    old_value = ""
    if field == "phone":
        old_value = _ask(session, "Current phone value", required=True)
        new_value = _ask(session, "New phone value", required=True)
    elif field == "remove-phone":
        new_value = _ask(session, "Phone to remove", required=True)
    elif field == "add-phone":
        new_value = _ask(session, "New phone to add", required=True)
    else:
        new_value = _ask(session, f"New value for '{field}' [blank to clear]")

    return {"field": field, "old_value": old_value, "new_value": new_value}


def _prompt_edit_note(session: PromptSession, note_title: str) -> dict:
    """Prompt for which note fields to update."""
    from smart_assistant.ui.renderer import CONSOLE
    CONSOLE.print(
        f"\n[bold cyan]  ── Edit Note: {note_title} ──[/bold cyan]\n"
        "  Leave blank to keep the current value."
    )
    new_title = _ask(session, "New title [or blank to keep]")
    new_body_flag = _ask(session, "Edit body? [y/n]")
    new_body: Optional[str] = None
    if new_body_flag.lower().startswith("y"):
        CONSOLE.print("  [dim]New body (press Enter twice to finish):[/dim]")
        lines: list[str] = []
        while True:
            try:
                line = session.prompt("  ")
            except KeyboardInterrupt:
                break
            if line == "" and lines and lines[-1] == "":
                break
            lines.append(line)
        new_body = "\n".join(lines).strip()

    return {
        "new_title": new_title or None,
        "new_body": new_body,
    }


# ── Command dispatcher ────────────────────────────────────────────────────────


def _dispatch(
    command: str,
    args: list[str],
    book: AddressBook,
    notebook: NoteBook,
    session: PromptSession,
) -> None:
    """Route a parsed command to the correct handler and renderer."""

    # ── Contacts ───────────────────────────────────────────────────────────────
    if command == "add-contact":
        fields = _prompt_contact_fields(session)
        status, payload = handle_add_contact(
            book,
            fields["name"],
            phones=fields["phones"],
            email=fields["email"],
            birthday=fields["birthday"],
            address=fields["address"],
        )
        if status == "ok":
            render_success(f"Contact '[bold]{payload.name}[/bold]' added successfully.")  # type: ignore[union-attr]
        else:
            render_error(str(payload))

    elif command == "show-contacts":
        status, payload = handle_show_contacts(book)
        if status == "ok":
            render_contacts_table([r.to_dict() for r in payload])  # type: ignore[union-attr]
        else:
            render_empty("contacts")

    elif command == "find-contact":
        query = " ".join(args).strip()
        if not query:
            render_error("Usage: find-contact <query>")
            return
        status, payload = handle_find_contact(book, query)
        if status == "ok":
            render_contacts_table([r.to_dict() for r in payload])  # type: ignore[union-attr]
        elif status == "empty":
            render_not_found("contacts", query)
        else:
            render_error(str(payload))

    elif command == "edit-contact":
        name = " ".join(args).strip()
        if not name:
            render_error("Usage: edit-contact <name>")
            return
        # Verify the contact exists before prompting
        try:
            book.find(name)
        except KeyError:
            render_not_found("contact", name)
            return
        edit_fields = _prompt_edit_contact(session, name)
        status, payload = handle_edit_contact(
            book,
            name,
            edit_fields["field"],
            old_value=edit_fields["old_value"],
            new_value=edit_fields["new_value"],
        )
        if status == "ok":
            render_success(f"Contact '[bold]{payload.name}[/bold]' updated.")  # type: ignore[union-attr]
        elif status == "not_found":
            render_not_found("contact or phone", str(payload))
        else:
            render_error(str(payload))

    elif command == "delete-contact":
        name = " ".join(args).strip()
        if not name:
            render_error("Usage: delete-contact <name>")
            return
        status, payload = handle_delete_contact(book, name)
        if status == "ok":
            render_success(f"Contact '[bold]{payload}[/bold]' deleted.")
        else:
            render_not_found("contact", name)

    elif command == "birthdays":
        days_str = args[0] if args else ""
        if not days_str:
            render_error("Usage: birthdays <days>  (e.g. birthdays 30)")
            return
        status, payload = handle_upcoming_birthdays(book, days_str)
        if status == "ok":
            rows = [
                {
                    "name": rec.name.value,
                    "birthday": rec.birthday.value,  # type: ignore[union-attr]
                    "days_remaining": str(days),
                }
                for rec, days in payload  # type: ignore[misc]
            ]
            render_birthdays_table(rows)
        elif status == "empty":
            render_not_found("birthdays", f"next {days_str} days")
        else:
            render_error(str(payload))

    # ── Notes ──────────────────────────────────────────────────────────────────
    elif command == "add-note":
        fields = _prompt_note_fields(session)
        status, payload = handle_add_note(notebook, fields["title"], fields["body"])
        if status == "ok":
            render_success(f"Note '[bold]{payload.title}[/bold]' created.")  # type: ignore[union-attr]
        else:
            render_error(str(payload))

    elif command == "show-notes":
        status, payload = handle_show_notes(notebook)
        if status == "ok":
            render_notes_table([n.to_dict() for n in payload])  # type: ignore[union-attr]
        else:
            render_empty("notes")

    elif command == "find-note":
        query = " ".join(args).strip()
        if not query:
            render_error("Usage: find-note <query>")
            return
        status, payload = handle_find_note(notebook, query)
        if status == "ok":
            render_notes_table([n.to_dict() for n in payload])  # type: ignore[union-attr]
        elif status == "empty":
            render_not_found("notes", query)
        else:
            render_error(str(payload))

    elif command == "edit-note":
        title = " ".join(args).strip()
        if not title:
            render_error("Usage: edit-note <title>")
            return
        # Verify note exists first
        try:
            notebook.get(title)
        except KeyError:
            render_not_found("note", title)
            return
        edit_fields = _prompt_edit_note(session, title)
        status, payload = handle_edit_note(
            notebook,
            title,
            new_title=edit_fields["new_title"],
            new_body=edit_fields["new_body"],
        )
        if status == "ok":
            render_success(f"Note '[bold]{payload.title}[/bold]' updated.")  # type: ignore[union-attr]
        elif status == "not_found":
            render_not_found("note", title)
        else:
            render_error(str(payload))

    elif command == "delete-note":
        title = " ".join(args).strip()
        if not title:
            render_error("Usage: delete-note <title>")
            return
        status, payload = handle_delete_note(notebook, title)
        if status == "ok":
            render_success(f"Note '[bold]{payload}[/bold]' deleted.")
        else:
            render_not_found("note", title)

    # ── Tags ───────────────────────────────────────────────────────────────────
    elif command == "add-tag":
        # Syntax: add-tag <note-title> <tag>   (title may be multi-word if quoted)
        # Simple heuristic: last token is the tag, everything before is the title
        if len(args) < 2:
            render_error("Usage: add-tag <note-title> <tag>")
            return
        tag = args[-1]
        title = " ".join(args[:-1]).strip()
        status, payload = handle_add_tag(notebook, title, tag)
        if status == "ok":
            render_success(f"Tag '[bold]#{tag}[/bold]' added to '[bold]{payload.title}[/bold]'.")  # type: ignore[union-attr]
        elif status == "not_found":
            render_not_found("note", title)
        else:
            render_error(str(payload))

    elif command == "remove-tag":
        if len(args) < 2:
            render_error("Usage: remove-tag <note-title> <tag>")
            return
        tag = args[-1]
        title = " ".join(args[:-1]).strip()
        status, payload = handle_remove_tag(notebook, title, tag)
        if status == "ok":
            render_success(f"Tag '[bold]#{tag}[/bold]' removed from '[bold]{payload.title}[/bold]'.")  # type: ignore[union-attr]
        elif status == "not_found":
            render_not_found("note or tag", f"{title} / {tag}")
        else:
            render_error(str(payload))

    elif command == "find-by-tag":
        tag = " ".join(args).strip()
        if not tag:
            render_error("Usage: find-by-tag <tag>")
            return
        status, payload = handle_find_by_tag(notebook, tag)
        if status == "ok":
            render_notes_table([n.to_dict() for n in payload])  # type: ignore[union-attr]
        elif status == "empty":
            render_not_found("notes with tag", tag)
        else:
            render_error(str(payload))

    elif command == "sort-by-tags":
        status, payload = handle_sort_by_tags(notebook)
        if status == "ok":
            render_notes_table([n.to_dict() for n in payload])  # type: ignore[union-attr]
        else:
            render_empty("notes")

    # ── System ─────────────────────────────────────────────────────────────────
    elif command == "help":
        render_help(COMMAND_HELP)

    else:
        render_error(
            f"Unknown command: [bold]'{command}'[/bold]. "
            "Type [bold]help[/bold] to see available commands."
        )


# ── Main REPL loop ────────────────────────────────────────────────────────────


def run() -> None:
    """
    Application entry point.

    1. Load persisted data from disk.
    2. Print welcome banner and help table (once).
    3. Enter the REPL loop with prompt_toolkit autocomplete.
    4. On exit: save data and print goodbye.
    """
    book = load_address_book()
    notebook = load_notebook()

    render_welcome()
    render_help(COMMAND_HELP)

    history_path = get_data_dir() / "history.txt"
    session: PromptSession = PromptSession(
        completer=WordCompleter(COMMANDS, ignore_case=True),
        history=FileHistory(str(history_path)),
        auto_suggest=AutoSuggestFromHistory(),
        complete_while_typing=True,
    )

    while True:
        try:
            raw: str = session.prompt("\n[assistant] ❯ ")
        except KeyboardInterrupt:
            # Ctrl+C cancels the current input line; keep running
            continue
        except EOFError:
            # Ctrl+D — treat as exit
            break

        raw = raw.strip()
        if not raw:
            continue

        parts = raw.split(maxsplit=1)
        command = parts[0].lower()
        rest_str = parts[1] if len(parts) > 1 else ""
        args = rest_str.split() if rest_str else []

        if command in ("exit", "quit", "close"):
            break

        try:
            _dispatch(command, args, book, notebook, session)
        except Exception as exc:  # noqa: BLE001  — last-resort safety net
            render_error(f"Unexpected error: {exc}")

    save_address_book(book)
    save_notebook(notebook)
    render_success("All data saved. Goodbye! 👋")
