CREATE TABLE IF NOT EXISTS deck (
    deck_id INTEGER PRIMARY KEY AUTOINCREMENT,
    deck_name TEXT NOT NULL,
    deck_description TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
-- index on deck_name used for search decks by deck_name
CREATE INDEX IF NOT EXISTS idx_deck_name ON deck(deck_name);
-- index on created_at used for search decks by created_at
CREATE INDEX IF NOT EXISTS idx_deck_created_at ON deck (created_at);
-- index on updated_at used for search decks by updated_at
CREATE INDEX IF NOT EXISTS idx_deck_updated_at ON deck (updated_at);

INSERT OR IGNORE INTO deck (
    deck_id,
    deck_name,
    deck_description,
    created_at,
    updated_at
) VALUES (
    1,
    'Default',
    'System default deck',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS note (
    note_id INTEGER PRIMARY KEY AUTOINCREMENT,
    note_type_id INTEGER NOT NULL,
    fields_JSON TEXT NOT NULL,
    tags_JSON TEXT NOT NULL,
    sort_field TEXT NOT NULL,
    checksum TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    hint TEXT NOT NULL DEFAULT ''
);
-- used for search note by note_type_id and checksum, which is unique for each note
CREATE INDEX IF NOT EXISTS idx_note_note_type_id ON note (note_type_id,checksum);

CREATE TABLE IF NOT EXISTS card (
    card_id INTEGER PRIMARY KEY AUTOINCREMENT,
    note_id INTEGER NOT NULL,
    deck_id INTEGER NOT NULL DEFAULT 1,
    template_ord INTEGER NOT NULL,
    status TEXT NOT NULL,
    due TEXT NOT NULL, -- when card is generated, there should be a due date
    interval INTEGER NOT NULL DEFAULT 0,
    ease FLOAT NOT NULL DEFAULT 2.5,
    reps INTEGER NOT NULL DEFAULT 0,
    lapses INTEGER NOT NULL DEFAULT 0,
    step_index INTEGER,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(note_id,template_ord),
    FOREIGN KEY (note_id) REFERENCES note (note_id) ON DELETE CASCADE,
    FOREIGN KEY (deck_id) REFERENCES deck (deck_id) ON DELETE CASCADE
);
-- index on note_id used for search cards by note_id
CREATE INDEX IF NOT EXISTS idx_card_note_id ON card (note_id);
-- index on deck_id used for search cards by deck_id
CREATE INDEX IF NOT EXISTS idx_card_deck_id ON card (deck_id);
-- index on status and due used for scheduling, which due<=today and with status
CREATE INDEX IF NOT EXISTS idx_card_status_due ON card (status, due);

CREATE TABLE IF NOT EXISTS review_log (
    review_log_id INTEGER PRIMARY KEY AUTOINCREMENT, -- log_id
    card_id INTEGER NOT NULL,
    deck_id INTEGER NOT NULL,
    rating TEXT NOT NULL CHECK(rating IN ('good', 'again')),
    old_status TEXT NOT NULL CHECK(old_status IN ('new', 'learning', 'review','relearning')),
    new_status TEXT NOT NULL CHECK(new_status IN ('new', 'learning', 'review','relearning')),
    old_due TEXT, -- JUST A quick shot
    new_due TEXT, -- JUST A quick shot
    old_interval INTEGER NOT NULL,
    new_interval INTEGER NOT NULL,
    old_ease FLOAT NOT NULL,
    new_ease FLOAT NOT NULL,
    old_lapses INTEGER NOT NULL,
    new_lapses INTEGER NOT NULL,
    old_reps INTEGER NOT NULL,
    new_reps INTEGER NOT NULL,
    old_step_index INTEGER,
    new_step_index INTEGER,
    hint_used BOOLEAN NOT NULL DEFAULT FALSE,
    review_time TEXT NOT NULL,
    FOREIGN KEY (card_id) REFERENCES card (card_id) ON DELETE CASCADE,
    FOREIGN KEY (deck_id) REFERENCES deck (deck_id) ON DELETE CASCADE
);
-- index on card_id used for search review logs by card_id
CREATE INDEX IF NOT EXISTS idx_review_log_card_id ON review_log (card_id);
-- index on deck_id used for search review logs by deck_id
CREATE INDEX IF NOT EXISTS idx_review_log_deck_id ON review_log (deck_id);
-- index on review_time used for search review logs by review_time
CREATE INDEX IF NOT EXISTS idx_review_log_card_time ON review_log (card_id,review_time);
-- index on deck_id and review_time used for search review logs by deck_id and review_time
CREATE INDEX IF NOT EXISTS idx_review_log_deck_time ON review_log (deck_id,review_time);
