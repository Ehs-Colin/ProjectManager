CREATE TABLE ProjectArea (
    project_id INTEGER NOT NULL,
    area_id INTEGER NOT NULL,
    description TEXT,
    PRIMARY KEY (project_id, area_id),
    FOREIGN KEY (project_id) REFERENCES Project(id),
    FOREIGN KEY (area_id) REFERENCES Area(id)
);
