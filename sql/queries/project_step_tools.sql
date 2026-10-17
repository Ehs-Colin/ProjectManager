-- name: CreateProjectStepTool :one
INSERT INTO ProjectStepTools (project_id, step_id, tool_id)
VALUES (
    ?,
    ?,
    ?
)
RETURNING *;

-- name: GetProjectStepTools :many
SELECT * FROM ProjectStepTools WHERE project_id = ?;

-- name: GetToolsProjectStep :many
SELECT * FROM ProjectStepTools WHERE project_id = ? AND step_id = ?;

-- name: DeleteProjectStepTool :exec
DELETE FROM ProjectStepTools WHERE project_id = ? AND step_id = ? AND tool_id = ?;
