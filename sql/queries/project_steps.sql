-- name: CreateProjectStep :one
INSERT INTO ProjectSteps (id, project_id, create_at, update_at, name, description, completion_percent, order_id, PerformStepValue, ProjectValue)
VALUES (
    ?,
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

-- name: GetProjectStepsByProjectId :many
SELECT * FROM ProjectSteps WHERE project_id = ?;

-- name: UpdateProjectStep :one
UPDATE ProjectSteps
SET name = ?,
    description = ?,
    completion_percent = ?,
    order_id = ?,
    PerformStepValue = ?,
    ProjectValue = ?,
    update_at = NOW()
WHERE id = ?
RETURNING *;

-- name: DeleteProjectStep :exec
DELETE FROM ProjectSteps WHERE id = ?;
