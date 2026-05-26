"""
UI package initializer.

Responsibility:
    Re-exports the public rendering API from renderer.py so callers
    can write ``from smart_assistant.ui import render_success`` etc.

Assignee:
"""

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

__all__ = [
    "render_welcome",
    "render_help",
    "render_contacts_table",
    "render_contact_detail",
    "render_notes_table",
    "render_note_detail",
    "render_birthdays_table",
    "render_success",
    "render_error",
    "render_not_found",
    "render_empty",
]
