"""Pytest fixtures for pyxel-ui tests."""
import pyxel
import pytest


@pytest.fixture(autouse=True, scope="session")
def init_pyxel():
    """Initialize Pyxel once for all tests (headless)."""
    pyxel.init(256, 256, title="test", display_scale=1)
    yield
