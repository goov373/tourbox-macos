#!/usr/bin/env python3
"""TourBox macOS Driver

A cross-platform driver for TourBox devices on macOS.
Uses pyserial for device communication and pynput for keyboard simulation.
"""

import sys
import time
import json
import glob
import logging
import subprocess
import threading
from pathlib import Path
from typing import Optional, Dict, Callable, Tuple

import serial
from pynput.keyboard import Key, Controller as KeyboardController

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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

# pynput key mapping
PYNPUT_KEYS = {
    # Modifiers
    'cmd': Key.cmd,
    'ctrl': Key.ctrl,
    'alt': Key.alt,
    'shift': Key.shift,
    'cmd_l': Key.cmd_l,
    'cmd_r': Key.cmd_r,
    'ctrl_l': Key.ctrl_l,
    'ctrl_r': Key.ctrl_r,
    'alt_l': Key.alt_l,
    'alt_r': Key.alt_r,
    'shift_l': Key.shift_l,
    'shift_r': Key.shift_r,
    # Navigation
    'up': Key.up,
    'down': Key.down,
    'left': Key.left,
    'right': Key.right,
    'home': Key.home,
    'end': Key.end,
    'page_up': Key.page_up,
    'page_down': Key.page_down,
    # Special
    'space': Key.space,
    'enter': Key.enter,
    'tab': Key.tab,
    'esc': Key.esc,
    'backspace': Key.backspace,
    'delete': Key.delete,
    # Function keys
    'f1': Key.f1, 'f2': Key.f2, 'f3': Key.f3, 'f4': Key.f4,
    'f5': Key.f5, 'f6': Key.f6, 'f7': Key.f7, 'f8': Key.f8,
    'f9': Key.f9, 'f10': Key.f10, 'f11': Key.f11, 'f12': Key.f12,
}


