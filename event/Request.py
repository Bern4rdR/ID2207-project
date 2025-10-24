"""
event/Request.py

A lightweight Request implementation for the `event` package.

This module provides:
- EventRequest: a minimal class representing an event request (constructor,
  attributes and methods used by the tests).
- get(request_id, requests_list): helper to find a request by .id in a list.

Additionally, when this module is loaded (as `event.Request`) it registers
itself as the top-level module name "Request" in `sys.modules` so that tests
which do `import Request` can succeed during collection (pytest may import the
package module before performing top-level imports).
"""

from __future__ import annotations

import sys
import uuid
import datetime
from typing import Any, List, Optional

# Prefer relative import of the package's Status. Fall back to a lightweight
# local stand-in if Status cannot be imported (keeps imports safe in isolation).
try:
    from .Status import Status  # type: ignore
except Exception:
    try:
        import Status  # type: ignore
    except Exception:  # pragma: no cover - fallback only used in unusual environments

        class _LocalStatus:
            Ongoing = "Ongoing"
            Approved = "Approved"
            Rejected = "Rejected"
            Closed = "Closed"

        Status = _LocalStatus  # type: ignore


def get(request_id: Any, requests_list: List[Any]) -> Optional[Any]:
    """
    Return the request from `requests_list` whose `.id` equals `request_id`,
    or None if not found.
    """
    for req in requests_list:
        if getattr(req, "id", None) == request_id:
            return req
    return None


class EventRequest:
    """
    Minimal event request used by tests.

    Constructor:
        EventRequest(type, budget, dates, preferences)

    - type: str
    - budget: int | float (>= 0)
    - dates: list[datetime.datetime] (future dates)
    - preferences: list[str] (optional)
    """

    def __init__(
        self,
        type: str,
        budget: float,
        dates: List[datetime.datetime],
        preferences: Optional[List[str]] = None,
    ) -> None:
        # Unique identifier
        self.id: str = uuid.uuid4().hex

        # Core fields
        self.type: str = type
        self.budget: float = budget
        self.dates: List[datetime.datetime] = dates if dates is not None else []
        self.preferences: List[str] = preferences if preferences is not None else []

        # Feedback list
        self.feedback: List[str] = []

        # Validate dates
        if not isinstance(self.dates, list):
            raise TypeError("dates must be a list of datetime objects")
        now = datetime.datetime.now()
        for d in self.dates:
            if not isinstance(d, datetime.datetime):
                raise TypeError("each date must be a datetime.datetime instance")
            if d < now:
                raise ValueError("dates cannot be in the past")

        # Validate budget
        try:
            if float(self.budget) < 0:
                raise ValueError("budget must be non-negative")
        except Exception:
            raise ValueError("budget must be a number >= 0")

        # Initial status (tests expect Status.Ongoing)
        self.status = getattr(Status, "Ongoing", Status.Ongoing)

    def addFeedback(self, message: str) -> None:
        """Append a feedback message."""
        if message is None:
            return
        self.feedback.append(message)

    def approve(self) -> None:
        """Mark request as approved."""
        self.status = getattr(Status, "Approved", Status.Approved)

    def reject(self, reason: Optional[str] = None) -> None:
        """
        Reject the request. If `reason` provided, it will be recorded as feedback.
        """
        if reason:
            self.addFeedback(reason)
        self.status = getattr(Status, "Rejected", Status.Rejected)

    def close(self) -> None:
        """Close/finalize the request (admin action)."""
        self.status = getattr(Status, "Closed", Status.Closed)

    def __str__(self) -> str:
        prefs = ", ".join(self.preferences) if self.preferences else "None"
        dates_str = ", ".join(d.isoformat() for d in self.dates)
        return (
            f"EventRequest(id={self.id}, type={self.type}, budget={self.budget}, "
            f"dates=[{dates_str}], preferences=[{prefs}], status={self.status}, "
            f"feedback_count={len(self.feedback)})"
        )


# Register this module under the top-level name "Request" if it's not already present.
# This allows simple `import Request` to succeed during pytest collection when this
# module has been imported via the package (event.Request).
try:
    if "Request" not in sys.modules:
        sys.modules["Request"] = sys.modules[__name__]
except Exception:
    # Non-fatal; registration is a convenience to aid tests that expect top-level import.
    pass


__all__ = ["EventRequest", "get"]
