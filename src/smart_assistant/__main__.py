"""
Entry point module for ``python -m smart_assistant`` invocation.

Responsibility:
    Provides the ``main()`` function registered as the ``assistant``
    console script in pyproject.toml.  Intentionally thin — imports
    and delegates to cli.run() so the real logic remains testable.

Functions:
    main() -> None  — entry point called by the installed script

Dependencies (internal):
    smart_assistant.cli

External libs:
    none

Assignee:
"""

from smart_assistant.cli import run


def main() -> None:
    """Entry point for the ``assistant`` CLI command."""
    run()


if __name__ == "__main__":
    main()
