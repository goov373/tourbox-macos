# CLAUDE.md - AI Context for TourBox macOS Driver

## Project Overview

This is a custom macOS driver for TourBox Lite that replaces the official TourBox Console. It uses JSON-based profiles for button mappings and will eventually include AI-powered profile generation.

## Tech Stack

- **Language:** Python 3.9+
- **Serial Communication:** pyserial
- **Keyboard Simulation:** pynput
- **Package Manager:** pip with pyproject.toml
- **Linting:** ruff
- **Testing:** pytest

## Project Structure

```
tourbox-macos/
├── src/tourbox_macos/
│   ├── __init__.py      # Package init, exports TourBoxDriver
│   └── driver.py        # Main driver implementation
├── profiles/
│   ├── default.json     # Default universal profile
│   └── developer.json   # Developer workflow profile
├── docs/
│   ├── PROTOCOL.md      # Serial protocol documentation
│   ├── ARCHITECTURE.md  # System architecture
│   └── PROFILES.md      # Profile format reference
├── tests/               # Test files (pytest)
├── pyproject.toml       # Project configuration
└── README.md
```

## Key Files

- `src/tourbox_macos/driver.py` - Main driver with TourBoxDriver class
- `profiles/*.json` - Button mapping profiles
- `~/Library/LaunchAgents/com.tourbox.driver.plist` - Auto-start config

## Common Tasks

### Run the driver manually
```bash
python3 src/tourbox_macos/driver.py -f profiles/developer.json
```

### Check driver logs
```bash
tail -f /tmp/tourbox-driver.log
```

### Restart the driver
```bash
launchctl stop com.tourbox.driver && launchctl start com.tourbox.driver
```

### Run linting
```bash
ruff check src/
ruff format src/
```

### Run tests
```bash
pytest
```

## Profile Format

Profiles map button names to actions:
```json
{
  "mappings": {
    "button_name": {
      "action": "cmd+c",              // Key combo
      "action": "type:text",          // Type literal text
      "action": "shell:command",      // Run shell command
      "action": ["a", "b"],           // Multiple actions
      "description": "Copy"
    }
  }
}
```

## Button Names

Main: `side`, `top`, `tall`, `short`
D-pad: `dpad_up`, `dpad_down`, `dpad_left`, `dpad_right`
C buttons: `c1`, `c2`
Scroll: `scroll_up`, `scroll_down`, `scroll_click`
Knob: `knob_cw`, `knob_ccw`, `knob_click`
Dial: `dial_cw`, `dial_ccw`, `dial_click`
Tour: `tour`

## Serial Protocol

- Port: `/dev/tty.usbmodemTourBox1`
- Baud: 115200
- Unlock: `5500078894001afe`
- Events: Single byte (bit 7 = release, bits 0-6 = button ID)

## Development Notes

- The driver runs as a launchd agent (auto-starts on login)
- Profile changes require driver restart
- Text typing uses `type:` prefix in action strings
- Shell commands use `shell:` prefix (e.g., `shell:claude-window`)
- Combo actions use arrays: `["type:/commit", "enter"]`

## Future Work (Roadmap)

1. **Phase 2:** FastAPI backend + Claude API for AI profile generation
2. **Phase 3:** Next.js web UI with visual editor
3. **Phase 4:** Polish, deployment, preset library
