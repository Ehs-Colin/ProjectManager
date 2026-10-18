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
    $1,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP,
    $2,
    $3,
    $4,
    $5,
    $6,
    $7
) RETURNING *;

-- name: GetProjects :many
SELECT * FROM projects;

-- name: GetProjectByName :one
SELECT * FROM projects WHERE name = $1;

-- name: GetProjectById :one
SELECT * FROM projects WHERE id = $1;

-- name: UpdateProject :one
UPDATE projects SET
    name = $2,
    description = $3,
    budget = $4,
    completion_percent = $5,
    active = $6,
    complete = $7,
    update_at = CURRENT_TIMESTAMP
WHERE id = $1
RETURNING *;

-- name: DeleteProject :exec
DELETE FROM projects WHERE id = $1;
