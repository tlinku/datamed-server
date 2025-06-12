CREATE TABLE IF NOT EXISTS prescriptions (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL, 
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    pesel VARCHAR(11) NOT NULL,
    issue_date DATE NOT NULL,
    expiry_date DATE NOT NULL,
    pdf_url TEXT,
    med_info_for_search TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS notes (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL, 
    note_name JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS doctors (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL, 
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    specialty VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_prescriptions_user_id ON prescriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_notes_user_id ON notes(user_id);
CREATE INDEX IF NOT EXISTS idx_doctors_user_id ON doctors(user_id);
