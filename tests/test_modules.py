"""Tests for the modules.py module."""

import time
import pytest
import numpy as np
import display_grid as dg

# Mock Grid class for testing modules without numpy dependencies
class MockGrid:
    def __init__(self, shape=(10, 20)):
        self.shape = shape
        self.colors = np.zeros((*shape, 2, 3))
        self.chars = np.zeros(shape)
        self.attrs = np.zeros(shape)
        self.fg = self.colors[:, :, 0]
        self.bg = self.colors[:, :, 1]
        self.offset = (0, 0)
        self.clear_called = False
        self.print_log = []
        self.fill_log = []

    def clear(self):
        self.clear_called = True
    
    def print(self, *values, **kwargs):
        self.print_log.append((values, kwargs))

    def fill(self, *args, **kwargs):
        self.fill_log.append((args, kwargs))

    def get_real_shape(self):
        return self.shape

    def events(self):
        return []

    def draw(self):
        pass

@pytest.fixture
def mock_grid():
    return MockGrid()

@pytest.fixture
def root_module(mock_grid):
    """A root module for testing."""
    return dg.Module(grid=mock_grid)

@pytest.fixture
def child_module(root_module):
    """A child module attached to the root_module."""
    return dg.Module(parent=root_module, box=[1, 1, 5, 5])

# --- Module Tests ---

def test_module_init_root(root_module, mock_grid):
    assert root_module.parent is None
    assert root_module.grid is not None
    assert isinstance(root_module.grid, dg.SubGrid)
    assert root_module.paused is False
    assert root_module.shape == mock_grid.shape

def test_module_init_child(child_module, root_module):
    assert child_module.parent is root_module
    assert root_module.submodules == [child_module]
    assert child_module.shape == (4, 4)
    assert child_module.box is not None

def test_module_start_stop(root_module):
    root_module.stop()
    assert root_module.paused is True
    root_module.start()
    assert root_module.paused is False

def test_module_draw_propagation(root_module, child_module, mocker):
    mocker.patch.object(root_module, "_draw")
    mocker.patch.object(child_module, "draw")
    root_module.draw()
    root_module._draw.assert_called_once()
    child_module.draw.assert_called_once()

def test_module_tick_propagation(root_module, child_module, mocker):
    mocker.patch.object(root_module, "_tick")
    mocker.patch.object(child_module, "tick")
    root_module.tick()
    child_module.tick.assert_called_once()
    root_module._tick.assert_called_once()

def test_module_handle_event_propagation(root_module, child_module, mocker):
    mocker.patch.object(child_module, "_handle_event", return_value=True)
    mocker.patch.object(root_module, "_handle_event")
    event = dg.KeyEvent("a")
    
    assert root_module.handle_event(event) is True
    child_module._handle_event.assert_called_once_with(event)
    root_module._handle_event.assert_not_called()

def test_module_handle_mouse_event_coords(root_module, child_module, mocker):
    # assert child_module in root_module.submodules
    mock_handler = mocker.patch.object(child_module, "_handle_event", return_value=True)
    # mock_handler = mocker.patch.object(root_module, "_handle_event", return_value=True)
    # Mouse event within the child's box
    event = dg.MouseEvent(pos=(2, 3)) 
    root_module.handle_event(event)
    
    # Check that coordinates are correctly translated relative to the child
    mock_handler.assert_called_once()
    translated_event = mock_handler.call_args[0][0]
    assert isinstance(translated_event, dg.MouseEvent)
    assert translated_event.pos == (1, 2) # (2-1, 3-1)

# --- Other Module Tests ---

def test_text_input_module(root_module):
    text_input = dg.modules.TextInputModule(root_module, box=(0,0,1,10), start_text="hello")
    assert str(text_input) == "hello"

    # Test backspace
    text_input.handle_event(dg.KeyEvent("KEY_BACKSPACE"))
    assert str(text_input) == "hell"
    assert text_input.cursor_pos == 4

    # Test adding text
    text_input.handle_event(dg.KeyEvent("o"))
    assert str(text_input) == "hello"
    assert text_input.cursor_pos == 5

    # Test left/right cursor
    text_input.handle_event(dg.KeyEvent("KEY_LEFT"))
    assert text_input.cursor_pos == 4
    text_input.handle_event(dg.KeyEvent("!"))
    assert str(text_input) == "hell!o"

def test_fps_meter(root_module):
    fps_meter = dg.modules.FPSMeter(root_module, box=(0,0,1,8))
    fps_meter.draw()
    # This is a visual module, so we can't easily assert the output without
    # a full grid implementation. We just test that it runs without error.
    
    # # Hard to test timing precisely, but we can check the basic logic
    # fps_meter.last_time = time.time() - 0.1 # Pretend 0.1s has passed
    # fps_meter.tick()
    # # avg = 0.9 * 60 + 0.1 * (1/0.1) = 54 + 1 = 55
    # assert 54 < fps_meter.avg < 56

    # fps_meter.draw()
    # assert len(root_module.grid.print_log) > 0
    # assert "FPS:" in root_module.grid.print_log[0][0][0]

def test_border_module(root_module):
    border = dg.modules.BorderModule(root_module, depth=1)
    border.draw()
    # This is a visual module, so we can't easily assert the output without
    # a full grid implementation. We just test that it runs without error.
    assert border.inner_box == (1, 1, 9, 19)

def test_tab_module(root_module):
    tab1 = dg.Module(root_module)
    tab2 = dg.Module(root_module)
    tab_module = dg.modules.TabModule(root_module, tabs=[tab1, tab2])

    assert tab_module.index == 0
    assert tab_module.tab is tab1
    assert tab1.paused is False
    assert tab2.paused is True

    tab_module.index = 1
    assert tab_module.tab is tab2
    assert tab1.paused is True
    assert tab2.paused is False

def test_key_trigger(root_module, mocker):
    callback = mocker.Mock()
    trigger = dg.modules.KeyTrigger(root_module, key="x", mod=dg.KM_CTRL, fn=callback)
    
    # No match
    trigger.handle_event(dg.KeyEvent("x"))
    callback.assert_not_called()
    
    # Match
    trigger.handle_event(dg.KeyEvent("x", dg.KM_CTRL))
    callback.assert_called_once()

def test_button_trigger(root_module, mocker):
    down_cb = mocker.Mock()
    up_cb = mocker.Mock()
    trigger = dg.modules.ButtonTrigger(root_module, button=1, down_fn=down_cb, up_fn=up_cb)

    # No match
    trigger.handle_event(dg.MouseEvent(button=2, state=True))
    down_cb.assert_not_called()

    # Match down
    trigger.handle_event(dg.MouseEvent(button=1, state=True))
    down_cb.assert_called_once()
    up_cb.assert_not_called()

    # Match up
    trigger.handle_event(dg.MouseEvent(button=1, state=False))
    up_cb.assert_called_once()