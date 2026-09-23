# RBGraph Chat Command Reference

Chat commands are short, direct transformations of the current diagram.

## Add

`add Redis`

Adds a technology node to the diagram.

## Connect

`add OpenAI to API`

Creates or updates a relationship involving the named components.

## Remove

`remove PostgreSQL`

Removes the requested node and its dependent edges when the command semantics allow it.

## Move

`move authentication left`

Requests a positional change without changing the logical relationship graph.

## Highlight

`highlight rollback path`

Marks a relevant path for visual emphasis.

## Clear

`clear highlight`

Removes the active visual highlight.

Command parsing should remain deterministic where possible so the same instruction produces a predictable model update.