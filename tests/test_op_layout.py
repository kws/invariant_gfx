"""Unit tests for gfx:layout operation."""

from decimal import Decimal

import pytest
from PIL import Image

from invariant_gfx.artifacts import ImageArtifact
from invariant_gfx.ops.layout import layout


class TestLayout:
    """Tests for layout operation."""

    def test_row_layout_basic(self):
        """Test basic row layout."""
        item1 = ImageArtifact(Image.new("RGBA", (10, 20), (255, 0, 0, 255)))
        item2 = ImageArtifact(Image.new("RGBA", (15, 25), (0, 255, 0, 255)))

        result = layout("row", "c", Decimal("5"), [item1, item2])

        assert isinstance(result, ImageArtifact)
        # Width = 10 + 5 + 15 = 30
        assert result.width == 30
        # Height = max(20, 25) = 25
        assert result.height == 25

    def test_column_layout_basic(self):
        """Test basic column layout."""
        item1 = ImageArtifact(Image.new("RGBA", (20, 10), (255, 0, 0, 255)))
        item2 = ImageArtifact(Image.new("RGBA", (25, 15), (0, 255, 0, 255)))

        result = layout("column", "c", Decimal("5"), [item1, item2])

        # Width = max(20, 25) = 25
        assert result.width == 25
        # Height = 10 + 5 + 15 = 30
        assert result.height == 30

    def test_row_align_start(self):
        """Test row layout with start alignment."""
        item1 = ImageArtifact(Image.new("RGBA", (10, 20), (255, 0, 0, 255)))
        item2 = ImageArtifact(Image.new("RGBA", (10, 10), (0, 255, 0, 255)))

        result = layout("row", "s", Decimal("0"), [item1, item2])

        # Both items should be at y=0 (start)
        assert result.height == 20  # max height

    def test_row_align_end(self):
        """Test row layout with end alignment."""
        item1 = ImageArtifact(Image.new("RGBA", (10, 10), (255, 0, 0, 255)))
        item2 = ImageArtifact(Image.new("RGBA", (10, 20), (0, 255, 0, 255)))

        result = layout("row", "e", Decimal("0"), [item1, item2])

        # item1 should be at bottom (y = 20 - 10 = 10)
        assert result.height == 20

    def test_column_align_start(self):
        """Test column layout with start alignment."""
        item1 = ImageArtifact(Image.new("RGBA", (20, 10), (255, 0, 0, 255)))
        item2 = ImageArtifact(Image.new("RGBA", (10, 10), (0, 255, 0, 255)))

        result = layout("column", "s", Decimal("0"), [item1, item2])

        # Both items should be at x=0 (start)
        assert result.width == 20  # max width

    def test_column_align_end(self):
        """Test column layout with end alignment."""
        item1 = ImageArtifact(Image.new("RGBA", (10, 10), (255, 0, 0, 255)))
        item2 = ImageArtifact(Image.new("RGBA", (20, 10), (0, 255, 0, 255)))

        result = layout("column", "e", Decimal("0"), [item1, item2])

        # item1 should be at right (x = 20 - 10 = 10)
        assert result.width == 20

    def test_with_int_gap(self):
        """Test with integer gap."""
        item1 = ImageArtifact(Image.new("RGBA", (10, 10), (255, 0, 0, 255)))
        item2 = ImageArtifact(Image.new("RGBA", (10, 10), (0, 255, 0, 255)))

        result = layout("row", "c", 10, [item1, item2])

        # Width = 10 + 10 + 10 = 30
        assert result.width == 30

    def test_with_string_gap(self):
        """Test with string gap (from CEL expressions)."""
        item1 = ImageArtifact(Image.new("RGBA", (10, 10), (255, 0, 0, 255)))
        item2 = ImageArtifact(Image.new("RGBA", (10, 10), (0, 255, 0, 255)))

        result = layout("row", "c", "15", [item1, item2])

        # Width = 10 + 15 + 10 = 35
        assert result.width == 35

    def test_zero_gap(self):
        """Test with zero gap."""
        item1 = ImageArtifact(Image.new("RGBA", (10, 10), (255, 0, 0, 255)))
        item2 = ImageArtifact(Image.new("RGBA", (10, 10), (0, 255, 0, 255)))

        result = layout("row", "c", Decimal("0"), [item1, item2])

        # Width = 10 + 0 + 10 = 20
        assert result.width == 20

    def test_three_items(self):
        """Test layout with three items."""
        item1 = ImageArtifact(Image.new("RGBA", (10, 10), (255, 0, 0, 255)))
        item2 = ImageArtifact(Image.new("RGBA", (10, 10), (0, 255, 0, 255)))
        item3 = ImageArtifact(Image.new("RGBA", (10, 10), (0, 0, 255, 255)))

        result = layout("row", "c", Decimal("5"), [item1, item2, item3])

        # Width = 10 + 5 + 10 + 5 + 10 = 40
        assert result.width == 40

    def test_invalid_direction(self):
        """Test that invalid direction raises ValueError."""
        item1 = ImageArtifact(Image.new("RGBA", (10, 10), (255, 0, 0, 255)))

        with pytest.raises(ValueError, match="direction must be 'row' or 'column'"):
            layout("diagonal", "c", Decimal("5"), [item1])

    def test_invalid_align(self):
        """Test that invalid align raises ValueError."""
        item1 = ImageArtifact(Image.new("RGBA", (10, 10), (255, 0, 0, 255)))

        with pytest.raises(ValueError, match="align must be 's', 'c', or 'e'"):
            layout("row", "x", Decimal("5"), [item1])

    def test_empty_items(self):
        """Test that empty items raises ValueError."""
        with pytest.raises(ValueError, match="items must contain at least one item"):
            layout("row", "c", Decimal("5"), [])

    def test_negative_gap(self):
        """Test that negative gap raises ValueError."""
        item1 = ImageArtifact(Image.new("RGBA", (10, 10), (255, 0, 0, 255)))

        with pytest.raises(ValueError, match="gap must be non-negative"):
            layout("row", "c", Decimal("-5"), [item1])

    def test_invalid_items_type(self):
        """Test that non-list items raises ValueError."""
        item1 = ImageArtifact(Image.new("RGBA", (10, 10), (255, 0, 0, 255)))

        with pytest.raises(ValueError, match="items must be a list"):
            layout("row", "c", Decimal("5"), item1)  # type: ignore

    def test_non_image_artifact_item(self):
        """Test that non-ImageArtifact item raises ValueError."""
        with pytest.raises(ValueError, match="items\\[0\\] must be ImageArtifact"):
            layout("row", "c", Decimal("5"), ["not an artifact"])  # type: ignore

    def test_invalid_gap_type(self):
        """Test that invalid gap type raises ValueError."""
        item1 = ImageArtifact(Image.new("RGBA", (10, 10), (255, 0, 0, 255)))

        with pytest.raises(ValueError, match="gap must be Decimal, int, or str"):
            layout("row", "c", 3.14, [item1])  # type: ignore
