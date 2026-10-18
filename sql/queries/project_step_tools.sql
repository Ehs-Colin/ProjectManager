-- name: CreateProjectStepTool :one
INSERT INTO ProjectStepTools (project_id, step_id, tool_id)
VALUES (
    $1,
    $2,
    $3
)
RETURNING *;

-- name: GetProjectStepTools :many
SELECT * FROM ProjectStepTools WHERE project_id = $1;

-- name: GetToolsProjectStep :many
SELECT * FROM ProjectStepTools WHERE project_id = $1 AND step_id = $2;

-- name: DeleteProjectStepTool :exec
DELETE FROM ProjectStepTools WHERE project_id = $1 AND step_id = $2 AND tool_id = $3;
