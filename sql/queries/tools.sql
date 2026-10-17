-- name: CreateTool :one
INSERT INTO tools (id, create_at, update_at, name, description)
VALUES (
    ?,
    NOW(),
    NOW(),
    ?,
    ?
) RETURNING *;

-- name: GetTools :many
SELECT * FROM tools;

-- name: GetToolbyId :one
SELECT * FROM tools WHERE id = ?;

-- name: GetToolByName :one
SELECT * FROM tools WHERE name = ?;

-- name: UpdateTool :one
UPDATE tools
SET name = ?, description = ?, update_at = NOW()
WHERE id = ?
RETURNING *;

-- name: DeleteTool :exec
DELETE FROM tools WHERE id = ?;
