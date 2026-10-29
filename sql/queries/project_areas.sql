-- name: CreateProjectArea :one
INSERT INTO ProjectAreas (project_id, area_id, notes)
VALUES (
    $1,
    $2,
    $3
)
RETURNING *;

-- name: GetProjectAreas :many
SELECT * FROM ProjectAreas WHERE project_id = $1;

-- name: GetProjectAreasInfo :many
SELECT ProjectAreas.notes as project_area_notes, Areas.*
FROM ProjectAreas
JOIN Areas ON ProjectAreas.area_id = Areas.id
WHERE ProjectAreas.project_id = $1;

-- name: GetAreaProjects :many
SELECT * FROM ProjectAreas WHERE area_id = $1;

-- name: UpdateProjectArea :one
UPDATE ProjectAreas
SET notes = $3
WHERE project_id = $1 AND area_id = $2
RETURNING *;

-- name: DeleteProjectArea :exec
DELETE FROM ProjectAreas
WHERE project_id = $1 AND area_id = $2;
