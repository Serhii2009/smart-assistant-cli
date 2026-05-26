"""
Terminal rendering module — the sole user of rich in Smart Assistant.

Responsibility:
    Contains EVERY rich output call in the application.  No other module
    may import or instantiate rich objects.  Functions accept plain Python
    dicts (produced by model.to_dict()) or primitive values so the renderer
    has zero dependency on domain objects.

    Uses a single module-level Console instance for consistent theming and
    colour support.

Functions:
    render_welcome() -> None
    render_help(commands: list[dict]) -> None
    render_contacts_table(records: list[dict]) -> None
    render_contact_detail(record_dict: dict) -> None
    render_notes_table(notes: list[dict]) -> None
    render_note_detail(note_dict: dict) -> None
    render_birthdays_table(rows: list[dict]) -> None
    render_success(message: str) -> None
    render_error(message: str) -> None
    render_not_found(entity: str, query: str) -> None
    render_empty(entity: str) -> None

Constants:
    CONSOLE : Console  — shared console instance (highlight=False for clean output)

Dependencies (internal):
    none — this module is the dependency leaf; nothing else in the app imports rich

External libs:
    rich>=13.0.0

Assignee:
"""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

from smart_assistant import __version__

CONSOLE = Console(highlight=False)

# ── ASCII logo ─────────────────────────────────────────────────────────────────

_LOGO = r"""
  ____                       _      _            _     _              _
 / ___| _ __ ___   __ _ _ __| |_   / \   ___ ___(_)___| |_ __ _ _ __ | |_
 \___ \| '_ ` _ \ / _` | '__| __| / _ \ / __/ __| / __| __/ _` | '_ \| __|
  ___) | | | | | | (_| | |  | |_ / ___ \\__ \__ \ \__ \ || (_| | | | | |_
 |____/|_| |_| |_|\__,_|_|   \__/_/   \_\___/___/_|___/\__\__,_|_| |_|\__|
"""


# ── Welcome ────────────────────────────────────────────────────────────────────


def render_welcome() -> None:
    """Render the startup banner with ASCII logo and version."""
    CONSOLE.print(
        Panel(
            Text(_LOGO, style="bold cyan", justify="center")
            + Text(
                f"\n  Personal Productivity CLI  •  v{__version__}\n"
                "  Type  [bold]help[/bold]  to see all commands\n",
                justify="center",
            ),
            border_style="cyan",
            padding=(0, 2),
        )
    )


# ── Help table ─────────────────────────────────────────────────────────────────


def render_help(commands: list[dict]) -> None:
    """
    Render the command reference table.

    Parameters
    ----------
    commands : list[dict]
        Each dict must have keys: command, description, example
    """
    table = Table(
        title="[bold cyan]Available Commands[/bold cyan]",
        box=box.ROUNDED,
        border_style="cyan",
        show_header=True,
        header_style="bold magenta",
        padding=(0, 1),
    )
    table.add_column("Command", style="bold green", no_wrap=True)
    table.add_column("Description")
    table.add_column("Example", style="dim")

    for cmd in commands:
        table.add_row(cmd["command"], cmd["description"], cmd["example"])

    CONSOLE.print(table)


# ── Contacts ───────────────────────────────────────────────────────────────────


def render_contacts_table(records: list[dict]) -> None:
    """
    Render a table of contacts.

    Parameters
    ----------
    records : list[dict]
        Each dict from Record.to_dict():
        name, phones, email, birthday, days_until_birthday, address
    """
    table = Table(
        title=f"[bold cyan]Address Book[/bold cyan]  ({len(records)} contact{'s' if len(records) != 1 else ''})",
        box=box.ROUNDED,
        border_style="blue",
        show_header=True,
        header_style="bold magenta",
        padding=(0, 1),
    )
    table.add_column("Name", style="bold cyan", no_wrap=True)
    table.add_column("Phones")
    table.add_column("E-mail")
    table.add_column("Birthday", no_wrap=True)
    table.add_column("Address")

    for rec in records:
        # Colour birthday depending on proximity
        days_str = rec.get("days_until_birthday", "—")
        bday_display = rec["birthday"]
        if bday_display != "—" and days_str != "—":
            try:
                days = int(days_str)
                if days <= 3:
                    bday_display = f"[bold green]{bday_display} ({days}d)[/bold green]"
                elif days <= 7:
                    bday_display = f"[yellow]{bday_display} ({days}d)[/yellow]"
                else:
                    bday_display = f"{bday_display} ({days}d)"
            except ValueError:
                pass

        table.add_row(
            rec["name"],
            rec["phones"],
            rec["email"],
            bday_display,
            rec["address"],
        )

    CONSOLE.print(table)


