# API Reference

## Health

`GET /health`

Returns the current service status.

## Generate

`POST /api/diagrams/generate`

Request:

```json
{
  "description": "User connects to API and API uses PostgreSQL",
  "name": "Example",
  "diagram_type": "architecture"
}
```

The response contains the validated diagram model and rendered SVG.

## Apply a command

`POST /api/diagrams/command`

Request:

```json
{
  "diagram": {},
  "command": "add Redis to API"
}
```

The response contains the updated diagram, SVG, and a human-readable message.

## Save

`POST /api/diagrams`

Stores a validated diagram in SQLite.

## History

`GET /api/diagrams`

Returns saved diagram metadata ordered by newest first.

## Load

`GET /api/diagrams/{diagram_id}`

Returns a saved diagram and its SVG.

## Delete

`DELETE /api/diagrams/{diagram_id}`

Deletes one saved diagram.
