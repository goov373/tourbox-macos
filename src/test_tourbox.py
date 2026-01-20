#!/usr/bin/env python3
"""Test script for TourBox on macOS

This script tests USB serial communication with a TourBox device.
It will display button press/release events in real-time.

Usage:
    python test_tourbox.py [port]

If no port is specified, it will try to auto-detect the TourBox.
"""

import sys
import time
import glob

try:
    import serial
except ImportError:
    print("Error: pyserial is required")
    print("Install with: pip install pyserial")
    sys.exit(1)


# TourBox Protocol Constants
UNLOCK_COMMAND = bytes.fromhex("5500078894001afe")

# Button code to name mapping
BUTTON_CODES = {
    # Buttons (press codes)
    0x00: 'tall',
    0x01: 'side',
    0x02: 'top',
    0x03: 'short',
    0x0a: 'scroll_click',
    0x10: 'dpad_up',
    0x11: 'dpad_down',
    0x12: 'dpad_left',
    0x13: 'dpad_right',
    0x22: 'c1',
    0x23: 'c2',
    0x2a: 'tour',
    0x37: 'knob_click',
    0x38: 'dial_click',
    # Rotary controls
    0x04: 'knob_ccw',
    0x44: 'knob_cw',
    0x09: 'scroll_down',
    0x49: 'scroll_up',
    0x0f: 'dial_ccw',
    0x4f: 'dial_cw',
}


def find_tourbox_port():
    """Auto-detect TourBox serial port on macOS"""
    patterns = [
        '/dev/tty.usbmodemTourBox*',
        '/dev/tty.usbmodemSN*',
        '/dev/tty.usbmodem*',
    ]

    for pattern in patterns:
        ports = glob.glob(pattern)
        if ports:
            return ports[0]

    return None


def get_button_name(byte_val):
    """Get button name and state from byte value"""
    is_release = (byte_val & 0x80) != 0
    button_id = byte_val & 0x7F

    name = BUTTON_CODES.get(button_id, f'unknown_0x{button_id:02x}')
    state = 'RELEASE' if is_release else 'PRESS'

    return name, state, button_id


def main():
    print("=" * 60)
    print("TourBox macOS Test")
    print("=" * 60)

    # Get port from command line or auto-detect
    if len(sys.argv) > 1:
        port = sys.argv[1]
    else:
        port = find_tourbox_port()
        if not port:
            print("\nError: Could not find TourBox device")
            print("\nTry one of these:")
            print("  1. Check that TourBox is connected via USB")
            print("  2. Run: ls /dev/tty.usbmodem*")
            print("  3. Specify port manually: python test_tourbox.py /dev/tty.usbmodemXXX")
            sys.exit(1)

    print(f"\nConnecting to {port}...")

    try:
        ser = serial.Serial(port, baudrate=115200, timeout=0.1)
    except serial.SerialException as e:
        print(f"\nError opening {port}: {e}")
        print("\nMake sure the TourBox Console app is NOT running.")
        sys.exit(1)

    print(f"Connected!\n")

    # Clear any pending data
    ser.reset_input_buffer()

    # Send unlock command
    print("Sending unlock command...")
    ser.write(UNLOCK_COMMAND)
    ser.flush()
    time.sleep(0.3)

    # Check for response
    response = ser.read(100)
    if response:
        print(f"Response: {response.hex()} ({len(response)} bytes)")
        if response[0:1] == b'\x07':
            print("Unlock successful!\n")
    else:
        print("No response (this may be normal)\n")

    print("=" * 60)
    print("Device ready! Press buttons on your TourBox...")
    print("Press Ctrl+C to exit")
    print("=" * 60)
    print()

    event_count = 0

    try:
        while True:
            data = ser.read(1)
            if data:
                event_count += 1
                byte_val = data[0]
                name, state, button_id = get_button_name(byte_val)

                # Format output with color for terminals that support it
                if state == 'PRESS':
                    print(f"[{event_count:4d}] {name:15s} {state:8s} (0x{byte_val:02x})")
                else:
                    print(f"[{event_count:4d}] {name:15s} {state:8s} (0x{byte_val:02x})")

    except KeyboardInterrupt:
        print(f"\n\nExiting... Received {event_count} events total.")

    finally:
        ser.close()
        print("Connection closed.")


if __name__ == "__main__":
    main()
