-- name: CreateArea :one
INSERT INTO areas (id, create_at, update_at, name, description)
VALUES (
    ?,
    NOW(),
    NOW(),
    ?,
    ?
) RETURNING *;

-- name: GetAreas :many
SELECT * FROM areas;

-- name: GetAreaByName :one
SELECT * FROM areas WHERE name = ?;

-- name: GetAreaById :one
SELECT * FROM areas WHERE id = ?;

-- name: UpdateArea :exec
UPDATE areas SET name = ?, description = ?, update_at = NOW() WHERE id = ?;

-- name: DeleteArea :exec
DELETE FROM areas WHERE id = ?;
