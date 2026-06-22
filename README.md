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
- Composable — dialogs can call each other internally
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
        # ... rest of your app
```

After this, you can call any dialog from event handlers, actions, or bindings without additional setup.

## API Overview

### File Dialogs

- **`OpenFile.show(...)`** — Supports `multiselect`, `filters`, `must_exist`
- **`OpenFolder.show(...)`** — Folder-only selection
- **`SaveFile.show(...)`** — Includes overwrite confirmation by default
- All dialogs accept `initial_directory`, `title`, `show_hidden`, and a `callback`

### MessageBox

```python
messagebox.show(
    message: str,
    title: str = "Message",
    buttons: list[str] | None = None,
    type: str = messagebox.type.INFO,
    callback: Callable[[str | None], None] | None = None,
)
```

- Available button presets: `OK`, `OK_CANCEL`, `YES_NO`, `YES_NO_CANCEL`, `RETRY_CANCEL`, etc.  
- Available types: `INFO`, `WARNING`, `ERROR`, `SUCCESS`.

## Package Structure

```
nannokit/dialogs/
├── core/              # Shared manager, base screen, and utilities
├── messagebox/        # Message dialog implementation
├── filedialogs/       # OpenFile, OpenFolder, SaveFile + shared tree
└── styles/            # TCSS stylesheets
```

## Development

```bash
# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## License

BSD 3-Clause License — see [LICENSE](LICENSE) for details.

---

Part of the [SuperNanno](https://github.com/hbisneto/SuperNanno) ecosystem.  
Built to make powerful Textual applications even easier to develop.