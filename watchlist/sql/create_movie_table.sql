DROP TABLE IF EXISTS movies;
CREATE TABLE movies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    director TEXT NOT NULL,
    title TEXT NOT NULL,
    year INTEGER NOT NULL,
    genre TEXT NOT NULL,
    duration INTEGER NOT NULL CHECK(duration > 0),
    rating REAL NOT NULL CHECK(rating >= 0.0 AND rating <= 10.0),
    watch_count INTEGER DEFAULT 0,
    deleted BOOLEAN DEFAULT FALSE,
    UNIQUE(director, title, year)
);