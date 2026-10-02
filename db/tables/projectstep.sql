CREATE TABLE ProjectStep (
    id INTEGER NOT NULL,
    project_id INTEGER NOT NULL,
    name TEXT,
    description TEXT,
    completion_percent REAL,
    order_id INTEGER,
    PerformStepValue INTEGER,
    ProjectValue INTEGER,
    PRIMARY KEY (id, project_id),
    FOREIGN KEY (project_id) REFERENCES Project(id)
);
