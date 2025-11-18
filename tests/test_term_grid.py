"""Tests for the term_grid.py module."""

import pytest
import numpy as np
import display_grid as dg

@pytest.fixture
def mock_urwid_screen(mocker):
    """Mocks the urwid.display.raw.Screen."""
    screen = mocker.Mock()
    screen.get_cols_rows.return_value = (80, 24)
    screen.get_input.return_value = []
    return screen

def test_term_grid_init(mock_urwid_screen):
    """Tests the TermGrid constructor."""
    grid = dg.TermGrid(mock_urwid_screen)
    assert grid.shape == (24, 80)
    assert grid.scr is mock_urwid_screen
    mock_urwid_screen.set_mouse_tracking.assert_called_once_with(True)
    mock_urwid_screen.clear.assert_called_once()

def test_term_grid_init_with_shape(mock_urwid_screen):
    """Tests TermGrid constructor with an explicit shape."""
    grid = dg.TermGrid(mock_urwid_screen, shape=(10, 20))
    assert grid.shape == (10, 20)

def test_term_grid_get_real_shape(mock_urwid_screen):
    """Tests the get_real_shape method."""
    grid = dg.TermGrid(mock_urwid_screen)
    assert grid.get_real_shape() == (24, 80)

def test_term_grid_draw(mock_urwid_screen, mocker):
    """Tests the draw method to ensure it calls the screen's draw_screen."""
    mocker.patch('urwid.Text')
    grid = dg.TermGrid(mock_urwid_screen, shape=(2, 3))
    grid.print("Hi", pos=(0, 0))
    grid.draw()
    
    mock_urwid_screen.draw_screen.assert_called_once()
    # We can do more detailed checks on the markup if needed,
    # but this confirms the core drawing call is made.

def test_term_grid_events_key(mock_urwid_screen):
    """Tests keyboard event translation."""
    mock_urwid_screen.get_input.return_value = ["a", "enter", "shift f1"]
    grid = dg.TermGrid(mock_urwid_screen)
    events = grid.events()
    
    assert len(events) == 3
    assert isinstance(events[0], dg.KeyEvent)
    assert events[0].key == "a"
    assert events[0].mod == dg.KM_NONE

    assert isinstance(events[1], dg.KeyEvent)
    assert events[1].key == "\n"
    
    assert isinstance(events[2], dg.KeyEvent)
    assert events[2].key == "f1"
    assert events[2].mod == dg.KM_SHIFT

def test_term_grid_events_mouse(mock_urwid_screen):
    """Tests mouse event translation."""
    mock_urwid_screen.get_input.return_value = [
        ("mouse press", 1, 10, 5),
        ("ctrl mouse release", 2, 20, 15),
    ]
    grid = dg.TermGrid(mock_urwid_screen)
    events = grid.events()

    assert len(events) == 2
    assert isinstance(events[0], dg.MouseEvent)
    assert events[0].button == 1
    assert events[0].state is True
    assert events[0].pos == (5, 10)
    assert events[0].mod == dg.KM_NONE

    assert isinstance(events[1], dg.MouseEvent)
    assert events[1].button == 2
    assert events[1].state is False
    assert events[1].pos == (15, 20)
    assert events[1].mod == dg.KM_CTRL
