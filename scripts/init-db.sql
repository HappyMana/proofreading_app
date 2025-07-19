-- Initial database setup for proofreading system

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create basic tables for initial setup
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create correction rules table
CREATE TABLE IF NOT EXISTS correction_rules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    pattern TEXT NOT NULL,
    replacement TEXT,
    rule_type VARCHAR(50) NOT NULL, -- 'spelling', 'grammar', 'style'
    confidence DECIMAL(3,2) DEFAULT 0.8,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create proofreading history table
CREATE TABLE IF NOT EXISTS proofreading_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    original_text TEXT NOT NULL,
    corrected_text TEXT,
    corrections_applied JSONB,
    processing_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_correction_rules_type ON correction_rules(rule_type);
CREATE INDEX IF NOT EXISTS idx_proofreading_history_user ON proofreading_history(user_id);
CREATE INDEX IF NOT EXISTS idx_proofreading_history_created ON proofreading_history(created_at);

-- Insert sample data
INSERT INTO users (email, username, hashed_password, is_admin) 
VALUES ('admin@example.com', 'admin', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', TRUE)
ON CONFLICT (email) DO NOTHING;

-- Insert sample correction rules
INSERT INTO correction_rules (name, pattern, replacement, rule_type) VALUES
('ら抜き言葉 - 食べれる', '食べれる', '食べられる', 'grammar'),
('ら抜き言葉 - 見れる', '見れる', '見られる', 'grammar'),
('助詞の誤用 - を', '(?<=時間)を(?=過ごす)', 'に', 'grammar'),
('漢字の誤用 - 詳細', '詳細', '詳細', 'spelling')
ON CONFLICT DO NOTHING;