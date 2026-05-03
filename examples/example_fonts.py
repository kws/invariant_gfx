"""Helpers for example scripts to pick a font that JustMyType can resolve.

Examples ship with no font assumption baked into ``invariant-gfx`` itself.
Install the optional font pack to run them out of the box::

    pip install 'invariant-gfx[fonts]'

The candidate families below are bundled by ``justmytype-western-core``,
which is what the ``fonts`` extra (and the ``dev`` group) installs.
"""

from __future__ import annotations

import sys

from justmytype import FontRegistry

PREFERRED_FAMILIES: tuple[str, ...] = ("Inter", "Noto Sans")

INSTALL_HINT = (
    "No usable font family was found for the example.\n"
    "Install the optional font pack:\n"
    "    pip install 'invariant-gfx[fonts]'\n"
    "or pass --font with the name of a font installed on this system."
)


def resolve_example_font(requested: str | None = None) -> str:
    """Return a font family name JustMyType can resolve.

    When ``requested`` is given the function only verifies it is resolvable.
    Otherwise the first match from :data:`PREFERRED_FAMILIES` wins.
    Exits with a non-zero status and an install hint when nothing matches.
    """
    registry = FontRegistry()

    if requested:
        if registry.find_font(requested) is None:
            sys.stderr.write(
                f"Font {requested!r} is not available on this system.\n"
                + INSTALL_HINT
                + "\n"
            )
            raise SystemExit(2)
        return requested

    for family in PREFERRED_FAMILIES:
        if registry.find_font(family) is not None:
            return family

    sys.stderr.write(INSTALL_HINT + "\n")
    raise SystemExit(2)
