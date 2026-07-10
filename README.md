# NannoKit.Dialogs

**Official dialogs extension for SuperNanno** — a modern, lightweight set of file and message dialogs built for [Textual](https://textual.textualize.io) applications.

NannoKit.Dialogs provides clean, high-level APIs for common user interactions:

- `OpenFile` — select one or multiple files
- `OpenFolder` — browse and select a folder
- `SaveFile` — choose a location and filename with optional overwrite confirmation
- `messagebox` — flexible notification and confirmation dialogs

> Designed to integrate seamlessly into SuperNanno and work standalone in any Textual app.

## Features

- Automatic resolution of the running Textual `App` (no manual passing required in most cases)
- Full keyboard navigation and mouse support
- Filterable directory tree (hidden files, glob patterns)
- Editable location field for quick path navigation
- Multiselect support in OpenFile
- Validation (`must_exist`) with inline feedback
- Consistent styling and Escape-to-cancel behavior
- **Priority-aware isolation** — `messagebox` and `filedialogs` never interrupt or replace each other; see [Isolation & Priority](#isolation--priority) below
- Composable — dialogs can call each other internally (e.g. `SaveFile`'s overwrite prompt)
- Thorough test coverage with Textual's `Pilot` harness
- Installable as a standalone package or as part of the SuperNanno ecosystem

## Installation

```bash
pip install nannokit.dialogs
```

To also install SuperNanno core (when available):

```bash
pip install "nannokit.dialogs[supernanno]"
```

## Quick Start

```python
from nannokit.dialogs import OpenFile, OpenFolder, SaveFile, messagebox
from pathlib import Path

# Open file(s)
OpenFile.show(
    initial_directory=".",
    filters=["*.py", "*.toml", "*.md"],
    callback=lambda path: print("Selected:", path),
)

# Open folder
OpenFolder.show(
    initial_directory=".",
    callback=lambda folder: print("Folder:", folder),
)

# Save file
SaveFile.show(
    default_filename="untitled.txt",
    callback=lambda path: print("Save to:", path),
)

# Message dialog
messagebox.show(
    "Save changes before closing?",
    title="SuperNanno",
    buttons=messagebox.buttons.YES_NO_CANCEL,
    type=messagebox.type.WARNING,
    callback=lambda choice: print("Choice:", choice),
)
```

## Integration with SuperNanno

In your main `App` class, attach the dialog manager once (recommended):

```python
from textual.app import App
from nannokit.dialogs.core import DialogManager

class SuperNannoApp(App):
    def on_mount(self) -> None:
        DialogManager.attach(self)
```

After this, you can call any dialog from event handlers, actions, or bindings without additional setup.

## Isolation & Priority

`messagebox` and `filedialogs` are completely isolated from one
another: neither can silently cancel, replace, or bury the other.
Every dialog carries a **priority** tier, and a shared `DialogQueue`
decides what happens when a new dialog is requested while another is
already on screen:

| Situation | Behaviour |
|---|---|
| Nothing currently showing | The dialog is shown immediately (same as always). |
| A **lower**-priority dialog is showing | The new one is stacked **on top** right away — Textual's screen stack keeps the interrupted dialog's state fully intact underneath, so it just picks up where it left off once the new one is dismissed. |
| An **equal or higher**-priority dialog is showing | The new one is **queued** and shown automatically as soon as the current one is dismissed — it never interrupts, cancels, or is dropped. |

Default priority tiers (`nannokit.dialogs.core.DialogPriority`):

```python
class DialogPriority:
    LOW = 30      # messagebox.type.INFO / SUCCESS
    MEDIUM = 50   # OpenFile, OpenFolder, SaveFile, OpenPath
    HIGH = 100    # messagebox.type.WARNING / ERROR
```

This is why `SaveFile`'s built-in overwrite confirmation (a `WARNING`
messagebox, `HIGH`) always appears on top of the `SaveFile` dialog
that spawned it (`MEDIUM`) and must be answered before `SaveFile` can
proceed — and, symmetrically, why an informational `messagebox.show()`
fired from a background task never yanks focus away from a file
dialog the user is actively using.

You normally don't need to think about any of this — it's automatic.
If you do need to override a dialog's default tier for a specific
call, every `.show(...)` accepts an explicit `priority=`:

```python
from nannokit.dialogs import messagebox
from nannokit.dialogs.core import DialogPriority

# An INFO box that must still interrupt an open file dialog:
messagebox.show(
    "Critical background task failed.",
    type=messagebox.type.INFO,
    priority=DialogPriority.HIGH,
    callback=on_result,
)

# ...or the equivalent, priority-first convenience form:
messagebox.show_with_priority(
    DialogPriority.HIGH,
    "Critical background task failed.",
    type=messagebox.type.INFO,
    callback=on_result,
)
```

`OpenFile`, `OpenFolder`, `SaveFile`, and `OpenPath` all accept the
same `priority=` kwarg and expose the same `show_with_priority(...)`
helper.

## API Overview

### File Dialogs

- **`OpenFile.show(...)`** — Supports `multiselect`, `filters`, `must_exist`, `priority`
- **`OpenFolder.show(...)`** — Folder-only selection
- **`SaveFile.show(...)`** — Includes overwrite confirmation by default
- All dialogs accept `initial_directory`, `title`, `show_hidden`, `priority`, and a `callback`

### MessageBox

```python
messagebox.show(
    message: str,
    title: str = "Message",
    buttons: list[str] | None = None,
    type: str = messagebox.type.INFO,
    callback: Callable[[str | None], None] | None = None,
    priority: int | None = None,
)
```

- Available button presets: `OK`, `OK_CANCEL`, `YES_NO`, `YES_NO_CANCEL`, `RETRY_CANCEL`, etc.
- Available types: `INFO`, `WARNING`, `ERROR`, `SUCCESS`. `WARNING`/`ERROR` default to `DialogPriority.HIGH`; `INFO`/`SUCCESS` default to `DialogPriority.LOW`.

## Package Structure

```
nannokit/dialogs/
├── core/              # Shared manager, priority queue, base screen, and utilities
│   ├── manager.py      # DialogManager - resolves the running App
│   ├── queue.py        # DialogQueue - priority-aware presentation scheduler
│   ├── priority.py     # DialogPriority - LOW / MEDIUM / HIGH tiers
│   └── base.py         # DialogScreenBase - shared ModalScreen plumbing
├── messagebox/         # Message dialog implementation
├── filedialogs/        # OpenFile, OpenFolder, SaveFile + shared tree
└── styles/             # TCSS stylesheets
```

## Development

```bash
# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## Roadmap / Extending

The priority/queue architecture was designed so that adding a new
dialog (e.g. a `ColorPicker`) only requires:

1. Subclassing `DialogScreenBase` and setting `self.priority` in
   `__init__` (defaults to `DialogPriority.MEDIUM` if you don't).
2. Calling `cls._present(instance)` from your dialog's own `show()`
   classmethod — isolation and queueing are handled for you.

Ideas for follow-up work:

- A `DialogPriority.CRITICAL` tier (above `HIGH`) for things like an
  unhandled-exception dialog that must pre-empt even a `WARNING`
  messagebox.
- Let `DialogQueue` coalesce duplicate/near-identical pending
  requests (e.g. two identical INFO toasts queued back to back) into
  one.
- A shared `DialogTheme` palette (the module already exists as a
  reserved extension point) so a future `ColorPicker` and the existing
  dialogs pull colors from one place instead of independent `.tcss`
  hex values.
- Optional async/await-style `await OpenFile.ask(...)` sugar on top of
  the existing callback API, for call sites that would rather `await`
  a result than provide a callback.

## License

BSD 3-Clause License — see [LICENSE](LICENSE) for details.

---

Part of the [SuperNanno](https://github.com/hbisneto/SuperNanno) ecosystem.
Built to make powerful Textual applications even easier to develop.
