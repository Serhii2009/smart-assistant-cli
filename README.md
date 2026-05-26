# Notii

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

A command-line tool for managing contacts and notes.
Stores an address book with full contact details — name, phones, e-mail, birthday,
and address — and a notebook of text notes that can be searched and organised with tags.
All data is saved automatically between sessions.

---

## Features

**Contacts**

- Add a contact with full name, phone number, e-mail, birthday, and address
- Search contacts across all fields by a text query
- Edit any field of an existing contact
- Delete a contact
- View contacts whose birthday falls within a given number of days

**Notes**

- Create notes with a title and a free-text body
- Search notes by their text content
- Edit a note's title or body
- Delete notes
- Attach keyword tags to notes
- Search notes by tag and sort alphabetically by tag

**General**

- Phone numbers and e-mail addresses are validated on entry; invalid values are
  rejected with a clear message and the prompt is repeated
- Data is persisted automatically to the `data/` folder at the project root
- Tab-autocomplete and command history via prompt_toolkit
- All commands use a `/` prefix; any input without a leading `/` is rejected with
  a friendly error

---

## Requirements

Python 3.10 or later.

---

## Installation

### From PyPI

```
pip install notii
```

### From source

```
git clone https://github.com/Serhii2009/smart-assistant-cli.git
cd smart-assistant-cli
pip install -r requirements.txt
pip install -e .
```

---

## Running

```
notii
```

The application starts, shows a short header, and waits for commands.
Type `/` to see the full command list with autocomplete.

---

## Commands

All commands use a `/` prefix. After entering a command, the application guides
you through each required field on a separate prompt line. No arguments are ever
typed on the same line as the command itself.

| Command           | Description                                   |
| ----------------- | --------------------------------------------- |
| `/add-contact`    | Add a new contact (interactive field prompts) |
| `/show-contacts`  | List all contacts                             |
| `/find-contact`   | Search contacts by any field                  |
| `/edit-contact`   | Edit a field of an existing contact           |
| `/delete-contact` | Delete a contact                              |
| `/birthdays`      | Contacts with a birthday in the next N days   |
| `/add-note`       | Create a new note (interactive)               |
| `/show-notes`     | List all notes                                |
| `/find-note`      | Search notes by title or body                 |
| `/edit-note`      | Edit a note's title or body                   |
| `/delete-note`    | Delete a note                                 |
| `/add-tag`        | Attach a tag to a note                        |
| `/remove-tag`     | Remove a tag from a note                      |
| `/find-by-tag`    | Find notes by tag                             |
| `/sort-by-tags`   | List notes sorted alphabetically by tag       |
| `/help`           | Show the command list                         |
| `/exit`           | Save data and exit                            |

---

## Project structure

```
smart-assistant-cli/
├── data/
│   ├── contacts.pkl     address book (created automatically on first run)
│   └── notes.pkl        notes (created automatically on first run)
├── src/
│   ├── __init__.py      package version
│   ├── __main__.py      entry point
│   ├── cli.py           REPL loop and command dispatch
│   ├── fields.py        Field base class and all field types
│   ├── contact.py       Record and AddressBook classes
│   ├── note.py          Note and NoteBook classes
│   ├── repository.py    pickle persistence (the only file touching disk)
│   ├── handlers.py      pure handler functions (no I/O)
│   └── renderer.py      all terminal output (the only file using rich)
├── requirements.txt
├── pyproject.toml
└── README.md
```

**Layered architecture:**

```
cli.py  →  handlers.py  →  contact.py / note.py / fields.py
  ↓                                ↓
renderer.py             repository.py
```

- `handlers.py` contains only pure functions: no printing, no input
- `renderer.py` is the only file that imports `rich`
- `repository.py` is the only file that reads or writes files

---

## Contributing

1. Clone the repository:

   ```
   git clone https://github.com/Serhii2009/smart-assistant-cli.git
   cd smart-assistant-cli
   ```

2. Create a branch for your work:

   ```
   git checkout -b feature/your-feature-name
   ```

3. Install dependencies:

   ```
   pip install -r requirements.txt
   pip install -e .
   ```

4. Make your changes, commit them, and open a pull request against `main`.

Branch naming conventions: `feature/`, `fix/`, `docs/`.

---

## License

MIT — see [LICENSE](LICENSE).