class TourBoxDriver:
    """TourBox macOS Driver"""

    def __init__(self, port: str = None, profile_path: str = None):
        """Initialize the driver

        Args:
            port: Serial port path (auto-detected if None)
            profile_path: Path to JSON profile file
        """
        self.port = port or self._find_port()
        self.serial: Optional[serial.Serial] = None
        self.keyboard = KeyboardController()
        self.running = False
        self.profile: Dict = {}
        self._pressed_keys: Dict[str, list] = {}  # Track pressed keys per button

        if profile_path:
            self.load_profile(profile_path)
        else:
            self._load_default_profile()

    def _find_port(self) -> str:
        """Auto-detect TourBox serial port"""
        patterns = [
            '/dev/tty.usbmodemTourBox*',
            '/dev/tty.usbmodemSN*',
            '/dev/tty.usbmodem*',
        ]

        for pattern in patterns:
            ports = glob.glob(pattern)
            if ports:
                logger.info(f"Found TourBox at {ports[0]}")
                return ports[0]

        raise RuntimeError("TourBox not found. Is it connected via USB?")

    def _load_default_profile(self):
        """Load default universal profile"""
        self.profile = {
            "name": "Default Universal",
            "description": "Universal shortcuts for developer workflow",
            "mappings": {
                # Main buttons - universal actions
                "side": {"action": "cmd+c", "description": "Copy"},
                "top": {"action": "cmd+v", "description": "Paste"},
                "tall": {"action": "cmd+z", "description": "Undo"},
                "short": {"action": "cmd+shift+z", "description": "Redo"},

                # D-pad - navigation
                "dpad_up": {"action": "up", "description": "Up"},
                "dpad_down": {"action": "down", "description": "Down"},
                "dpad_left": {"action": "left", "description": "Left"},
                "dpad_right": {"action": "right", "description": "Right"},

                # C buttons - common actions
                "c1": {"action": "cmd+s", "description": "Save"},
                "c2": {"action": "cmd+w", "description": "Close Tab"},

                # Scroll wheel
                "scroll_up": {"action": "cmd+shift+]", "description": "Next Tab"},
                "scroll_down": {"action": "cmd+shift+[", "description": "Prev Tab"},
                "scroll_click": {"action": "cmd+t", "description": "New Tab"},

                # Knob - zoom
                "knob_cw": {"action": "cmd+=", "description": "Zoom In"},
                "knob_ccw": {"action": "cmd+-", "description": "Zoom Out"},
                "knob_click": {"action": "cmd+0", "description": "Reset Zoom"},

                # Dial - scroll
                "dial_cw": {"action": "page_down", "description": "Page Down"},
                "dial_ccw": {"action": "page_up", "description": "Page Up"},
                "dial_click": {"action": "home", "description": "Home"},

                # Tour button
                "tour": {"action": "cmd+space", "description": "Spotlight"},
            }
        }
        logger.info(f"Loaded default profile: {self.profile['name']}")

    def load_profile(self, path: str):
        """Load profile from JSON file"""
        with open(path, 'r') as f:
            self.profile = json.load(f)
        logger.info(f"Loaded profile: {self.profile.get('name', 'Unknown')}")

    def save_profile(self, path: str):
        """Save current profile to JSON file"""
        with open(path, 'w') as f:
            json.dump(self.profile, f, indent=2)
        logger.info(f"Saved profile to {path}")

    def connect(self) -> bool:
        """Connect to TourBox device"""
        try:
            logger.info(f"Connecting to {self.port}...")
            self.serial = serial.Serial(self.port, baudrate=115200, timeout=0.1)
            self.serial.reset_input_buffer()

            # Send unlock command
            logger.info("Sending unlock command...")
            self.serial.write(UNLOCK_COMMAND)
            self.serial.flush()
            time.sleep(0.3)

            # Check response
            response = self.serial.read(100)
            if response and response[0] == 0x07:
                logger.info("TourBox unlocked successfully!")
                return True
            else:
                logger.warning("No unlock response (may still work)")
                return True

        except serial.SerialException as e:
            logger.error(f"Connection error: {e}")
            return False

    def disconnect(self):
        """Disconnect from TourBox"""
        self.running = False
        if self.serial and self.serial.is_open:
            self.serial.close()
            logger.info("Disconnected from TourBox")

    def _parse_action(self, action_str: str) -> list:
        """Parse action string into key sequence

        Examples:
            "cmd+c" -> [Key.cmd, 'c']
            "cmd+shift+z" -> [Key.cmd, Key.shift, 'z']
            "up" -> [Key.up]
            "a" -> ['a']
        """
        parts = action_str.lower().split('+')
        keys = []

        for part in parts:
            part = part.strip()
            if part in PYNPUT_KEYS:
                keys.append(PYNPUT_KEYS[part])
            elif len(part) == 1:
                keys.append(part)
            else:
                logger.warning(f"Unknown key: {part}")

        return keys

    def _execute_action(self, action, is_press: bool, control_name: str):
        """Execute a keyboard action

        Args:
            action: Action string like "cmd+c", "type:text", or list of actions
            is_press: True for press, False for release
            control_name: Name of the control for tracking
        """
        # Handle action arrays (combo actions)
        if isinstance(action, list):
            if is_press:
                for act in action:
                    self._execute_single_action(act, control_name)
            return

        self._execute_single_action(action, control_name, is_press)

    def _execute_single_action(self, action_str: str, control_name: str, is_press: bool = True):
        """Execute a single keyboard action

        Args:
            action_str: Action string like "cmd+c" or "type:text"
            control_name: Name of the control for tracking
            is_press: True for press, False for release (ignored for type: actions)
        """
        if action_str.lower() == 'none':
            return

        # Handle text typing actions
        if action_str.startswith('type:'):
            if is_press:
                text = action_str[5:]  # Remove 'type:' prefix
                self.keyboard.type(text)
                logger.debug(f"Typed: {text}")
            return

        # Handle shell command actions
        if action_str.startswith('shell:'):
            if is_press:
                cmd = action_str[6:]  # Remove 'shell:' prefix
                try:
                    subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    logger.debug(f"Executed: {cmd}")
                except Exception as e:
                    logger.error(f"Shell command failed: {e}")
            return

        keys = self._parse_action(action_str)
        if not keys:
            return

        if is_press:
            # Press all keys in order
            self._pressed_keys[control_name] = keys
            for key in keys:
                self.keyboard.press(key)
            # Release immediately for single actions (tap behavior)
            for key in reversed(keys):
                self.keyboard.release(key)
            logger.debug(f"Tapped: {action_str}")
        else:
            # For explicit release (held keys)
            stored_keys = self._pressed_keys.pop(control_name, keys)
            for key in reversed(stored_keys):
                self.keyboard.release(key)
            logger.debug(f"Released: {action_str}")

    def _handle_button_event(self, byte_val: int):
        """Handle a button event byte"""
        is_release = (byte_val & 0x80) != 0
        button_id = byte_val & 0x7F

        control_name = BUTTON_CODES.get(button_id)
        if not control_name:
            logger.warning(f"Unknown button code: 0x{byte_val:02x}")
            return

        # Get action from profile
        mapping = self.profile.get('mappings', {}).get(control_name)
        if not mapping:
            logger.debug(f"No mapping for {control_name}")
            return

        action = mapping.get('action', 'none')
        is_press = not is_release

        # For rotary controls, always treat as press-release cycle
        is_rotary = control_name in ['scroll_up', 'scroll_down', 'knob_cw', 'knob_ccw', 'dial_cw', 'dial_ccw']

        if is_rotary:
            if is_press:
                # Execute as tap (press + release) - _execute_action handles this
                self._execute_action(action, True, control_name)
                logger.info(f"{control_name}: {action}")
        else:
            self._execute_action(action, is_press, control_name)
            if is_press:
                logger.info(f"{control_name} press: {action}")

    def run(self):
        """Main driver loop"""
        if not self.serial or not self.serial.is_open:
            if not self.connect():
                return

        self.running = True
        print("\n" + "=" * 50)
        print("TourBox macOS Driver Running")
        print(f"Profile: {self.profile.get('name', 'Unknown')}")
        print("=" * 50)
        print("\nPress Ctrl+C to stop\n")

        # Print current mappings
        print("Current mappings:")
        for control, mapping in self.profile.get('mappings', {}).items():
            action = mapping.get('action', 'none')
            desc = mapping.get('description', '')
            print(f"  {control:15s} -> {action:20s} ({desc})")
        print()

        try:
            while self.running:
                if self.serial.in_waiting > 0:
                    data = self.serial.read(1)
                    if data:
                        self._handle_button_event(data[0])
                else:
                    time.sleep(0.01)

        except KeyboardInterrupt:
            print("\nStopping...")
        finally:
            self.disconnect()


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='TourBox macOS Driver')
    parser.add_argument('--port', '-p', help='Serial port path')
    parser.add_argument('--profile', '-f', help='Path to JSON profile file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable debug logging')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        driver = TourBoxDriver(port=args.port, profile_path=args.profile)
        driver.run()
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
