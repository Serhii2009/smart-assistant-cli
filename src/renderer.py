"""
Module: renderer.py
Responsibility: The sole module that imports and uses rich; every terminal
                output call in notii goes through a function here.

Functions:
    render_welcome()                          — startup header with frame
    render_help(commands)                     — compact /command list
    render_contacts_table(records)            — address book table
    render_contact_detail(record_dict)        — single contact panel
    render_notes_table(notes)                 — notes table
    render_note_detail(note_dict)             — single note panel
    render_birthdays_table(rows)              — upcoming birthdays table
    render_success(message)                   — green success panel
    render_error(message)                     — red error panel
    render_not_found(entity, query)           — yellow not-found panel
    render_empty(entity)                      — dim empty-collection notice

Colour palette:
    cyan          — structural borders and section titles
    spring_green2 — interactive items: command names, contact/note names, "/" hints
    bright_cyan   — subtitles and secondary labels
    yellow        — prompt labels and warnings
    green         — success messages and confirmed actions only
    red           — errors and validation failures only
    dim/white     — regular body text

Trello tasks:
    Store contacts
    Store notes
    Search contacts
    Search notes
    Upcoming birthdays
    Tags on notes
    Search and sort by tags

Dependencies (internal):
    notii (for __version__)

External libs:
    rich>=13.0.0

Assignee:
"""

"""
Module: renderer.py
Responsibility: The sole module that imports and uses rich; every terminal
                output call in notii goes through a function here.

Functions:
    render_welcome()                          — startup header with frame
    render_help(commands)                     — compact /command list
    render_contacts_table(records)            — address book table
    render_contact_detail(record_dict)        — single contact panel
    render_notes_table(notes)                 — notes table
    render_note_detail(note_dict)             — single note panel
    render_birthdays_table(rows)              — upcoming birthdays table
    render_success(message)                   — green success panel
    render_error(message)                     — red error panel
    render_not_found(entity, query)           — yellow not-found panel
    render_empty(entity)                      — dim empty-collection notice

Colour palette:
    cyan          — structural borders and section titles
    spring_green2 — interactive items: command names, contact/note names, "/" hints
    bright_cyan   — subtitles and secondary labels
    yellow        — prompt labels and warnings
    green         — success messages and confirmed actions only
    red           — errors and validation failures only
    dim/white     — regular body text

Trello tasks:
    Store contacts
    Store notes
    Search contacts
    Search notes
    Upcoming birthdays
    Tags on notes
    Search and sort by tags

Dependencies (internal):
    notii (for __version__)

External libs:
    rich>=13.0.0

Assignee:
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel


console = Console()


def render_notes_table(notes):
    table = Table(title="Notes")

    table.add_column("Title", style="spring_green2")
    table.add_column("Body", style="white")
    table.add_column("Created", style="bright_cyan")
    table.add_column("Updated", style="yellow")

    for note in notes:
        data = note.to_dict()

        body_preview = data["body"]

        if len(body_preview) > 50:
            body_preview = body_preview[:50] + "..."

        table.add_row(
            data["title"],
            body_preview,
            data["created_at"],
            data["updated_at"],
        )

    console.print(table)


def render_note_detail(note_dict):
    text = (
        f"[bright_cyan]Title:[/bright_cyan] {note_dict['title']}\n\n"
        f"[bright_cyan]Body:[/bright_cyan]\n{note_dict['body']}\n\n"
        f"[dim]Created: {note_dict['created_at']}[/dim]\n"
        f"[dim]Updated: {note_dict['updated_at']}[/dim]"
    )

    console.print(
        Panel(
            text,
            title="Note detail",
            border_style="cyan",
        )
    )


def render_birthdays_table(rows):
    table = Table(title="Upcoming birthdays")

    table.add_column("Name", style="spring_green2")
    table.add_column("Birthday", style="bright_cyan")
    table.add_column("Days left", style="yellow")
    table.add_column("Phones", style="white")
    table.add_column("Email", style="white")

    for record, days_left in rows:
        data = record.to_dict()

        table.add_row(
            data["name"],
            data["birthday"],
            str(days_left),
            data["phones"],
            data["email"],
        )

    console.print(table)


def render_welcome():
    console.print(
        Panel(
            "[spring_green2]Smart Assistant CLI[/spring_green2]\n"
            "[dim]Type /help to see available commands.[/dim]",
            title="Welcome",
            border_style="cyan",
        )
    )


def render_help(commands):
    table = Table(title="Commands")

    table.add_column("Command", style="spring_green2")
    table.add_column("Description", style="white")

    for item in commands:
        table.add_row(item["command"], item["description"])

    console.print(table)


def render_success(message):
    console.print(
        Panel(
            str(message),
            title="Success",
            border_style="green",
        )
    )


def render_error(message):
    console.print(
        Panel(
            str(message),
            title="Error",
            border_style="red",
        )
    )


def render_not_found(entity, query):
    console.print(
        Panel(
            f"{entity.capitalize()} '{query}' not found.",
            title="Not found",
            border_style="yellow",
        )
    )


def render_empty(entity):
    console.print(f"[dim]No {entity} found.[/dim]")
