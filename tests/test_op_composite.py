"""Unit tests for gfx:composite operation."""

from decimal import Decimal

import pytest
from PIL import Image

from invariant_gfx.anchors import absolute, relative
from invariant_gfx.artifacts import ImageArtifact
from invariant_gfx.ops.composite import composite


class TestComposite:
    """Tests for composite operation."""

    def test_single_layer(self):
        """Test compositing a single layer."""
        bg = ImageArtifact(Image.new("RGBA", (10, 10), (255, 0, 0, 255)))

        layers = [
            {
                "image": bg,
                "id": "bg",
            }
        ]

        result = composite(layers)

        assert isinstance(result, ImageArtifact)
        assert result.width == 10
        assert result.height == 10
        assert result.image.getpixel((0, 0)) == (255, 0, 0, 255)

    def test_two_layer_center(self):
        """Test two-layer composition with centered content."""
        bg = ImageArtifact(Image.new("RGBA", (20, 20), (0, 0, 0, 255)))
        content = ImageArtifact(Image.new("RGBA", (10, 10), (255, 255, 255, 255)))

        layers = [
            {
                "image": bg,
                "id": "bg",
            },
            {
                "image": content,
                "anchor": relative("bg", "c@c"),
                "id": "content",
            },
        ]

        result = composite(layers)

        assert result.width == 20
        assert result.height == 20

        # Center should be white (content)
        assert result.image.getpixel((10, 10)) == (255, 255, 255, 255)
        # Corner should be black (background)
        assert result.image.getpixel((0, 0)) == (0, 0, 0, 255)

    def test_three_layer_with_relative(self):
        """Test three-layer composition with relative positioning."""
        bg = ImageArtifact(Image.new("RGBA", (30, 30), (40, 40, 40, 255)))
        icon = ImageArtifact(Image.new("RGBA", (10, 10), (0, 100, 200, 255)))
        badge = ImageArtifact(Image.new("RGBA", (5, 5), (200, 0, 0, 255)))

        layers = [
            {
                "image": bg,
                "id": "bg",
            },
            {
                "image": icon,
                "anchor": relative("bg", "c@c"),
                "id": "icon",
            },
            {
                "image": badge,
                "anchor": relative("icon", "se@se", x=-2, y=2),
                "id": "badge",
            },
        ]

        result = composite(layers)

        assert result.width == 30
        assert result.height == 30

        # Center should be blue (icon)
        assert result.image.getpixel((15, 15)) == (0, 100, 200, 255)
        # Corner should be dark gray (background)
        assert result.image.getpixel((0, 0)) == (40, 40, 40, 255)

    def test_invalid_layers_type(self):
        """Test that invalid layers type raises ValueError."""
        with pytest.raises(ValueError, match="layers must be a list"):
            composite({"layers": {}})  # type: ignore

    def test_empty_layers(self):
        """Test that empty layers raises ValueError."""
        with pytest.raises(ValueError, match="layers must contain at least one layer"):
            composite([])

    def test_first_layer_with_anchor(self):
        """Test that first layer with anchor raises ValueError."""
        bg = ImageArtifact(Image.new("RGBA", (10, 10), (255, 0, 0, 255)))

        layers = [
            {
                "image": bg,
                "id": "bg",
                "anchor": absolute(0, 0),  # Forbidden on first layer
            }
        ]

        with pytest.raises(
            ValueError, match="First layer must not have an 'anchor' field"
        ):
            composite(layers)

    def test_subsequent_layer_without_anchor(self):
        """Test that subsequent layer without anchor raises ValueError."""
        bg = ImageArtifact(Image.new("RGBA", (10, 10), (255, 0, 0, 255)))
        content = ImageArtifact(Image.new("RGBA", (5, 5), (0, 255, 0, 255)))

        layers = [
            {
                "image": bg,
                "id": "bg",
            },
            {
                "image": content,
                # Missing anchor - should raise error
                "id": "content",
            },
        ]

        with pytest.raises(ValueError, match="Layer 1 must have 'anchor' field"):
            composite(layers)

    def test_missing_image_field(self):
        """Test that missing image field raises ValueError."""
        layers = [
            {
                # Missing image field
                "id": "bg",
            }
        ]

        with pytest.raises(ValueError, match="First layer must have 'image' field"):
            composite(layers)

    def test_opacity(self):
        """Test opacity support."""
        bg = ImageArtifact(Image.new("RGBA", (10, 10), (255, 255, 255, 255)))
        overlay = ImageArtifact(Image.new("RGBA", (10, 10), (0, 0, 0, 255)))

        layers = [
            {
                "image": bg,
                "id": "bg",
            },
            {
                "image": overlay,
                "anchor": relative("bg", "c@c"),
                "id": "overlay",
                "opacity": Decimal("0.5"),
            },
        ]

        result = composite(layers)

        # With 50% opacity black over white, should be gray
        pixel = result.image.getpixel((5, 5))
        # Should be approximately (128, 128, 128, 255) - allow some tolerance
        # Note: Alpha compositing may result in alpha < 255 when layers have opacity
        # The alpha channel reflects the composited opacity
        assert 120 <= pixel[0] <= 135  # R
        assert 120 <= pixel[1] <= 135  # G
        assert 120 <= pixel[2] <= 135  # B
        assert (
            pixel[3] >= 180
        )  # Alpha should be reasonably high (opacity affects alpha channel)

    def test_alignment_variations(self):
        """Test various alignment string formats."""
        bg = ImageArtifact(Image.new("RGBA", (20, 20), (0, 0, 0, 255)))
        content = ImageArtifact(Image.new("RGBA", (10, 10), (255, 255, 255, 255)))

        # Test "e@e" alignment (end to end, right-aligned)
        layers = [
            {
                "image": bg,
                "id": "bg",
            },
            {
                "image": content,
                "anchor": relative("bg", "e@e"),
                "id": "content",
            },
        ]

        result = composite(layers)
        # Content end should align with bg end (20, 20)
        # So content should be at (10, 10) to (20, 20)
        assert result.width == 20
        assert result.height == 20
        # Bottom-right corner should be white
        assert result.image.getpixel((19, 19)) == (255, 255, 255, 255)

    def test_relative_parent_not_found(self):
        """Test that relative() with non-existent parent raises ValueError."""
        bg = ImageArtifact(Image.new("RGBA", (10, 10), (255, 0, 0, 255)))
        content = ImageArtifact(Image.new("RGBA", (5, 5), (0, 255, 0, 255)))

        layers = [
            {
                "image": bg,
                "id": "bg",
            },
            {
                "image": content,
                "anchor": relative("nonexistent", "c@c"),
                "id": "content",
            },
        ]

        with pytest.raises(
            ValueError,
            match="references parent 'nonexistent' which hasn't been placed yet",
        ):
            composite(layers)

    def test_relative_parent_no_id(self):
        """Test that relative() parent must have id field."""
        bg = ImageArtifact(Image.new("RGBA", (10, 10), (255, 0, 0, 255)))
        content = ImageArtifact(Image.new("RGBA", (5, 5), (0, 255, 0, 255)))

        layers = [
            {
                "image": bg,
                # Missing id - can't be referenced
            },
            {
                "image": content,
                "anchor": relative("bg", "c@c"),
                "id": "content",
            },
        ]

        with pytest.raises(
            ValueError, match="references parent 'bg' which hasn't been placed yet"
        ):
            composite(layers)

    def test_alignment_format_at_sign(self):
        """Test that alignment format uses @ separator."""
        bg = ImageArtifact(Image.new("RGBA", (20, 20), (0, 0, 0, 255)))
        content = ImageArtifact(Image.new("RGBA", (10, 10), (255, 255, 255, 255)))

        layers = [
            {
                "image": bg,
                "id": "bg",
            },
            {
                "image": content,
                "anchor": relative("bg", "c@c"),  # @ format
                "id": "content",
            },
        ]

        result = composite(layers)
        assert result.width == 20
        assert result.height == 20
        # Center should be white
        assert result.image.getpixel((10, 10)) == (255, 255, 255, 255)

    def test_alignment_format_invalid(self):
        """Test that invalid alignment format raises ValueError."""
        bg = ImageArtifact(Image.new("RGBA", (20, 20), (0, 0, 0, 255)))
        content = ImageArtifact(Image.new("RGBA", (10, 10), (255, 255, 255, 255)))

        layers = [
            {
                "image": bg,
                "id": "bg",
            },
            {
                "image": content,
                "anchor": relative("bg", "c,c"),  # Old comma format - should fail
                "id": "content",
            },
        ]

        with pytest.raises(ValueError, match="Alignment string must use '@' separator"):
            composite(layers)

    def test_transparent_background_preserves_alpha(self):
        """Semi-transparent layer on transparent background: alpha is preserved (not squared)."""
        bg = ImageArtifact(Image.new("RGBA", (20, 20), (0, 0, 0, 0)))
        # Red with alpha 180; paste-with-mask would give alpha ~ 180^2/255 ~ 127
        overlay = ImageArtifact(Image.new("RGBA", (10, 10), (255, 0, 0, 180)))

        layers = [
            {"image": bg, "id": "bg"},
            {
                "image": overlay,
                "anchor": relative("bg", "c@c"),
                "id": "overlay",
            },
        ]

        result = composite(layers)
        # Center pixel should have alpha 180 (proper alpha_composite), not ~127 (squared)
        center = result.image.getpixel((10, 10))
        assert center[0] == 255
        assert center[1] == 0
        assert center[2] == 0
        assert center[3] == 180

    def test_normal_layer_clips_when_partially_off_canvas(self):
        """Normal alpha compositing should clip layers outside the base canvas."""
        bg = ImageArtifact(Image.new("RGBA", (10, 10), (0, 0, 0, 0)))
        overlay = ImageArtifact(Image.new("RGBA", (5, 5), (255, 0, 0, 180)))

        result = composite(
            [
                {"image": bg, "id": "bg"},
                {"image": overlay, "anchor": absolute(-2, -2), "id": "overlay"},
            ]
        )

        assert result.image.getpixel((0, 0)) == (255, 0, 0, 180)
        assert result.image.getpixel((2, 2)) == (255, 0, 0, 180)
        assert result.image.getpixel((3, 3)) == (0, 0, 0, 0)

    def test_blend_mode_multiply(self):
        """Multiply darkens: white * gray = gray, black * anything = black."""
        bg = ImageArtifact(Image.new("RGBA", (10, 10), (255, 255, 255, 255)))
        overlay = ImageArtifact(Image.new("RGBA", (10, 10), (128, 128, 128, 255)))

        layers = [
            {"image": bg, "id": "bg"},
            {
                "image": overlay,
                "anchor": relative("bg", "c@c"),
                "id": "overlay",
                "mode": "multiply",
            },
        ]

        result = composite(layers)
        center = result.image.getpixel((5, 5))
        # 255 * 128 / 255 = 128
        assert center[0] == 128
        assert center[1] == 128
        assert center[2] == 128
        assert center[3] == 255

    def test_blend_mode_screen(self):
        """Screen lightens: black stays black, white stays white, mid tones lighten."""
        bg = ImageArtifact(Image.new("RGBA", (10, 10), (64, 64, 64, 255)))
        overlay = ImageArtifact(Image.new("RGBA", (10, 10), (64, 64, 64, 255)))

        layers = [
            {"image": bg, "id": "bg"},
            {
                "image": overlay,
                "anchor": relative("bg", "c@c"),
                "id": "overlay",
                "mode": "screen",
            },
        ]

        result = composite(layers)
        center = result.image.getpixel((5, 5))
        # screen: 1 - (1-64/255)^2 = 1 - (191/255)^2 ~ 0.44 -> ~112
        assert center[0] >= 100
        assert center[0] <= 130
        assert center[1] == center[0]
        assert center[2] == center[0]

    def test_blend_mode_add(self):
        """Add brightens: values sum and saturate at 255."""
        bg = ImageArtifact(Image.new("RGBA", (10, 10), (100, 100, 100, 255)))
        overlay = ImageArtifact(Image.new("RGBA", (10, 10), (100, 100, 100, 255)))

        layers = [
            {"image": bg, "id": "bg"},
            {
                "image": overlay,
                "anchor": relative("bg", "c@c"),
                "id": "overlay",
                "mode": "add",
            },
        ]

        result = composite(layers)
        center = result.image.getpixel((5, 5))
        # add: min(1, 100/255 + 100/255) = 200/255 -> ~200
        assert center[0] >= 195
        assert center[0] <= 205
        assert center[1] == center[0]
        assert center[2] == center[0]

    def test_blend_mode_unknown_raises(self):
        """Unknown blend mode raises ValueError."""
        bg = ImageArtifact(Image.new("RGBA", (10, 10), (255, 255, 255, 255)))
        overlay = ImageArtifact(Image.new("RGBA", (10, 10), (0, 0, 0, 255)))

        layers = [
            {"image": bg, "id": "bg"},
            {
                "image": overlay,
                "anchor": relative("bg", "c@c"),
                "id": "overlay",
                "mode": "invalid_mode",
            },
        ]

        with pytest.raises(ValueError, match="Unknown blend mode"):
            composite(layers)
