-- name: CreateTool :one
INSERT INTO tools (id, create_at, update_at, name, description)
VALUES (
    $1,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP,
    $2,
    $3
) RETURNING *;

-- name: GetTools :many
SELECT * FROM tools;

-- name: GetToolById :one
SELECT * FROM tools WHERE id = $1;

-- name: GetToolByName :one
SELECT * FROM tools WHERE name = $1;

-- name: UpdateTool :one
UPDATE tools
SET name = $2, description = $3, update_at = CURRENT_TIMESTAMP
WHERE id = $1
RETURNING *;

-- name: DeleteTool :exec
DELETE FROM tools WHERE id = $1;
