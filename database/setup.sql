-- Users table: stores user information for predictions
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    budget REAL DEFAULT 1000000
    -- Add additional fields as needed (e.g., stats)
);

-- Questions table: stores the questions (only those that users answered)
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY,
    question TEXT NOT NULL,
    tag TEXT,
    end_date DATETIME,
    description TEXT,
    outcome BOOLEAN DEFAULT NULL,  
    outcome_probs TEXT NOT NULL,  -- JSON array of probabilities
    outcomes TEXT NOT NULL  -- JSON array of possible outcomes
);

-- Responses table: stores each user's prediction for a given question
CREATE TABLE IF NOT EXISTS responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    answer TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    correct BOOLEAN DEFAULT NULL,  
    explanation TEXT DEFAULT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (question_id) REFERENCES questions(id)
);

---------------------------------------------------

-- Money Database Tables

-- Transactions table: records each simulated financial transaction
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,  
    transaction_type TEXT NOT NULL,  -- e.g., 'buy', 'sell'
    amount REAL NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Optional: Positions table to track open positions (aggregated stakes)
CREATE TABLE IF NOT EXISTS positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    stake REAL NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users_money(id),
    FOREIGN KEY (question_id) REFERENCES questions(id)
);
