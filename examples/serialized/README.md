# Serialized Examples

## Square Button Badge

[`square_button_badge.json`](./square_button_badge.json) is a graph-output
wrapper for a square button/badge template:

- `gfx:create_solid` creates a 144x144 button background.
- `stdlib:coalesce` resolves optional `text`, `color`, `width`, and `height`
  params to graph-local defaults.
- `gfx:resolve_color` resolves a hex or named text color to an RGBA tuple.
- `gfx:render_text` renders the resolved text using `fit_width`.
- `gfx:composite` centers the fitted text on the background.

Run it with its built-in defaults:

```bash
uv run python -m invariant \
  examples/serialized/square_button_badge.json \
  --output output/square_button_badge.png
```

Override the context defaults from the CLI:

```bash
uv run python -m invariant \
  examples/serialized/square_button_badge.json \
  --param "text=My Button" \
  --param "color=#FF0000" \
  --param width=144 \
  --param height=72 \
  --output output/button.png
```

The CLI selects the `final` `ImageArtifact` and writes it as a PNG. Without
`--output`, the selected artifact is emitted as Invariant JSON. In Python, load
the same graph with `load_graph_output_from_dict()`, execute with a context such
as `{"text": "SALE", "color": "gold", "width": 144, "height": 72}`, or use
`None` values to select graph-local defaults, then save `results[output].image`
as PNG.
