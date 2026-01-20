# TourBox Serial Protocol Documentation

Based on reverse engineering from [tourbox-linux](https://github.com/AndyCappDev/tourbox-linux).

## Connection Setup

### USB Serial Parameters
- **Port**: `/dev/tty.usbmodemTourBox1` or `/dev/tty.usbmodemSN*` (macOS)
- **Baud rate**: 115200
- **Timeout**: 0.1 seconds

### Initialization Sequence

1. **Open serial port** at 115200 baud
2. **Clear input buffer** (`serial.reset_input_buffer()`)
3. **Send unlock command**: `5500078894001afe` (8 bytes hex)
4. **Wait 300ms** for device initialization
5. **Read response** (expect ~26 bytes, starts with `0x07`)
6. **(Optional) Send haptic config** for Elite/Elite Plus models

### Unlock Command
```
55 00 07 88 94 00 1a fe
```

## Button Events

Each button event is a **single byte**:
- **Press**: bit 7 = 0 (0x00-0x7F)
- **Release**: bit 7 = 1 (0x80-0xFF)
- **Button ID**: byte & 0x7F

## Button Code Reference

### Buttons (press/release pairs)
| Control | Press | Release | Description |
|---------|-------|---------|-------------|
| side | 0x01 | 0x81 | Side button |
| top | 0x02 | 0x82 | Top button |
| tall | 0x00 | 0x80 | Tall button |
| short | 0x03 | 0x83 | Short button |
| c1 | 0x22 | 0xa2 | C1 button |
| c2 | 0x23 | 0xa3 | C2 button |
| dpad_up | 0x10 | 0x90 | D-pad up |
| dpad_down | 0x11 | 0x91 | D-pad down |
| dpad_left | 0x12 | 0x92 | D-pad left |
| dpad_right | 0x13 | 0x93 | D-pad right |
| scroll_click | 0x0a | 0x8a | Scroll wheel click |
| knob_click | 0x37 | 0xb7 | Knob click |
| dial_click | 0x38 | 0xb8 | Dial click |
| tour | 0x2a | 0xaa | Tour button |

### Rotary Controls (momentary events)
| Control | CW/Up | CCW/Down | Description |
|---------|-------|----------|-------------|
| scroll_up | 0x49 | 0xc9 | Scroll wheel up (tick/stop) |
| scroll_down | 0x09 | 0x89 | Scroll wheel down (tick/stop) |
| knob_cw | 0x44 | 0xc4 | Knob clockwise (tick/stop) |
| knob_ccw | 0x04 | 0x84 | Knob counter-clockwise (tick/stop) |
| dial_cw | 0x4f | 0xcf | Dial clockwise (tick/stop) |
| dial_ccw | 0x0f | 0x8f | Dial counter-clockwise (tick/stop) |

## TourBox Lite Notes

The TourBox Lite uses the **same button codes** as Elite/Neo but has fewer physical buttons:
- Fewer buttons overall (compact form factor)
- No haptic feedback
- Same serial protocol

## macOS Considerations

1. **Serial ports**: Appear as `/dev/tty.usbmodem*` instead of `/dev/ttyACM*`
2. **Permissions**: May need to grant Terminal/app access in System Settings > Privacy & Security
3. **Input simulation**: Use `pynput` (cross-platform) or `Quartz/CGEvent` (native)

## Configuration Commands (Haptics)

For Elite/Elite Plus with haptic feedback, send these after unlock:
```python
CONFIG_COMMANDS = [
    bytes.fromhex("b5005d0400050006000700080009000b000c000d"),
    bytes.fromhex("000e000f0026002700280029003b003c003d003e"),
    bytes.fromhex("003f004000410042004300440045004600470048"),
    bytes.fromhex("0049004a004b004c004d004e004f005000510052"),
    bytes.fromhex("0053005400a800a900aa00ab00fe"),
]
```

Note: TourBox Lite does NOT have haptics - skip these commands.
