# System Architecture

## Overview

The TourBox macOS driver is a Python application that:
1. Communicates with TourBox Lite hardware via USB serial
2. Reads button events from the device
3. Simulates keyboard input based on profile mappings

## Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│                    User Space                        │
│                                                      │
│  ┌─────────────────┐      ┌─────────────────────┐   │
│  │  tourbox_driver │      │   JSON Profiles     │   │
│  │     .py         │◄─────│  (developer.json)   │   │
│  └────────┬────────┘      └─────────────────────┘   │
│           │                                          │
│           │ pynput                                   │
│           ▼                                          │
│  ┌─────────────────┐                                │
│  │ Keyboard Events │──────► Active Application      │
│  │  (simulated)    │        (Ghostty, Cursor, etc) │
│  └─────────────────┘                                │
└─────────────────────────────────────────────────────┘
           ▲
           │ pyserial (115200 baud)
           │
┌──────────┴──────────┐
│   TourBox Lite      │
│   (USB Serial)      │
│   /dev/tty.usb...   │
└─────────────────────┘
```

## Components

### 1. TourBox Driver (`tourbox_driver.py`)

The main driver handles:

| Component | Responsibility |
|-----------|----------------|
| `TourBoxDriver` class | Main driver logic |
| `_find_port()` | Auto-detect TourBox USB port |
| `connect()` | Open serial, send unlock command |
| `_handle_button_event()` | Parse button bytes, route to action |
| `_execute_action()` | Execute keyboard shortcuts or text |
| `run()` | Main event loop |

### 2. Serial Communication

**Connection:**
- Port: `/dev/tty.usbmodemTourBox1` (auto-detected)
- Baud: 115200
- Unlock command: `5500078894001afe`

**Event format:** Single byte per event
- Bit 7 = 0: Button press
- Bit 7 = 1: Button release
- Bits 0-6: Button ID

### 3. Keyboard Simulation

Uses `pynput` library for cross-platform keyboard control:
- Modifier keys: `cmd`, `ctrl`, `alt`, `shift`
- Navigation: `up`, `down`, `left`, `right`, `page_up`, `page_down`
- Special: `enter`, `tab`, `esc`, `space`, `backspace`
- Function keys: `f1`-`f12`

### 4. Profile System

JSON files define button-to-action mappings:
```json
{
  "name": "Profile Name",
  "mappings": {
    "button_name": {
      "action": "cmd+c",
      "description": "Copy"
    }
  }
}
```

## Auto-Start (launchd)

The driver runs as a user launch agent:

**Plist location:** `~/Library/LaunchAgents/com.tourbox.driver.plist`

**Behavior:**
- Starts on user login (`RunAtLoad: true`)
- Restarts if it crashes (`KeepAlive.SuccessfulExit: false`)
- Logs to `/tmp/tourbox-driver.log`

**Management:**
```bash
launchctl start com.tourbox.driver   # Start
launchctl stop com.tourbox.driver    # Stop
launchctl list | grep tourbox        # Status
```

## Data Flow

```
1. User presses button on TourBox
   │
2. TourBox sends byte over USB serial
   │
3. Driver reads byte, extracts button ID
   │
4. Driver looks up action in profile
   │
5. Driver simulates keyboard shortcut via pynput
   │
6. Active application receives keystroke
```

## Future Architecture (Planned)

```
┌─────────────────────────────────────────────────────┐
│                 Next.js Frontend                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │   Visual    │  │  AI Chat    │  │   Profile   │  │
│  │   Editor    │  │  Interface  │  │   Manager   │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
└────────────────────────┬────────────────────────────┘
                         │ REST + WebSocket
┌────────────────────────▼────────────────────────────┐
│              Python FastAPI Backend                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │   TourBox   │  │   Claude    │  │   Profile   │  │
│  │   Driver    │  │     API     │  │   Manager   │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────┘
```

Phase 2 will add:
- FastAPI backend wrapping the driver
- Claude API integration for AI profile generation
- WebSocket for real-time button feedback

Phase 3 will add:
- Next.js web UI
- Visual TourBox editor
- AI chat for profile creation
