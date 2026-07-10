"""
nannokit.dialogs.core.priority
==================================

Priority tiers shared by every dialog in the package.

``DialogQueue`` (see :mod:`nannokit.dialogs.core.queue`) uses a
dialog's ``priority`` to decide, whenever more than one dialog is
requested around the same time, which one wins the screen:

- A dialog requested with a **higher** priority than whatever is
  currently on screen is stacked on top of it immediately. Textual's
  own screen stack keeps the interrupted dialog fully intact
  underneath - nothing is cancelled, nothing loses its state - it
  simply waits its turn again once the higher-priority dialog is
  dismissed.
- A dialog requested with an **equal or lower** priority than what's
  currently showing is queued instead, and only presented once the
  current dialog resolves.

This is what guarantees the two behaviours the package promises:
a critical confirmation (e.g. an overwrite prompt) is *never* silently
buried behind - or replaced by - a lower priority dialog, and a
FileDialog that's already open is never yanked away by an
informational messagebox that happens to fire at the same moment.
"""

from __future__ import annotations


class DialogPriority:
    """Priority tiers for dialogs shown via :class:`DialogScreenBase`.

    Plain integers, not an enum, so callers can supply their own
    fine-grained values (e.g. ``DialogPriority.HIGH + 1``) if a future
    dialog needs to sit strictly above/below one of these tiers without
    a package release.
    """

    #: Informational messageboxes (INFO, SUCCESS) - nice to show, but
    #: never worth interrupting something the user is actively doing.
    LOW = 30

    #: File dialogs (OpenFile, OpenFolder, SaveFile, OpenPath) - the
    #: "normal" priority tier most user-driven interactions live at.
    MEDIUM = 50

    #: Confirmation/critical messageboxes (WARNING, ERROR) - must
    #: always get a chance to be answered before anything else
    #: (including an already-open file dialog) continues.
    HIGH = 100
