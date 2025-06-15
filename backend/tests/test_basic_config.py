"""
Basic test to verify pytest configuration works without complex imports.
"""

import pytest
import os


def test_basic_functionality():
    """Test that basic pytest functionality works."""
    assert True


def test_basic_math():
    """Test basic mathematical operations."""
    assert 1 + 1 == 2
    assert 2 * 3 == 6


@pytest.mark.unit
def test_with_unit_marker():
    """Test that unit marker works."""
    assert "hello" == "hello"


def test_environment_setup():
    """Test that we can set environment variables for testing."""
    # Set a test environment variable
    os.environ["TEST_VAR"] = "test_value"
    assert os.environ.get("TEST_VAR") == "test_value"
    
    # Clean up
    del os.environ["TEST_VAR"]


class TestBasicClass:
    """Test class to verify class-based tests work."""
    
    def test_class_method(self):
        """Test method in a class."""
        assert len("test") == 4
    
    def test_another_method(self):
        """Another test method."""
        assert isinstance([], list)


def test_pytest_ini_configuration():
    """Test that pytest.ini configuration is being read."""
    # This test verifies that pytest is reading our configuration
    # by checking if we can use the markers we defined
    assert True  # If this runs, pytest.ini is working


@pytest.mark.slow
def test_slow_marker():
    """Test that slow marker works."""
    import time
    time.sleep(0.01)  # Very short sleep to simulate slow test
    assert True