def render_contact_detail(record_dict: dict) -> None:
    """Render a single contact in a detail panel."""
    lines = []
    lines.append(f"[bold cyan]Name:[/bold cyan]     {record_dict['name']}")
    lines.append(f"[bold]Phones:[/bold]   {record_dict['phones']}")
    lines.append(f"[bold]E-mail:[/bold]   {record_dict['email']}")
    lines.append(f"[bold]Birthday:[/bold] {record_dict['birthday']}")
    lines.append(f"[bold]Address:[/bold]  {record_dict['address']}")

    CONSOLE.print(
        Panel(
            "\n".join(lines),
            title=f"[bold cyan]Contact: {record_dict['name']}[/bold cyan]",
            border_style="cyan",
            padding=(1, 2),
        )
    )


# ── Notes ──────────────────────────────────────────────────────────────────────


def render_notes_table(notes: list[dict]) -> None:
    """
    Render a table of notes.

    Parameters
    ----------
    notes : list[dict]
        Each dict from Note.to_dict():
        title, body_preview, tags, created_at, updated_at
    """
    table = Table(
        title=f"[bold cyan]Notes[/bold cyan]  ({len(notes)} note{'s' if len(notes) != 1 else ''})",
        box=box.ROUNDED,
        border_style="blue",
        show_header=True,
        header_style="bold magenta",
        padding=(0, 1),
    )
    table.add_column("Title", style="bold cyan", no_wrap=True)
    table.add_column("Tags", style="magenta")
    table.add_column("Created", style="dim", no_wrap=True)
    table.add_column("Preview")

    for note in notes:
        table.add_row(
            note["title"],
            note["tags"],
            note["created_at"],
            note["body_preview"],
        )

    CONSOLE.print(table)


def render_note_detail(note_dict: dict) -> None:
    """Render a single note in a detail panel."""
    content = (
        f"[bold]Tags:[/bold]    {note_dict['tags']}\n"
        f"[bold]Created:[/bold] {note_dict['created_at']}\n"
        f"[bold]Updated:[/bold] {note_dict['updated_at']}\n\n"
        f"{note_dict['body']}"
    )
    CONSOLE.print(
        Panel(
            content,
            title=f"[bold cyan]{note_dict['title']}[/bold cyan]",
            border_style="cyan",
            padding=(1, 2),
        )
    )


# ── Birthdays ──────────────────────────────────────────────────────────────────


def render_birthdays_table(rows: list[dict]) -> None:
    """
    Render upcoming birthdays.

    Parameters
    ----------
    rows : list[dict]
        Each dict: name, birthday, days_remaining (int as str)
    """
    table = Table(
        title="[bold cyan]Upcoming Birthdays[/bold cyan]",
        box=box.ROUNDED,
        border_style="yellow",
        show_header=True,
        header_style="bold magenta",
        padding=(0, 1),
    )
    table.add_column("Name", style="bold cyan", no_wrap=True)
    table.add_column("Birthday", no_wrap=True)
    table.add_column("Days Until", justify="right")

    for row in rows:
        days = int(row["days_remaining"])
        if days <= 3:
            style = "bold green"
        elif days <= 7:
            style = "yellow"
        else:
            style = ""
        table.add_row(
            row["name"],
            row["birthday"],
            f"[{style}]{days}[/{style}]" if style else str(days),
        )

    CONSOLE.print(table)


# ── Status messages ────────────────────────────────────────────────────────────


def render_success(message: str) -> None:
    """Green success panel."""
    CONSOLE.print(
        Panel(
            f"[bold green]✓[/bold green]  {message}",
            border_style="green",
            padding=(0, 2),
        )
    )


def render_error(message: str) -> None:
    """Red error panel."""
    CONSOLE.print(
        Panel(
            f"[bold red]✗[/bold red]  {message}",
            border_style="red",
            padding=(0, 2),
        )
    )


def render_not_found(entity: str, query: str) -> None:
    """Yellow warning — entity not found by query."""
    CONSOLE.print(
        Panel(
            f"[yellow]⚠[/yellow]  No {entity} found for [bold]'{query}'[/bold].",
            border_style="yellow",
            padding=(0, 2),
        )
    )


def render_empty(entity: str) -> None:
    """Dim notice — no items in the collection yet."""
    # entity examples: "contacts", "notes" → strip trailing 's' for the command
    cmd_noun = entity.rstrip("s")  # "contacts" → "contact", "notes" → "note"
    CONSOLE.print(
        f"[dim]  No {entity} yet. Use [bold]add-{cmd_noun}[/bold] to create one.[/dim]"
    )
