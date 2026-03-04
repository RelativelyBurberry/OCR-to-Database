-- Records table for OCR results
CREATE TABLE IF NOT EXISTS records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id TEXT NOT NULL,
    data_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

-- Helpful index for querying by template
CREATE INDEX IF NOT EXISTS idx_records_template
ON records(template_id);