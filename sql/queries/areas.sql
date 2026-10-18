-- name: CreateArea :one
INSERT INTO areas (id, create_at, update_at, name, description)
VALUES (
    $1,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP,
    $2,
    $3
) RETURNING *;

-- name: GetAreas :many
SELECT * FROM areas;

-- name: GetAreaByName :one
SELECT * FROM areas WHERE name = $1;

-- name: GetAreaById :one
SELECT * FROM areas WHERE id = $1;

-- name: UpdateArea :exec
UPDATE areas SET name = $2, description = $3, update_at = CURRENT_TIMESTAMP WHERE id = $1;

-- name: DeleteArea :exec
DELETE FROM areas WHERE id = $1;
