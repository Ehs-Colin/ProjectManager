-- name: CreateProjectArea :one
INSERT INTO ProjectAreas (project_id, area_id, notes)
VALUES (
    ?,
    ?,
    ?
)
RETURNING *;

-- name: GetProjectAreas :many
SELECT * FROM ProjectAreas WHERE project_id = ?;

-- name: GetAreaProjects :many
SELECT * FROM ProjectAreas WHERE area_id = ?;

-- name: UpdateProjectArea :one
UPDATE ProjectAreas
SET notes = ?
WHERE project_id = ? AND area_id = ?
RETURNING *;

-- name: DeleteProjectArea :exec
DELETE FROM ProjectAreas
WHERE project_id = ? AND area_id = ?;
