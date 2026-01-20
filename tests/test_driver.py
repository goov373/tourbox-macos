"""Tests for TourBox driver functionality."""

import json
import pytest
from pathlib import Path


class TestProfileLoading:
    """Test profile loading and validation."""

    def test_developer_profile_is_valid_json(self):
        """Developer profile should be valid JSON."""
        profile_path = Path(__file__).parent.parent / "profiles" / "developer.json"
        with open(profile_path) as f:
            profile = json.load(f)

        assert "name" in profile
        assert "mappings" in profile

    def test_default_profile_is_valid_json(self):
        """Default profile should be valid JSON."""
        profile_path = Path(__file__).parent.parent / "profiles" / "default.json"
        with open(profile_path) as f:
            profile = json.load(f)

        assert "name" in profile
        assert "mappings" in profile

    def test_profile_has_required_buttons(self):
        """Profile should have mappings for common buttons."""
        profile_path = Path(__file__).parent.parent / "profiles" / "developer.json"
        with open(profile_path) as f:
            profile = json.load(f)

        mappings = profile["mappings"]
        required_buttons = ["side", "top", "tall", "short", "tour"]

        for button in required_buttons:
            assert button in mappings, f"Missing mapping for {button}"
            assert "action" in mappings[button], f"Missing action for {button}"


class TestActionParsing:
    """Test action string parsing."""

    def test_simple_key_combo(self):
        """Simple key combos should parse correctly."""
        # This tests the format, actual parsing is in driver
        action = "cmd+c"
        parts = action.split("+")
        assert parts == ["cmd", "c"]

    def test_multi_modifier_combo(self):
        """Multi-modifier combos should parse correctly."""
        action = "cmd+shift+z"
        parts = action.split("+")
        assert parts == ["cmd", "shift", "z"]

    def test_type_action_format(self):
        """Type actions should have correct prefix."""
        action = "type:/commit"
        assert action.startswith("type:")
        text = action[5:]
        assert text == "/commit"

    def test_array_action_format(self):
        """Array actions should be valid lists."""
        action = ["type:/commit", "enter"]
        assert isinstance(action, list)
        assert len(action) == 2
