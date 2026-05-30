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

console = Console()


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
