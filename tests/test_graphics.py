"""Tests for the graphics.py module."""

import os
import tempfile
import numpy as np
import pytest

import display_grid as dg

@pytest.fixture
def graphics_dir():
    """Creates a temporary directory with a sample graphic file for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        asset_path = os.path.join(tmpdir, "test_asset.txt")
        with open(asset_path, "w") as f:
            f.write("AB \nC D")
        yield tmpdir

def test_load_graphics(graphics_dir):
    """Tests that load_graphics correctly loads a graphic from a file."""
    # Clear any previously loaded graphics
    dg.graphics.GRAPHICS.clear()

    dg.load_graphics(graphics_dir + "/")
    
    assert "test_asset" in dg.GRAPHICS
    graphic = dg.GRAPHICS["test_asset"]
    
    assert isinstance(graphic, np.ndarray)
    expected_array = np.array([
        [ord("A"), ord("B"), ord(" ")],
        [ord("C"), ord(" "), ord("D")],
    ], dtype=np.int32)
    
    assert np.array_equal(graphic, expected_array)

def test_load_graphics_empty_dir():
    """Tests that load_graphics handles an empty directory gracefully."""
    dg.graphics.GRAPHICS.clear()
    with tempfile.TemporaryDirectory() as tmpdir:
        dg.load_graphics(tmpdir + "/")
        assert len(dg.GRAPHICS) == 0

def test_load_graphics_no_txt_files():
    """Tests that load_graphics ignores non-.txt files."""
    dg.graphics.GRAPHICS.clear()
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, "test.dat"), "w") as f:
            f.write("data")
        dg.load_graphics(tmpdir + "/")
        assert len(dg.GRAPHICS) == 0
