"""
event/Status.py

Status enumeration used by the event package.

This module exposes both the `Status` Enum and module-level names
`Ongoing`, `Approved`, `Rejected`, `Closed` so callers can do either:

    import event.Status as S
    # or
    from event import Status

and also support code that expects module-level attributes:

    import Status
    assert request.status == Status.Ongoing

To avoid accidental mismatch between different Status definitions, this
module defines the Enum and then re-exports its members at module level.
"""

from enum import Enum


class Status(Enum):
    """Enumeration of possible request statuses used across the project/tests."""

    Ongoing = "Ongoing"
    Approved = "Approved"
    Rejected = "Rejected"
    Closed = "Closed"

    def __str__(self) -> str:
        return self.value


# Module-level re-exports to match tests that import `Status` and reference names
Ongoing = Status.Ongoing
Approved = Status.Approved
Rejected = Status.Rejected
Closed = Status.Closed

__all__ = ["Status", "Ongoing", "Approved", "Rejected", "Closed"]
