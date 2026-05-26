# Smart Assistant CLI

[![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![PyPI](https://img.shields.io/pypi/v/smart-assistant-cli?color=green)](https://pypi.org/project/smart-assistant-cli/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Code style: PEP 8](https://img.shields.io/badge/code%20style-PEP%208-orange)](https://peps.python.org/pep-0008/)

> **A personal productivity tool for managing contacts and notes — entirely in your terminal.**

Smart Assistant is a polished command-line application that keeps your address book and notes organised, validates every input, and persists everything safely between sessions. It feels like a real tool, because it is one.

---

## ✨ Features

| Area | What it does |
|------|-------------|
| 📇 **Contacts** | Store name, address, multiple phones, e-mail, and birthday |
| 🎂 **Birthdays** | List contacts whose birthday falls within the next N days |
| ✅ **Validation** | Phones and e-mails are validated on entry; bad input is rejected gracefully, never crashes |
| 🔍 **Search** | Full-text search across all contact fields |
| ✏️ **Edit & Delete** | Update any field or remove a contact entirely |
| 📝 **Notes** | Create titled notes with a free-text body |
| 🔍 **Note Search** | Full-text search across note titles and bodies |
| ✏️ **Note Edit** | Change the title, body, or both of any note |
| 🏷️ **Tags** | Attach keyword tags to notes; search and sort by tag |
| 💾 **Persistence** | All data saved to `~/.smart_assistant/` — survives restarts |
| 🎨 **Rich UI** | Tables, coloured panels, and styled text via [rich](https://github.com/Textualize/rich) |
| ⌨️ **Autocomplete** | Tab-completion and command history via [prompt_toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit) |

---

## 📦 Installation

### From PyPI *(recommended)*

```bash
pip install smart-assistant-cli
```

### From source

```bash
git clone https://github.com/Serhii2009/smart-assistant-cli.git
cd smart-assistant-cli
pip install -e .
```

> **Requires Python 3.10 or later.**

---

## 🚀 Quick Start

```bash
assistant
```

That's it. The application loads your data, prints the help table once, and waits for commands.

```
  ____                       _      _            _     _              _
 / ___| _ __ ___   __ _ _ __| |_   / \   ___ ___(_)___| |_ __ _ _ __ | |_
 \___ \| '_ ` _ \ / _` | '__| __| / _ \ / __/ __| / __| __/ _` | '_ \| __|
  ___) | | | | | | (_| | |  | |_ / ___ \__ \__ \ \__ \ || (_| | | | | |_
 |____/|_| |_| |_|\__,_|_|   \__/_/   \_\___/___/_|___/\__\__,_|_| |_|\__|

            Personal Productivity CLI  •  v1.0.0
            Type  help  to see all commands

[assistant] ❯ _
```

---

## 🛠️ Commands Reference

### Contacts

| Command | Description | Example |
|---------|-------------|---------|
| `add-contact` | Add a new contact (interactive prompts) | `add-contact` |
| `show-contacts` | List all contacts in a table | `show-contacts` |
| `find-contact <query>` | Search contacts by any field | `find-contact Alice` |
| `edit-contact <name>` | Edit a field of an existing contact | `edit-contact Alice` |
| `delete-contact <name>` | Delete a contact permanently | `delete-contact Alice` |
| `birthdays <days>` | Contacts with birthday in the next N days | `birthdays 30` |

**Editable fields:** `name` · `add-phone` · `remove-phone` · `phone` (replace) · `email` · `birthday` · `address`

### Notes

| Command | Description | Example |
|---------|-------------|---------|
| `add-note` | Create a new note (interactive) | `add-note` |
| `show-notes` | List all notes | `show-notes` |
| `find-note <query>` | Full-text search in notes | `find-note meeting` |
| `edit-note <title>` | Edit a note's title or body | `edit-note "Team sync"` |
| `delete-note <title>` | Delete a note | `delete-note "Team sync"` |

### Tags *(bonus)*

| Command | Description | Example |
|---------|-------------|---------|
| `add-tag <title> <tag>` | Attach a tag to a note | `add-tag "Team sync" work` |
| `remove-tag <title> <tag>` | Remove a tag from a note | `remove-tag "Team sync" work` |
| `find-by-tag <tag>` | Find all notes with a tag | `find-by-tag work` |
| `sort-by-tags` | List all notes sorted by tag | `sort-by-tags` |

### System

| Command | Description |
|---------|-------------|
| `help` | Show the command table |
| `exit` / `quit` / `close` | Save data and exit |

---

## 📋 Usage Examples

### Add a contact

```
[assistant] ❯ add-contact

  ── New Contact ──
  Full name: Alice Johnson
  Phone(s) [comma-separated, or blank]: +380991234567, +380501112233
  E-mail [or blank]: alice@example.com
  Birthday DD.MM.YYYY [or blank]: 15.03.1990
  Address [or blank]: 123 Main St, Kyiv

✓  Contact 'Alice Johnson' added successfully.
```

### View upcoming birthdays

```
[assistant] ❯ birthdays 14

╭─ Upcoming Birthdays ─────────────────────────────╮
│ Name          │ Birthday   │ Days Until           │
│ Alice Johnson │ 15.03.1990 │ 3   ← green if ≤ 3d │
│ Bob Smith     │ 20.03.1985 │ 8                    │
╰──────────────────────────────────────────────────╯
```

### Work with notes and tags

```
[assistant] ❯ add-note
  Title: Sprint planning
  Body: Discuss Q2 roadmap and assign tasks.

[assistant] ❯ add-tag Sprint planning work
✓  Tag '#work' added to 'Sprint planning'.

[assistant] ❯ find-by-tag work
  # Sprint planning  #work  2026-05-26  Discuss Q2 roadmap…
```

---

## 💾 Data Storage

All data is saved automatically to `~/.smart_assistant/`:

```
~/.smart_assistant/
├── contacts.pkl   # address book
├── notes.pkl      # notes and tags
└── history.txt    # command history
```

Writes are **atomic** — a crash mid-save cannot corrupt your data.

---

## 🏗️ Project Structure

```
smart-assistant-cli/
├── src/
│   └── smart_assistant/
│       ├── __init__.py          # package version
│       ├── __main__.py          # entry point (python -m smart_assistant)
│       ├── cli.py               # REPL loop + command dispatch
│       ├── models/
│       │   ├── fields.py        # Field hierarchy (Name, Phone, Email, Birthday, Address, Tag)
│       │   ├── contact.py       # Record + AddressBook
│       │   └── note.py          # Note + NoteBook
│       ├── storage/
│       │   └── repository.py    # ALL filesystem I/O (atomic pickle read/write)
│       ├── handlers/
│       │   ├── contacts.py      # Pure contact handler functions
│       │   └── notes.py         # Pure note handler functions
│       └── ui/
│           └── renderer.py      # ALL rich output (the only file that imports rich)
├── pyproject.toml
├── README.md
└── .gitignore
```

### Architecture

```
CLI Layer       cli.py           — REPL, I/O, command routing
     ↓
Handler Layer   handlers/        — Pure functions; no I/O; return (status, data)
     ↓
Model Layer     models/          — OOP domain objects; all validation here
     ↓
Storage Layer   storage/         — Isolated pickle persistence; atomic writes
     ↑
UI Layer        ui/renderer.py   — All rich output; accepts plain dicts only
```

**OOP principles applied:**
- **Encapsulation** — each class owns its data and exposes a minimal public API
- **Abstraction** — `Field`, `AddressBook`, `NoteBook` hide internal details
- **Inheritance** — `Name`, `Phone`, `Email`, `Birthday`, `Address`, `Tag` all extend `Field`
- **Polymorphism** — each `Field` subclass overrides `validate()` and `__str__()`

---

## 🧑‍💻 Development

### Setup

```bash
git clone https://github.com/Serhii2009/smart-assistant-cli.git
cd smart-assistant-cli

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -e .
```

### Run from source

```bash
assistant
# or
python -m smart_assistant
```

### Build a distribution package

```bash
pip install build
python -m build
# produces dist/smart_assistant_cli-1.0.0-py3-none-any.whl
```

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Follow PEP 8 and the existing code style
4. Keep handler functions pure (no I/O)
5. Keep all `rich` calls inside `ui/renderer.py`
6. Open a Pull Request with a clear description

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<p align="center">Built with ❤️ using <a href="https://github.com/Textualize/rich">rich</a> and <a href="https://github.com/prompt-toolkit/python-prompt-toolkit">prompt_toolkit</a></p>
