"""Unit tests for example scripts.

These tests ensure that the example scripts continue to work correctly
when code changes are made to the invariant_gfx package. Tests execute the
scripts as external Python processes using subprocess for accurate testing.
"""

import subprocess
import sys
from pathlib import Path

import pytest

# Get the project root directory (parent of tests/)
PROJECT_ROOT = Path(__file__).parent.parent
EXAMPLES_DIR = PROJECT_ROOT / "examples"


class TestQuickStartExample:
    """Tests for examples/quick_start.py."""

    @pytest.fixture
    def script_path(self):
        """Return the path to the quick start example script."""
        return EXAMPLES_DIR / "quick_start.py"

    def test_default_arguments(self, script_path):
        """Test example with default arguments."""
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            check=True,
        )

        output = result.stdout
        assert "Generating image..." in output
        assert "Size: 72x72" in output
        assert "✓ Saved to:" in output
        assert result.returncode == 0

    def test_custom_size(self, script_path):
        """Test example with custom size."""
        result = subprocess.run(
            [sys.executable, str(script_path), "--size", "144"],
            capture_output=True,
            text=True,
            check=True,
        )

        output = result.stdout
        assert "Size: 144x144" in output
        assert "✓ Saved to:" in output
        assert result.returncode == 0


class TestTextBadgeExample:
    """Tests for examples/text_badge.py."""

    @pytest.fixture
    def script_path(self):
        """Return the path to the text badge example script."""
        return EXAMPLES_DIR / "text_badge.py"

    def test_default_arguments(self, script_path):
        """Test example with default arguments."""
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            check=True,
        )

        output = result.stdout
        assert "✓ Saved to:" in output
        assert result.returncode == 0

    def test_custom_text(self, script_path):
        """Test example with custom text."""
        result = subprocess.run(
            [sys.executable, str(script_path), "--text", "Hello"],
            capture_output=True,
            text=True,
            check=True,
        )

        output = result.stdout
        assert "✓ Saved to:" in output
        assert result.returncode == 0


class TestColorDashboardExample:
    """Tests for examples/color_dashboard.py."""

    @pytest.fixture
    def script_path(self):
        """Return the path to the color dashboard example script."""
        return EXAMPLES_DIR / "color_dashboard.py"

    def test_default_arguments(self, script_path):
        """Test example with default arguments."""
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            check=True,
        )

        output = result.stdout
        assert "✓ Saved to:" in output
        assert result.returncode == 0

    def test_custom_items(self, script_path):
        """Test example with custom items."""
        result = subprocess.run(
            [
                sys.executable,
                str(script_path),
                "--items",
                "CPU:75:red,MEM:42:green",
                "--cell-size",
                "80",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        output = result.stdout
        assert "✓ Saved to:" in output
        assert result.returncode == 0


class TestThermometerButtonExample:
    """Tests for examples/thermometer_button.py."""

    @pytest.fixture
    def script_path(self):
        """Return the path to the thermometer button example script."""
        return EXAMPLES_DIR / "thermometer_button.py"

    def test_default_arguments(self, script_path):
        """Test example with default arguments."""
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            check=True,
        )

        output = result.stdout
        assert "✓ Saved to:" in output
        assert result.returncode == 0

    def test_custom_arguments(self, script_path):
        """Test example with custom arguments."""
        result = subprocess.run(
            [
                sys.executable,
                str(script_path),
                "--size",
                "72",
                "--temperature",
                "22.5C",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        output = result.stdout
        assert "✓ Saved to:" in output
        assert result.returncode == 0
