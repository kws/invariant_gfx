# **Subgraphs: Reusable DAG Fragments**

A **subgraph** is a DAG fragment that appears as a single vertex in a parent graph. Instead of merging many internal nodes into the parent, the parent sees one node with dependencies and one output artifact. This keeps graphs composable, allows reuse of complex pipelines (e.g. effect recipes), and preserves fine-grained caching because internal ops still run against the same ArtifactStore.

Subgraphs are a core Invariant GFX (and Invariant) concept. They are not specific to any domain; [effects.md](effects.md) uses them for bundled effect recipes (drop shadow, stroke, glow, etc.).

## **1. The SubGraphNode Model**

A **SubGraphNode** is a node-like construct that:

* **Has `deps` and `params`** — just like a regular `Node`. Upstream artifacts (and any other inputs) are declared as dependencies.
* **Carries an internal `graph: dict[str, Node]`** and an **`output: str`** — the node ID of the internal node whose artifact is the subgraph's result. There is no `op_name`; execution runs the internal graph instead of invoking a single op.
* **Produces one artifact** — the output of the designated internal node.
* **Hides its internals** — the parent graph never sees or references internal node IDs. No naming convention or prefix is needed, because internal nodes are never merged into the parent namespace.

From the parent graph's perspective, a SubGraphNode is indistinguishable from a regular Node: it has an ID, it declares deps, and it produces one artifact that downstream nodes reference via `ref(node_id)`.

## **2. Execution Semantics**

When the Executor encounters a SubGraphNode (in topological order), it:

1. **Resolves** the SubGraphNode's params normally (ref/cel/expressions) using the parent's `artifacts_by_node`.
2. **Executes** the internal graph by calling `executor.execute(node.graph, context=resolved_params)` — the same Executor instance, same registry, same ArtifactStore. Resolved params are passed as context so internal nodes can reference upstream artifacts (and any other inputs) by the same dependency names the subgraph builder used.
3. **Returns** the internal `output` node's artifact as this vertex's artifact, storing it in `artifacts_by_node[node_id]` for downstream nodes.

Internal nodes are never part of the parent graph's dict. They run in an isolated execution context; only the final output artifact is visible to the parent.

## **3. Shared Caching**

All subgraph executions use the **same ArtifactStore** as the parent graph. Each internal op is cached by `(op_name, digest)` in that store. Therefore:

* If two different SubGraphNodes both run the same op on the same upstream artifact, the second execution gets a **cache hit** — the store already has the artifact for that digest.
* If the same subgraph recipe is used in multiple places with the same inputs and params, internal nodes are deduplicated across those subgraph runs.
* No SubGraphNode-level caching is required; fine-grained op caching is sufficient.

This guarantees that identical work is never repeated, whether it occurs inside one subgraph, across multiple subgraphs, or in a mix of subgraphs and regular nodes.

## **4. Usage Example**

A subgraph is typically produced by a builder function (e.g. an effect recipe) that returns a `SubGraphNode`. The parent graph assigns it to a node ID and uses that ID like any other node.

```python
graph = {
    "background": Node(op_name="gfx:create_solid", params={...}, deps=[]),
    "text": Node(op_name="gfx:render_text", params={...}, deps=[]),
    "shadow": drop_shadow("text", dx=2, dy=2, sigma=Decimal("3")),  # Returns SubGraphNode; deps=["text"]
    "final": Node(
        op_name="gfx:composite",
        params={
            "layers": [
                {"image": ref("background"), "id": "background"},
                {"image": ref("shadow"), "id": "shadow"},
                {"image": ref("text"), "id": "text"},
            ],
        },
        deps=["background", "shadow", "text"],
    ),
}
```

Here `drop_shadow()` is an effect recipe that returns a `SubGraphNode` whose `deps` include the source node ID (e.g. `"text"`). The parent graph treats `"shadow"` exactly like `"text"` — no prefix, no `graph.update()`, no exposed internal node IDs. For full effect recipes and filter primitives, see [effects.md](effects.md).

## **5. Upstream Dependency (Invariant)**

This model requires changes to **Invariant (parent project)**:

| Component | Change |
|:--|:--|
| **Node / SubGraphNode** | Introduce a `SubGraphNode` dataclass (or a shared base with `Node`) that has `params`, `deps`, `graph: dict[str, Node]`, and `output: str` instead of `op_name`. The executor and resolver must accept both types in a graph. |
| **Executor** | In the execution loop, branch on node type: for a `SubGraphNode`, resolve params, then call `self.execute(node.graph, context=resolved_params)` and use the result for `node.output` as this vertex's artifact. Do not merge internal nodes into the parent graph. |
| **GraphResolver** | `validate()` and `topological_sort()` must accept `SubGraphNode` alongside `Node`: validate that `deps` exist, skip the op-registry check for SubGraphNodes, and defer validation of the internal graph to sub-execution time. |

Until these upstream changes exist, subgraph-returning helpers can be implemented that build and return a `SubGraphNode` structure; the actual execution branch must be added in Invariant.

## **6. Related Documents**

* [architecture.md](architecture.md) — Op standard library, artifact types, pipeline model
* [effects.md](effects.md) — Uses subgraphs for effect recipes (drop shadow, stroke, glow, inner shadow)
