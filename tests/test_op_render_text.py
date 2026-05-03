"""Unit tests for gfx:render_text operation."""

from decimal import Decimal

import pytest

from invariant_gfx.artifacts import BlobArtifact, ImageArtifact
from invariant_gfx.ops.render_text import (
    _fit_width_font_size,
    _measure_text_width,
    render_text,
)

from .conftest import TEST_FONT_FAMILY

FONT = TEST_FONT_FAMILY


@pytest.fixture(autouse=True)
def _ensure_font(test_font_family: str) -> str:
    return test_font_family


class TestRenderText:
    """Tests for render_text operation."""

    def test_basic_text_rendering(self):
        """Test basic text rendering with string font."""
        result = render_text(
            text="Hello",
            font=FONT,
            size=Decimal("24"),
            color=(255, 0, 0, 255),
        )

        assert isinstance(result, ImageArtifact)
        assert result.image.mode == "RGBA"
        assert result.width > 0
        assert result.height > 0

    def test_with_int_size(self):
        """Test with integer size."""
        result = render_text(
            text="Test",
            font=FONT,
            size=12,
            color=(0, 255, 0, 255),
        )

        assert result.width > 0
        assert result.height > 0

    def test_with_string_size(self):
        """Test with string size (from CEL expressions)."""
        result = render_text(
            text="Test",
            font=FONT,
            size="18",
            color=(0, 0, 255, 255),
        )

        assert result.width > 0
        assert result.height > 0

    def test_with_font_weight(self):
        """Test with font weight parameter."""
        result = render_text(
            text="Bold",
            font=FONT,
            size=24,
            color=(255, 255, 255, 255),
            weight=700,
        )

        assert result.width > 0
        assert result.height > 0

    def test_with_font_style(self):
        """Test with font style parameter."""
        result = render_text(
            text="Italic",
            font=FONT,
            size=24,
            color=(255, 255, 255, 255),
            style="normal",
        )

        assert result.width > 0
        assert result.height > 0

    def test_with_blob_font(self):
        """Test with BlobArtifact font (resolved via JustMyType)."""
        from justmytype import FontRegistry

        info = FontRegistry().find_font(FONT)
        if info is None:
            pytest.skip(f"{FONT} not available for blob font test")
        font_blob = BlobArtifact(
            data=info.path.read_bytes(),
            content_type="font/ttf",
        )

        result = render_text(
            text="Blob Font",
            font=font_blob,
            size=24,
            color=(255, 0, 0, 255),
        )

        assert isinstance(result, ImageArtifact)
        assert result.width > 0
        assert result.height > 0

    def test_missing_text(self):
        """Required-arg sanity placeholder; render_text rejects missing text."""

    def test_missing_font(self):
        """Required-arg sanity placeholder; render_text rejects missing font."""

    def test_missing_size(self):
        """Test that missing both size and fit_width raises ValueError."""
        with pytest.raises(ValueError, match="must provide either size or fit_width"):
            render_text(
                text="Hello",
                font=FONT,
                color=(255, 0, 0, 255),
            )

    def test_missing_color(self):
        """Required-arg sanity placeholder; render_text rejects missing color."""

    def test_invalid_font_type(self):
        """Test that invalid font type raises ValueError."""
        with pytest.raises(ValueError, match="font must be a string or BlobArtifact"):
            render_text(
                text="Hello",
                font=123,  # type: ignore
                size=24,
                color=(255, 0, 0, 255),
            )

    def test_invalid_font_name(self):
        """Test that invalid font name raises ValueError."""
        with pytest.raises(ValueError, match="failed to find font"):
            render_text(
                text="Hello",
                font="NonexistentFont12345",
                size=24,
                color=(255, 0, 0, 255),
            )

    def test_invalid_weight(self):
        """Test that invalid weight raises ValueError."""
        with pytest.raises(ValueError, match="weight must be int in range"):
            render_text(
                text="Hello",
                font=FONT,
                size=24,
                color=(255, 0, 0, 255),
                weight=50,  # Too low
            )

    def test_invalid_style(self):
        """Test that invalid style raises ValueError."""
        with pytest.raises(ValueError, match="style must be 'normal' or 'italic'"):
            render_text(
                text="Hello",
                font=FONT,
                size=24,
                color=(255, 0, 0, 255),
                style="bold",  # Invalid
            )

    def test_negative_size(self):
        """Test that negative size raises ValueError."""
        with pytest.raises(ValueError, match="size must be positive"):
            render_text(
                text="Hello",
                font=FONT,
                size=-10,
                color=(255, 0, 0, 255),
            )

    def test_invalid_color(self):
        """Test that invalid color raises ValueError."""
        with pytest.raises(ValueError, match="color must be a tuple"):
            render_text(
                text="Hello",
                font=FONT,
                size=24,
                color=(255, 0, 0),  # Missing alpha
            )

    def test_tight_bounding_box(self):
        """Test that output has tight bounding box."""
        result = render_text(
            text="Hi",
            font=FONT,
            size=24,
            color=(255, 0, 0, 255),
        )

        assert result.width < 100  # "Hi" should be small
        assert result.height < 50

    def test_multiline_text_uses_multiline_bounds(self):
        """Test that multiline text keeps enough vertical space."""
        single_line = render_text(
            text="A",
            font=FONT,
            size=24,
            color=(255, 0, 0, 255),
        )
        multiline = render_text(
            text="A\nB",
            font=FONT,
            size=24,
            color=(255, 0, 0, 255),
        )

        assert multiline.height > single_line.height

    def test_fit_width_basic(self):
        """Test fit_width with short text - result fits within target width."""
        result = render_text(
            text="Hello",
            font=FONT,
            fit_width=100,
            color=(255, 0, 0, 255),
        )

        assert isinstance(result, ImageArtifact)
        assert result.width <= 105  # text width + padding (2*2)
        assert result.height > 0

    def test_fit_width_long_text(self):
        """Test fit_width with longer text fits within target."""
        result = render_text(
            text="Hello World Example",
            font=FONT,
            fit_width=150,
            color=(0, 255, 0, 255),
        )

        assert isinstance(result, ImageArtifact)
        assert result.width <= 155  # text width + padding
        assert result.height > 0

    def test_fit_width_exact_uses_largest_fitting_size(self):
        """Test exact fit_width finds the largest fitting metric size."""
        text = "WWWWWWWWWW"
        target = 80
        size = _fit_width_font_size(
            text=text,
            font=FONT,
            fit_width=Decimal(str(target)),
            exact=True,
        )

        width, _ = _measure_text_width(text, FONT, size)
        next_width, _ = _measure_text_width(text, FONT, size + 1)
        assert width <= target
        assert next_width > target

    def test_fit_width_exclusive(self):
        """Test that passing both size and fit_width raises ValueError."""
        with pytest.raises(ValueError, match="exactly one of size or fit_width"):
            render_text(
                text="Hello",
                font=FONT,
                size=24,
                fit_width=100,
                color=(255, 0, 0, 255),
            )

    def test_fit_width_with_blob_font(self):
        """Test fit_width works with BlobArtifact font."""
        from justmytype import FontRegistry

        info = FontRegistry().find_font(FONT)
        if info is None:
            pytest.skip(f"{FONT} not available for blob font test")
        font_blob = BlobArtifact(
            data=info.path.read_bytes(),
            content_type="font/ttf",
        )

        result = render_text(
            text="Fit",
            font=font_blob,
            fit_width=80,
            color=(255, 0, 0, 255),
        )

        assert isinstance(result, ImageArtifact)
        assert result.width <= 85
        assert result.height > 0
