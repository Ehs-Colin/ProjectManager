-- +goose Up
CREATE TABLE Projects (
    id TEXT PRIMARY KEY,
    create_at TIMESTAMP NOT NULL,
    update_at TIMESTAMP NOT NULL,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    budget INTEGER,
    completion_percent REAL,
    active BOOLEAN,
    complete BOOLEAN
);

CREATE TABLE Areas (
    id TEXT PRIMARY KEY,
    create_at TIMESTAMP NOT NULL,
    update_at TIMESTAMP NOT NULL,
    name TEXT UNIQUE NOT NULL,
    description TEXT
);

CREATE TABLE ProjectAreas (
    project_id TEXT NOT NULL,
    area_id TEXT NOT NULL,
    notes TEXT,
    PRIMARY KEY (project_id, area_id),
    FOREIGN KEY (project_id) REFERENCES Projects(id),
    FOREIGN KEY (area_id) REFERENCES Areas(id)
);

CREATE TABLE ProjectSteps (
    id TEXT NOT NULL,
    project_id TEXT NOT NULL,
    create_at TIMESTAMP NOT NULL,
    update_at TIMESTAMP NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    completion_percent REAL,
    order_id INTEGER,
    PerformStepValue INTEGER,
    ProjectValue INTEGER,
    PRIMARY KEY (id, project_id),
    FOREIGN KEY (project_id) REFERENCES Projects(id)
);

CREATE TABLE ProjectStepTools (
    project_id TEXT NOT NULL,
    step_id TEXT NOT NULL,
    tool_id TEXT NOT NULL,
    PRIMARY KEY (project_id, step_id, tool_id),
    FOREIGN KEY (project_id) REFERENCES Projects(id),
    FOREIGN KEY (step_id) REFERENCES ProjectSteps(id),
    FOREIGN KEY (tool_id) REFERENCES Tools(id)
);

create table Tools (
    id TEXT PRIMARY KEY,
    create_at TIMESTAMP NOT NULL,
    update_at TIMESTAMP NOT NULL,
    name TEXT UNIQUE NOT NULL,
    description TEXT
);

-- +goose Down
DROP TABLE ProjectStepTools;
DROP TABLE ProjectAreas;
DROP TABLE ProjectSteps;
DROP TABLE Projects;
DROP TABLE Areas;
DROP TABLE Tools;
