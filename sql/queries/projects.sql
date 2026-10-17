-- name: CreateProject :one
INSERT INTO projects (
    id,
    create_at,
    update_at,
    name,
    description,
    budget,
    completion_percent,
    active,
    complete
) VALUES (
    ?,
    NOW(),
    NOW(),
    ?,
    ?,
    ?,
    ?,
    ?,
    ?
) RETURNING *;

-- name: GetProjects :many
SELECT * FROM projects;

-- name: GetProjectByName :one
SELECT * FROM projects WHERE name = ?;

-- name: GetProjectById :one
SELECT * FROM projects WHERE id = ?;

-- name: UpdateProject :one
UPDATE projects SET
    name = ?,
    description = ?,
    budget = ?,
    completion_percent = ?,
    active = ?,
    complete = ?,
    update_at = NOW()
WHERE id = ?
RETURNING *;

-- name: DeleteProject :exec
DELETE FROM projects WHERE id = ?;
