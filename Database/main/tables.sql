CREATE TABLE IF NOT EXISTS Customer (
    name VARCHAR(255) NOT NULL,
    DOB INT NOT NULL, 
    phone BIGINT PRIMARY KEY,
    DLN INT,
    email VARCHAR(255),
    customerSince INT NOT NULL
);

CREATE TABLE IF NOT EXISTS Inventory (
    name VARCHAR(255) NOT NULL,
    SKU INT PRIMARY KEY,
    price FLOAT NOT NULL,
    count INT
);

CREATE TABLE IF NOT EXISTS Reward (
    name VARCHAR(255) NOT NULL PRIMARY KEY,
    requirement INT,
    priceReq FLOAT,
    description VARCHAR(255),
    createdBy VARCHAR(255),
    active INT,
    numReq INT,
    createdOn INT,
    expireDate INT,
    type VARCHAR(255),
    FOREIGN KEY(requirement) REFERENCES Inventory(SKU)
);

CREATE TABLE IF NOT EXISTS hasReward (
    phone BIGINT,
    title VARCHAR(255),
    useBy INT,
    FOREIGN KEY(phone) REFERENCES Customer(phone),
    FOREIGN KEY(title) REFERENCES Reward(name)
);

CREATE TABLE IF NOT EXISTS purchaseHistory (
    phone BIGINT,
    SKU INT,
    quantity INT,
    purchaseDate INT,
    totalCost FLOAT,
    FOREIGN KEY(phone) REFERENCES Customer(phone),
    FOREIGN KEY(SKU) REFERENCES Inventory(SKU)
);
