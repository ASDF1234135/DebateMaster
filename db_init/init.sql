CREATE TABLE IF NOT EXISTS debate_sessions (
    session_id UUID PRIMARY KEY,
    prompt TEXT NOT NULL,
    context TEXT,
    file_name TEXT,
    opponent_persona TEXT,
    my_persona TEXT,
    max_rounds INT NOT NULL,
    trial INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS debate_messages (
    id SERIAL PRIMARY KEY,
    session_id UUID REFERENCES debate_sessions(session_id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    speaker VARCHAR(50) NOT NULL,
    round INT NOT NULL,
    trial INT NOT NULL,
    content TEXT NOT NULL,
    sequence_no INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS debate_summaries (
    session_id UUID PRIMARY KEY REFERENCES debate_sessions(session_id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    speaker VARCHAR(50) NOT NULL,
    pros JSONB,
    cons JSONB,
    improvement_tips JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);