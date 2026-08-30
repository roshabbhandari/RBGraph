# Command Reference

RBGraph accepts short editing commands after a diagram has been generated.

## Add

```text
add Redis
add OpenAI to API
```

The second form creates a connection from the matching existing node.

## Remove

```text
remove PostgreSQL
remove authentication
```

## Move

```text
move API left
move Redis right
move database down
```

## Highlight

```text
highlight rollback path
highlight deploy
```

## Clear highlights

```text
clear highlight
```

Commands operate on the current diagram and are validated before the updated SVG is returned.
