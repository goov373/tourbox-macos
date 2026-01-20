# Profile Format Reference

Profiles are JSON files that define how TourBox buttons map to keyboard actions.

## Profile Structure

```json
{
  "name": "Profile Name",
  "description": "What this profile is for",
  "version": "1.0",
  "target_apps": ["App1", "App2"],
  "mappings": {
    "button_name": {
      "action": "cmd+c",
      "description": "Copy"
    }
  }
}
```

### Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Display name for the profile |
| `description` | No | What this profile is optimized for |
| `version` | No | Profile version |
| `target_apps` | No | List of apps this profile works with |
| `mappings` | Yes | Button-to-action mappings |

## Action Types

### 1. Key Combinations

Standard keyboard shortcuts using `+` to combine keys.

```json
"action": "cmd+c"           // Cmd+C (copy)
"action": "cmd+shift+z"     // Cmd+Shift+Z (redo)
"action": "ctrl+alt+delete" // Ctrl+Alt+Delete
```

### 2. Single Keys

Navigation and special keys.

```json
"action": "up"              // Arrow up
"action": "page_down"       // Page down
"action": "enter"           // Enter/Return
"action": "f5"              // F5
```

### 3. Text Typing

Type literal text using the `type:` prefix.

```json
"action": "type:/commit"    // Types "/commit"
"action": "type:hello"      // Types "hello"
```

### 4. Combo Actions (Arrays)

Execute multiple actions in sequence.

```json
"action": ["type:/commit", "enter"]  // Types "/commit" then presses Enter
"action": ["cmd+a", "cmd+c"]         // Select all, then copy
```

### 5. Shell Commands

Execute shell commands using the `shell:` prefix.

```json
"action": "shell:claude-window"           // Run command in PATH
"action": "shell:open -a Safari"          // Open an application
"action": "shell:~/.local/bin/my-script"  // Run a script
```

**Note:** Commands run via the user's default shell. For commands that need
environment variables from `.zshrc`/`.bashrc`, create a wrapper script that
uses a login shell (e.g., `zsh -l -c 'command'`).

### 6. No Action

Disable a button.

```json
"action": "none"
```

## Available Keys

### Modifiers

| Key | macOS |
|-----|-------|
| `cmd` | Command (⌘) |
| `ctrl` | Control (⌃) |
| `alt` | Option (⌥) |
| `shift` | Shift (⇧) |

### Navigation

| Key | Description |
|-----|-------------|
| `up`, `down`, `left`, `right` | Arrow keys |
| `page_up`, `page_down` | Page navigation |
| `home`, `end` | Line/document start/end |

### Special Keys

| Key | Description |
|-----|-------------|
| `enter` | Return/Enter |
| `tab` | Tab |
| `space` | Spacebar |
| `esc` | Escape |
| `backspace` | Backspace/Delete |
| `delete` | Forward delete |

### Function Keys

`f1`, `f2`, `f3`, `f4`, `f5`, `f6`, `f7`, `f8`, `f9`, `f10`, `f11`, `f12`

### Characters

Any single character: `a`, `b`, `1`, `2`, `-`, `=`, `[`, `]`, etc.

## Button Names

### Main Buttons

| Name | Physical Location |
|------|-------------------|
| `tall` | Large button (left side) |
| `short` | Small button (below tall) |
| `side` | Side button |
| `top` | Top button |

### D-Pad

| Name | Direction |
|------|-----------|
| `dpad_up` | Up |
| `dpad_down` | Down |
| `dpad_left` | Left |
| `dpad_right` | Right |

### C Buttons

| Name | Position |
|------|----------|
| `c1` | C1 button |
| `c2` | C2 button |

### Scroll Wheel (Top)

| Name | Action |
|------|--------|
| `scroll_up` | Scroll up (each tick) |
| `scroll_down` | Scroll down (each tick) |
| `scroll_click` | Press scroll wheel |

### Knob (Middle Rotary)

| Name | Action |
|------|--------|
| `knob_cw` | Rotate clockwise |
| `knob_ccw` | Rotate counter-clockwise |
| `knob_click` | Press knob |

### Dial (Bottom Rotary)

| Name | Action |
|------|--------|
| `dial_cw` | Rotate clockwise |
| `dial_ccw` | Rotate counter-clockwise |
| `dial_click` | Press dial |

### Tour Button

| Name | Description |
|------|-------------|
| `tour` | Tour button (center) |

## Example Profiles

### Minimal Profile

```json
{
  "name": "Minimal",
  "mappings": {
    "side": { "action": "cmd+c", "description": "Copy" },
    "top": { "action": "cmd+v", "description": "Paste" }
  }
}
```

### Developer Profile

```json
{
  "name": "Developer Mode",
  "description": "Optimized for terminal and code editors",
  "mappings": {
    "side": { "action": "cmd+c", "description": "Copy" },
    "top": { "action": "cmd+v", "description": "Paste" },
    "tall": { "action": "cmd+z", "description": "Undo" },
    "short": { "action": "cmd+shift+z", "description": "Redo" },
    "c1": { "action": "ctrl+c", "description": "Terminal interrupt" },
    "c2": { "action": "cmd+w", "description": "Close tab" },
    "knob_click": { "action": "shift+tab", "description": "Cycle mode" },
    "dial_click": { "action": "cmd+n", "description": "New window" },
    "tour": { "action": "shell:claude-window", "description": "New Ghostty + Claude" }
  }
}
```

### Claude Code Profile (with text typing)

```json
{
  "name": "Claude Code",
  "mappings": {
    "c1": {
      "action": ["type:/commit", "enter"],
      "description": "Run /commit command"
    },
    "c2": {
      "action": ["type:/help", "enter"],
      "description": "Run /help command"
    },
    "knob_click": {
      "action": "shift+tab",
      "description": "Cycle Chat/Edit/Agent mode"
    }
  }
}
```

## Loading Profiles

```bash
# Use specific profile
python3 tourbox_driver.py -f /path/to/profile.json

# Use default profile (built-in)
python3 tourbox_driver.py
```

## Creating Custom Profiles

1. Copy an existing profile as a starting point
2. Edit the `mappings` section
3. Test with: `python3 tourbox_driver.py -f your_profile.json`
4. Check logs: `tail -f /tmp/tourbox-driver.log`
