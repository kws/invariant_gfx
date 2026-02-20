"""gfx:resolve_resource operation - resolves bundled resources via JustMyResource."""

from justmyresource import get_default_registry

from invariant.protocol import ICacheable
from invariant_gfx.artifacts import BlobArtifact


def resolve_resource(name: str) -> ICacheable:
    """Resolve bundled resources (icons, images) via JustMyResource.

    Args:
        name: String resource identifier with optional pack prefix
              (e.g., "lucide:thermometer", "material-icons:cloud")

    Returns:
        BlobArtifact containing the resource bytes.

    Raises:
        ValueError: If name is not a string or resource cannot be found.
    """
    if not isinstance(name, str):
        raise ValueError(f"name must be a string, got {type(name)}")

    # Get resource from JustMyResource
    registry = get_default_registry()
    try:
        resource = registry.get_resource(name)
    except Exception as e:
        raise ValueError(
            f"gfx:resolve_resource failed to find resource '{name}': {e}"
        ) from e

    # Convert to BlobArtifact
    return BlobArtifact(data=resource.data, content_type=resource.content_type)
