CREATE TABLE IF NOT EXISTS sentences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL ,
    descriptions TEXT NULL
);
CREATE TABLE IF NOT EXISTS words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word TEXT NOT NULL,
    definition TEXT NOT NULL,
    sentence_id INTEGER,
    FOREIGN KEY (sentence_id) REFERENCES sentences(id) 
);