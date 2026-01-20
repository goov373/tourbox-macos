# TourBox macOS Driver

A custom macOS driver for TourBox Lite that replaces the official TourBox Console with an open, hackable solution. Features JSON-based profiles and AI-powered profile generation (coming soon).

## Features

- **Native macOS support** - Works with TourBox Lite via USB serial
- **JSON profiles** - Human-readable, easily editable configuration
- **Text typing** - Type literal strings with `type:` actions
- **Combo actions** - Chain multiple actions together
- **Auto-start** - Runs automatically on login via launchd

## Quick Start

### Prerequisites

```bash
pip3 install pyserial pynput
```

### Run Manually

```bash
cd ~/Projects/tourbox-ai/tourbox-macos/src
python3 tourbox_driver.py -f ../profiles/developer.json
```

### Auto-Start on Login

The driver is configured to start automatically via launchd:

```bash
# Check status
launchctl list | grep tourbox

# View logs
tail -f /tmp/tourbox-driver.log

# Stop
launchctl stop com.tourbox.driver

# Start
launchctl start com.tourbox.driver

# Disable auto-start
launchctl unload ~/Library/LaunchAgents/com.tourbox.driver.plist

# Re-enable auto-start
launchctl load ~/Library/LaunchAgents/com.tourbox.driver.plist
```

## Project Structure

```
tourbox-macos/
├── src/
│   └── tourbox_driver.py    # Main driver
├── profiles/
│   ├── default.json         # Default universal profile
│   └── developer.json       # Developer workflow profile
├── docs/
│   ├── PROTOCOL.md          # Serial protocol documentation
│   ├── ARCHITECTURE.md      # System architecture
│   └── PROFILES.md          # Profile format reference
└── README.md
```

## Profiles

Profiles are JSON files that map TourBox buttons to keyboard actions.

**Current profiles:**
- `default.json` - Universal shortcuts (copy, paste, undo, redo, etc.)
- `developer.json` - Optimized for Claude Code, Ghostty, and Cursor

See [docs/PROFILES.md](docs/PROFILES.md) for the full profile format reference.

## Button Reference

| Control | Description |
|---------|-------------|
| `side`, `top`, `tall`, `short` | Main buttons |
| `dpad_up/down/left/right` | D-pad navigation |
| `c1`, `c2` | C buttons |
| `scroll_up/down`, `scroll_click` | Scroll wheel |
| `knob_cw/ccw`, `knob_click` | Knob (top rotary) |
| `dial_cw/ccw`, `dial_click` | Dial (bottom rotary) |
| `tour` | Tour button |

## Documentation

- [PROTOCOL.md](docs/PROTOCOL.md) - Serial protocol details
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - System architecture
- [PROFILES.md](docs/PROFILES.md) - Profile format reference

## Roadmap

- [x] Phase 1: macOS driver foundation
- [x] Text typing support
- [x] Developer profile
- [ ] Phase 2: AI integration (Claude API for profile generation)
- [ ] Phase 3: Web frontend (Next.js visual editor)
- [ ] Phase 4: Polish & deployment
