"""Tests for the util.py module."""

import pytest
from display_grid import util

@pytest.mark.parametrize("seconds, expected", [
    (0, "0:00"),
    (30, "0:30"),
    (59, "0:59"),
    (60, "1:00"),
    (125, "2:05"),
    (3599, "59:59"),
    (3600, "1:00:00"),
    (3661, "1:01:01"),
    (86399, "23:59:59"),
])
def test_format_time(seconds, expected):
    """Tests the format_time function with various durations."""
    assert util.format_time(seconds) == expected

def test_event_base_class():
    """Tests that the Event base class can be instantiated."""
    event = util.Event()
    assert isinstance(event, util.Event)

def test_key_event():
    """Tests the KeyEvent data class."""
    event = util.KeyEvent(key="a", mod=1)
    assert event.key == "a"
    assert event.mod == 1

def test_mouse_event():
    """Tests the MouseEvent data class."""
    event = util.MouseEvent(button=1, state=True, pos=(10, 20), mod=2)
    assert event.button == 1
    assert event.state is True
    assert event.pos == (10, 20)
    assert event.mod == 2