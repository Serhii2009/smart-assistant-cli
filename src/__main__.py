"""
Module: __main__.py
Responsibility: Thin entry point wiring the `notii` console script and
                `python -m src` invocation to cli.run().

Functions:
    main() -> None  — called by the installed `notii` script

Trello tasks:
    (none — infrastructure only)

Dependencies (internal):
    notii.cli

External libs:
    none

Assignee: Serhii Kravchenko
"""

from .cli import run


def main() -> None:
    """Entry point for the ``notii`` command."""
    run()


if __name__ == "__main__":
    main()
