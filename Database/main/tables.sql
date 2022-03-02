CREATE TABLE IF NOT EXISTS Loyalty (
    name TEXT
    requirement TEXT,
    description TEXT,
    title TEXT PRIMARY KEY,
    createdBy TEXT
);

CREATE TABLE IF NOT EXISTS Customer (
    name TEXT,
    address TEXT,
    age INTEGER,
    phone INTEGER PRIMARY KEY,
    DLN INTEGER,
    email TEXT,
    customerSince
);

CREATE TABLE IF NOT EXISTS Inventory (
    name TEXT
    SKU INTEGER PRIMARY KEY,
    price REAL,
    count INTEGER
);

CREATE TABLE IF NOT EXISTS hasReward (
    phone INTEGER,
    title text,
    quantity INTEGER,
    FOREIGN KEY(phone) REFERENCES Customer(phone),
    FOREIGN KEY(title) REFERENCES Loyalty(title)
);

CREATE TABLE IF NOT EXISTS purchaseHistory (
    phone INTEGER,
    SKU INTEGER,
    quantity INTEGER,
    FOREIGN KEY(phone) REFERENCES Customer(phone),
    FOREIGN KEY(SKU) REFERENCES Inventory(SKU)
);