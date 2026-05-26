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