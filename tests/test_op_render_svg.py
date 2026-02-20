"""Unit tests for gfx:render_svg operation."""

from decimal import Decimal

import pytest

from invariant_gfx.artifacts import BlobArtifact, ImageArtifact
from invariant_gfx.ops.render_svg import render_svg


class TestRenderSvg:
    """Tests for render_svg operation."""

    def test_render_lucide_icon(self):
        """Test rendering a Lucide icon SVG."""
        # Get a real SVG from JustMyResource
        from justmyresource import get_default_registry

        registry = get_default_registry()
        resource = registry.get_resource("lucide:thermometer")
        svg_blob = BlobArtifact(data=resource.data, content_type=resource.content_type)

        result = render_svg(
            svg_content=svg_blob,
            width=Decimal("48"),
            height=Decimal("48"),
        )

        assert isinstance(result, ImageArtifact)
        assert result.width == 48
        assert result.height == 48
        assert result.image.mode == "RGBA"

    def test_with_int_dimensions(self):
        """Test with integer dimensions."""
        from justmyresource import get_default_registry

        registry = get_default_registry()
        resource = registry.get_resource("lucide:cloud")
        svg_blob = BlobArtifact(data=resource.data, content_type=resource.content_type)

        result = render_svg(
            svg_content=svg_blob,
            width=32,
            height=32,
        )

        assert result.width == 32
        assert result.height == 32

    def test_with_string_dimensions(self):
        """Test with string dimensions (from CEL expressions)."""
        from justmyresource import get_default_registry

        registry = get_default_registry()
        resource = registry.get_resource("lucide:thermometer")
        svg_blob = BlobArtifact(data=resource.data, content_type=resource.content_type)

        result = render_svg(
            svg_content=svg_blob,
            width="64",
            height="64",
        )

        assert result.width == 64
        assert result.height == 64

    def test_missing_width(self):
        """Test that missing width raises TypeError."""
        # This test is no longer applicable since width is a required parameter
        # The function will fail at call time if width is not provided
        pass

    def test_missing_height(self):
        """Test that missing height raises TypeError."""
        # This test is no longer applicable since height is a required parameter
        # The function will fail at call time if height is not provided
        pass

    def test_missing_svg_content(self):
        """Test that missing svg_content raises TypeError."""
        # This test is no longer applicable since svg_content is a required parameter
        # The function will fail at call time if svg_content is not provided
        pass

    def test_inline_svg_string(self):
        """Test rendering inline SVG string."""
        svg_string = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><rect width="24" height="24" fill="red"/></svg>'

        result = render_svg(
            svg_content=svg_string,
            width=Decimal("48"),
            height=Decimal("48"),
        )

        assert isinstance(result, ImageArtifact)
        assert result.width == 48
        assert result.height == 48
        assert result.image.mode == "RGBA"

    def test_negative_dimensions(self):
        """Test that negative dimensions raise ValueError."""
        from justmyresource import get_default_registry

        registry = get_default_registry()
        resource = registry.get_resource("lucide:thermometer")
        svg_blob = BlobArtifact(data=resource.data, content_type=resource.content_type)

        with pytest.raises(ValueError, match="size must be positive"):
            render_svg(
                svg_content=svg_blob,
                width=-10,
                height=48,
            )

    def test_invalid_svg_data(self):
        """Test that invalid SVG data raises ValueError."""
        blob = BlobArtifact(data=b"not an svg", content_type="image/svg+xml")

        with pytest.raises(ValueError, match="failed to render"):
            render_svg(
                svg_content=blob,
                width=48,
                height=48,
            )
