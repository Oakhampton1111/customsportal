"""
Basic test to verify pytest configuration works.
"""

import pytest


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


class TestBasicClass:
    """Test class to verify class-based tests work."""
    
    def test_class_method(self):
        """Test method in a class."""
        assert len("test") == 4
    
    def test_another_method(self):
        """Another test method."""
        assert isinstance([], list)