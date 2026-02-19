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

        manifest = {
            "svg_content": svg_blob,
            "width": Decimal("48"),
            "height": Decimal("48"),
        }

        result = render_svg(manifest)

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

        manifest = {
            "svg": svg_blob,
            "width": 32,
            "height": 32,
        }

        result = render_svg(manifest)

        assert result.width == 32
        assert result.height == 32

    def test_with_string_dimensions(self):
        """Test with string dimensions (from CEL expressions)."""
        from justmyresource import get_default_registry

        registry = get_default_registry()
        resource = registry.get_resource("lucide:thermometer")
        svg_blob = BlobArtifact(data=resource.data, content_type=resource.content_type)

        manifest = {
            "svg": svg_blob,
            "width": "64",
            "height": "64",
        }

        result = render_svg(manifest)

        assert result.width == 64
        assert result.height == 64

    def test_missing_width(self):
        """Test that missing width raises KeyError."""
        from justmyresource import get_default_registry

        registry = get_default_registry()
        resource = registry.get_resource("lucide:thermometer")
        svg_blob = BlobArtifact(data=resource.data, content_type=resource.content_type)

        manifest = {
            "svg": svg_blob,
            "height": 48,
        }

        with pytest.raises(KeyError, match="width"):
            render_svg(manifest)

    def test_missing_height(self):
        """Test that missing height raises KeyError."""
        from justmyresource import get_default_registry

        registry = get_default_registry()
        resource = registry.get_resource("lucide:thermometer")
        svg_blob = BlobArtifact(data=resource.data, content_type=resource.content_type)

        manifest = {
            "svg": svg_blob,
            "width": 48,
        }

        with pytest.raises(KeyError, match="height"):
            render_svg(manifest)

    def test_missing_svg_content(self):
        """Test that missing svg_content raises KeyError."""
        manifest = {
            "width": 48,
            "height": 48,
        }

        with pytest.raises(KeyError, match="svg_content"):
            render_svg(manifest)

    def test_inline_svg_string(self):
        """Test rendering inline SVG string."""
        svg_string = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><rect width="24" height="24" fill="red"/></svg>'

        manifest = {
            "svg_content": svg_string,
            "width": Decimal("48"),
            "height": Decimal("48"),
        }

        result = render_svg(manifest)

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

        manifest = {
            "svg": svg_blob,
            "width": -10,
            "height": 48,
        }

        with pytest.raises(ValueError, match="size must be positive"):
            render_svg(manifest)

    def test_invalid_svg_data(self):
        """Test that invalid SVG data raises ValueError."""
        blob = BlobArtifact(data=b"not an svg", content_type="image/svg+xml")

        manifest = {
            "svg_content": blob,
            "width": 48,
            "height": 48,
        }

        with pytest.raises(ValueError, match="failed to render"):
            render_svg(manifest)
