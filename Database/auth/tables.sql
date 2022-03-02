CREATE TABLE IF NOT EXISTS Employee (
    accessLevel INTEGER,
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    salt TEXT NOT NULL,
    name TEXT NOT NULL
);