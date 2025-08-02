-- Drop existing tables if recreating (optional, for clean start)
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS users;

-- Create users table (matches CS50 distribution)
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    username TEXT NOT NULL,
    hash TEXT NOT NULL,
    cash NUMERIC NOT NULL DEFAULT 10000.00
);

-- Unique index on username
CREATE UNIQUE INDEX username ON users (username);

-- Create transactions table
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    user_id INTEGER NOT NULL,
    symbol TEXT NOT NULL,
    shares INTEGER NOT NULL,
    price NUMERIC NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('buy', 'sell')),  -- Constraint for valid types
    transacted DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Index for fast user-based queries
CREATE INDEX user_transactions ON transactions (user_id);