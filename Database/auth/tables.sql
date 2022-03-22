CREATE TABLE IF NOT EXISTS Employee (
    accessLevel INT, 
    username VARCHAR(255) PRIMARY KEY, 
    password BINARY(32) NOT NULL, 
    salt VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL
);
