"""Unit tests for example scripts.

These tests ensure that the example scripts continue to work correctly
when code changes are made to the invariant-gfx package. Tests execute the
scripts as external Python processes using subprocess for accurate testing.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest
from invariant import load_value_from_jsonable
from invariant_gfx.artifacts import ImageArtifact
from PIL import Image, ImageChops

# Get the project root directory (parent of tests/)
PROJECT_ROOT = Path(__file__).parent.parent
EXAMPLES_DIR = PROJECT_ROOT / "examples"
SERIALIZED_EXAMPLES_DIR = EXAMPLES_DIR / "serialized"


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


class TestShapesShowcaseExample:
    """Tests for examples/shapes_showcase.py."""

    @pytest.fixture
    def script_path(self):
        """Return the path to the shapes showcase example script."""
        return EXAMPLES_DIR / "shapes_showcase.py"

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
        assert "shapes_showcase" in output
        assert result.returncode == 0

    def test_custom_cell_size(self, script_path):
        """Test example with custom cell size."""
        result = subprocess.run(
            [
                sys.executable,
                str(script_path),
                "--cell-size",
                "56",
                "--output",
                "output/shapes_test.png",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        output = result.stdout
        assert "✓ Saved to:" in output
        assert "56x56" in output
        assert result.returncode == 0


class TestEffectsShowcaseExample:
    """Tests for examples/effects_showcase.py."""

    @pytest.fixture
    def script_path(self):
        """Return the path to the effects showcase example script."""
        return EXAMPLES_DIR / "effects_showcase.py"

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
        assert "effects_showcase" in output
        assert result.returncode == 0

    def test_custom_cell_size(self, script_path):
        """Test example with custom cell size."""
        result = subprocess.run(
            [
                sys.executable,
                str(script_path),
                "--cell-size",
                "56",
                "--output",
                "output/effects_test.png",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        output = result.stdout
        assert "✓ Saved to:" in output
        assert "56x56" in output
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


class TestSerializedExamples:
    """Tests for serialized graph examples."""

    def test_square_button_badge_executes_with_cli(self):
        """Serialized square badge renders a centered fit-width label."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "invariant",
                str(SERIALIZED_EXAMPLES_DIR / "square_button_badge.json"),
                "--param",
                "text=null",
                "--param",
                "color=null",
                "--param",
                "width=null",
                "--param",
                "height=null",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        artifact = load_value_from_jsonable(json.loads(result.stdout))

        assert isinstance(artifact, ImageArtifact)
        assert artifact.width == 144
        assert artifact.height == 144

        background = Image.new("RGB", (144, 144), (30, 41, 59))
        changed = ImageChops.difference(
            artifact.image.convert("RGB"), background
        ).getbbox()
        assert changed is not None

        center_x = (changed[0] + changed[2]) / 2
        center_y = (changed[1] + changed[3]) / 2
        assert abs(center_x - 72) <= 4
        assert abs(center_y - 72) <= 4
        assert changed[2] - changed[0] <= 104

    def test_square_button_badge_output_file_is_png(self, tmp_path: Path):
        """Serialized square badge can be parameterized and saved as a PNG."""
        output_path = tmp_path / "button.png"
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "invariant",
                str(SERIALIZED_EXAMPLES_DIR / "square_button_badge.json"),
                "--param",
                "text=My Button",
                "--param",
                "color=#FF0000",
                "--param",
                "width=144",
                "--param",
                "height=72",
                "--output",
                str(output_path),
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        assert result.stdout == ""
        assert result.stderr == ""
        assert output_path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")

        with Image.open(output_path) as image:
            assert image.size == (144, 72)
            assert image.mode == "RGBA"
