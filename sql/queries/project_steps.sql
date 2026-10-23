-- name: CreateProjectStep :one
INSERT INTO ProjectSteps (id, project_id, create_at, update_at, name, description, completion_percent, order_id, PerformStepValue, ProjectValue)
VALUES (
    $1,
    $2,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP,
    $3,
    $4,
    $5,
    $6,
    $7,
    $8
) RETURNING *;

-- name: GetProjectStepsByProjectId :many
SELECT * FROM ProjectSteps WHERE project_id = $1;

-- name: GetProjectStepsByProjectName :many
SELECT * FROM ProjectSteps WHERE project_id IN (SELECT id FROM Projects WHERE projects.name = $1);

-- name: GetProjectStepByName :one
SELECT * FROM ProjectSteps WHERE project_id = $1 AND name = $2;

-- name: GetProjectStepById :one
SELECT * FROM ProjectSteps WHERE id = $1;

-- name: UpdateProjectStep :one
UPDATE ProjectSteps
SET name = $2,
    description = $3,
    completion_percent = $4,
    order_id = $5,
    PerformStepValue = $6,
    ProjectValue = $7,
    update_at = CURRENT_TIMESTAMP
WHERE id = $1
RETURNING *;

-- name: DeleteProjectStep :exec
DELETE FROM ProjectSteps WHERE id = $1;
