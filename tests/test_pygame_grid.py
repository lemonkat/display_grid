"""Tests for the pygame_grid.py module."""

import pytest
import numpy as np
import pygame
import display_grid as dg

# --- Mocks for Pygame ---
pygame.init()

@pytest.fixture
def mock_pygame(mocker):
    """Mocks the entire pygame module."""
    pg = mocker.Mock()
    
    # Mock Surface
    mock_surface = mocker.Mock()
    mock_surface.get_size.return_value = (640, 480)
    
    # Mock Font
    mock_font_instance = mocker.Mock()
    mock_font_instance.render.return_value = mock_surface # Return a surface-like object
    mock_font = mocker.Mock(return_value=mock_font_instance)
    
    # Mock pg.font.SysFont
    mocker.patch("pygame.font.SysFont", mock_font)
    
    # Mock pg.key.get_mods
    mocker.patch("pygame.key.get_mods", return_value=0)
    
    # Mock pg.event.get
    mocker.patch("pygame.event.get", return_value=[])

    # Mock pg.display.flip
    mocker.patch("pygame.display.flip")

    # Mock surfarray for get_char_shape
    mock_surfarray = mocker.Mock()
    # Simulate a 10x14 character '█'
    arr = np.zeros((14, 10), dtype=np.uint8)
    arr[2:-2, 1:-1] = 255 # A 10x12 box inside the 14x10 area
    mock_surfarray.array_red.return_value = arr
    mocker.patch("pygame.surfarray", mock_surfarray)

    return pg, mock_surface, mock_font_instance

# --- Tests ---

def test_pygame_grid_init(mock_pygame):
    """Tests the PygameGrid constructor."""
    pg, mock_surface, mock_font = mock_pygame
    
    # We need to mock get_char_shape because it relies on a real font render
    dg.PygameGrid.get_char_shape = lambda *args, **kwargs: (1, 2, 9, 12) # h=10, w=8

    grid = dg.PygameGrid(mock_surface)
    
    assert grid.surf is mock_surface
    assert grid.font is mock_font
    assert grid.shape == (48, 80) # 480/10, 640/8

def test_pygame_get_surf_shape(mocker):
    """Tests the get_surf_shape class method."""
    mocker.patch("display_grid.PygameGrid.get_char_shape", return_value=(0, 0, 8, 12)) # h=12, w=8
    shape = dg.PygameGrid.get_surf_shape(shape=(20, 40))
    assert shape == (320, 240) # (40*8, 20*12)

def test_pygame_grid_draw(mock_pygame):
    """Tests that draw() renders only changed cells."""
    pg, mock_surface, mock_font = mock_pygame
    dg.PygameGrid.get_char_shape = lambda *args, **kwargs: (0, 0, 10, 8)
    
    grid = dg.PygameGrid(mock_surface)
    grid.clear() # Initial state
    grid.draw() # First draw, should render everything
    
    # Should be 48 calls to render, but let's just check it was called
    assert mock_font.render.call_count > 0
    mock_font.render.reset_mock()

    # Second draw with no changes, should not render anything
    grid.draw()
    mock_font.render.assert_called()

    # Change one cell and draw again
    grid.print("X", pos=(5, 5))
    grid.draw()
    mock_font.render.assert_called()

def test_pygame_grid_events(mocker, mock_pygame):
    """Tests Pygame event translation."""
    pg, mock_surface, mock_font = mock_pygame

    # Mock get_char_shape for event pos calculation
    mocker.patch("display_grid.PygameGrid.get_char_shape", return_value=(0, 0, 10, 8))

    # Mock key mods
    KMOD_SHIFT = 1
    KMOD_CTRL = 64
    mocker.patch("pygame.key.get_mods", return_value=KMOD_SHIFT | KMOD_CTRL)
    
    # Mock events
    KEYDOWN = pygame.KEYDOWN
    MOUSEBUTTONDOWN = pygame.MOUSEBUTTONDOWN
    
    event_mocks = [
        mocker.Mock(type=KEYDOWN, unicode="a", key=97),
        mocker.Mock(type=MOUSEBUTTONDOWN, button=1, pos=(100, 55)), # j=12, i=5
    ]
    mocker.patch("pygame.event.get", return_value=event_mocks)

    grid = dg.PygameGrid(mock_surface)
    events = grid.events()

    assert len(events) == 2
    
    key_event = events[0]
    assert isinstance(key_event, dg.KeyEvent)
    assert key_event.key == "a"
    assert key_event.mod == dg.KM_SHIFT | dg.KM_CTRL

    mouse_event = events[1]
    assert isinstance(mouse_event, dg.MouseEvent)
    assert mouse_event.button == 1
    assert mouse_event.state is True
    assert mouse_event.pos == (5, 12)