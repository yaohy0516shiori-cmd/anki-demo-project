CREATE TABLE IF NOT EXISTS user (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    username TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    phone TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
-- index on email used for search users by email
CREATE INDEX IF NOT EXISTS idx_user_email ON user(email);
-- index on username used for search users by username
CREATE TABLE IF NOT EXISTS deck (
    deck_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    deck_name TEXT NOT NULL,
    deck_description TEXT NOT NULL DEFAULT '',
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,

    FOREIGN KEY (user_id) REFERENCES user (user_id) ON DELETE CASCADE,
    UNIQUE(user_id, deck_name)
);
-- index on deck_name used for search decks by deck_name
CREATE INDEX IF NOT EXISTS idx_deck_id ON deck(deck_id);
-- index on user_id used for search decks by user_id
CREATE INDEX IF NOT EXISTS idx_deck_user_id ON deck (user_id);
-- index on is_default used for search decks by is_default
CREATE INDEX IF NOT EXISTS idx_deck_DEFAULT ON deck (is_default);
CREATE UNIQUE INDEX IF NOT EXISTS idx_one_default_deck_per_user ON deck (user_id) where is_default=1;

CREATE TABLE IF NOT EXISTS note (
    note_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    note_type_id INTEGER NOT NULL,
    fields_JSON TEXT NOT NULL,
    tags_JSON TEXT NOT NULL,
    sort_field TEXT NOT NULL,
    checksum TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    hint TEXT NOT NULL DEFAULT '',

    FOREIGN KEY (user_id) REFERENCES user (user_id) ON DELETE CASCADE,
    UNIQUE(user_id, note_type_id, checksum)
);
-- used for search note by note_type_id and checksum, which is unique for each note
CREATE INDEX IF NOT EXISTS idx_note_user_checksum ON note (user_id,note_type_id,checksum);
CREATE INDEX IF NOT EXISTS idx_note_user_id ON note (user_id,note_id);

CREATE TABLE IF NOT EXISTS card (
    card_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    note_id INTEGER NOT NULL,
    deck_id INTEGER NOT NULL,
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

    FOREIGN KEY (note_id) REFERENCES note (note_id) ON DELETE CASCADE,
    FOREIGN KEY (deck_id) REFERENCES deck (deck_id) ,
    FOREIGN KEY (user_id) REFERENCES user (user_id) ON DELETE CASCADE,
    UNIQUE(user_id, note_id, template_ord)
);
-- index on status and due used for scheduling, which due<=today and with status
CREATE INDEX IF NOT EXISTS idx_card_status_due ON card (user_id,status, due);
CREATE INDEX IF NOT EXISTS idx_card_user_deck_due ON card(user_id, deck_id, due);
CREATE INDEX IF NOT EXISTS idx_card_user_note ON card(user_id, note_id);

CREATE TABLE IF NOT EXISTS review_log (
    review_log_id INTEGER PRIMARY KEY AUTOINCREMENT,-- log_id
    user_id INTEGER NOT NULL, 
    card_id INTEGER ,
    deck_id INTEGER ,
    note_id INTEGER ,
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

    FOREIGN KEY (user_id) REFERENCES user (user_id) ON DELETE CASCADE,
    FOREIGN KEY (card_id) REFERENCES card (card_id) ON DELETE SET NULL,
    FOREIGN KEY (deck_id) REFERENCES deck (deck_id) ON DELETE SET NULL,
    FOREIGN KEY (note_id) REFERENCES note (note_id) ON DELETE SET NULL
);
-- index on review_time used for search review logs by review_time
CREATE INDEX IF NOT EXISTS idx_review_log_card_time ON review_log (user_id,card_id);
-- index on deck_id and review_time used for search review logs by deck_id and review_time
CREATE INDEX IF NOT EXISTS idx_review_log_deck_time ON review_log (user_id,deck_id,review_time);
CREATE INDEX IF NOT EXISTS idx_review_log_user_time ON review_log(user_id, review_time);

CREATE TABLE IF NOT EXISTS study_session (
    session_id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    deck_id INTEGER NOT NULL,
    today TEXT NOT NULL,
    status TEXT NOT NULL,

    learning_queue TEXT NOT NULL DEFAULT '[]',
    review_queue TEXT NOT NULL DEFAULT '[]',
    new_queue TEXT NOT NULL DEFAULT '[]',

    current_card_id INTEGER,
    current_hint_used INTEGER NOT NULL DEFAULT 0,
    current_back_revealed INTEGER NOT NULL DEFAULT 0,

    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,

    FOREIGN KEY(deck_id) REFERENCES deck(deck_id),
    FOREIGN KEY(user_id) REFERENCES user(user_id) ON DELETE CASCADE,
    FOREIGN KEY(current_card_id) REFERENCES card(card_id) ON DELETE SET NULL
);
-- index on deck_id used for search study sessions by deck_id
CREATE INDEX IF NOT EXISTS idx_study_session_deck_id ON study_session (deck_id);
-- index on today used for search study sessions by today
CREATE INDEX IF NOT EXISTS idx_study_session_today ON study_session (today);
CREATE INDEX IF NOT EXISTS idx_study_session_user_id ON study_session(user_id);