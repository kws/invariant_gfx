# Cut an `invariant-gfx` release

Follow the full normative checklist in @AGENTS.md (section **Release process**). Use when shipping a new semver for this package (for example `0.2.0`) or adjusting that workflow.

## What to do

1. Run **`uv run pytest tests/`** and fix failures before changing versions.
2. Confirm **`invariant-core`** on PyPI (and `pyproject.toml` `invariant-core>=…`) supports what this release needs; release the parent engine first if GFX depends on unreleased Invariant changes.
3. Set **`[project].version`** in `pyproject.toml` to the **stable** release (no `.dev` suffix).
4. Run **`uv lock --refresh`** and confirm `uv.lock` lists the same version on the **`invariant-gfx`** workspace package stanza.
5. Commit with title **`chore: release vX.Y.Z`** and a body summarizing user-visible changes since the last tag.
6. Create git tag **`vX.Y.Z`** on that commit.
7. **Post-release commit:** bump to the next dev line (e.g. `0.3.0.dev0` after `0.2.0`), **`uv lock --refresh`**, commit with **`chore: bump to development release …`**.
8. **Build PyPI artifacts from the tag**, not from dev `main`:

   ```bash
   git checkout "vX.Y.Z"
   rm -f dist/invariant_gfx-*
   uv build
   git checkout -
   ```

9. **Do not** `git push` or publish to PyPI unless the user explicitly asks and can authenticate.

## Notes

- Distribution name on PyPI / metadata: **`invariant-gfx`** (hyphen). Wheel/sdist filenames use underscores: **`invariant_gfx-…`**.
- For lockfile-only edits after a manual version bump, **`uv lock --refresh`** is sufficient.
