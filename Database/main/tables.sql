CREATE TABLE IF NOT EXISTS Reward (
    name TEXT NOT NULL PRIMARY KEY,
    requirement INTEGER NOT NULL, -- This is for items
    priceReq REAL,
    description TEXT,
    createdBy TEXT,
    active INTEGER,
    numReq INTEGER,
    createdOn INTEGER,
    expireDate INTEGER,
    type TEXT,
    FOREIGN KEY(requirement) REFERENCES Inventory(SKU)
);

CREATE TABLE IF NOT EXISTS Customer (
    name TEXT NOT NULL,
    DOB INTEGER NOT NULL, 
    phone INTEGER PRIMARY KEY,
    DLN INTEGER,
    email TEXT,
    customerSince INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS Inventory (
    name TEXT NOT NULL,
    SKU INTEGER PRIMARY KEY,
    price REAL NOT NULL,
    count INTEGER
);

CREATE TABLE IF NOT EXISTS hasReward (
    phone INTEGER,
    title text,
    useBy INTEGER,
    FOREIGN KEY(phone) REFERENCES Customer(phone),
    FOREIGN KEY(title) REFERENCES Reward(name)
);

CREATE TABLE IF NOT EXISTS purchaseHistory (
    phone INTEGER,
    SKU INTEGER,
    quantity INTEGER,
    purchaseDate INTEGER,
    totalCost REAL,
    FOREIGN KEY(phone) REFERENCES Customer(phone),
    FOREIGN KEY(SKU) REFERENCES Inventory(SKU)
);

INSERT OR IGNORE INTO Inventory(name, SKU, price, count) VALUES ('Visit', 0, 0.00, 1);