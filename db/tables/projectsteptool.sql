CREATE TABLE ProjectStepTool (
    project_id INTEGER NOT NULL,
    step_id INTEGER NOT NULL,
    tool_id INTEGER NOT NULL,
    PRIMARY KEY (project_id, step_id, tool_id),
    FOREIGN KEY (project_id) REFERENCES Project(id),
    FOREIGN KEY (step_id) REFERENCES ProjectStep(id),
    FOREIGN KEY (tool_id) REFERENCES Tool(id)
);
