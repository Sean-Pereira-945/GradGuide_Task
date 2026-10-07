-- SQLite Database Schema for GradGuide Job Discovery Tool

CREATE TABLE IF NOT EXISTS jobs (
  id TEXT PRIMARY KEY,
  source TEXT NOT NULL,
  url TEXT NOT NULL,
  title TEXT NOT NULL,
  employer TEXT,
  location_text TEXT,
  city TEXT,
  lat REAL,
  lng REAL,
  job_type TEXT NOT NULL,
  category TEXT,
  pay_min REAL,
  pay_max REAL,
  pay_unit TEXT,
  pay_text TEXT,
  hours_min REAL,
  hours_max REAL,
  posted_date TEXT,
  description TEXT,
  content_hash TEXT UNIQUE,
  trust_score INTEGER DEFAULT 100,
  trust_reasons TEXT DEFAULT '[]',   -- JSON array string
  first_seen TEXT NOT NULL,
  last_seen TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_jobs_type ON jobs(job_type);
CREATE INDEX IF NOT EXISTS idx_jobs_city ON jobs(city);
CREATE INDEX IF NOT EXISTS idx_jobs_category ON jobs(category);

CREATE TABLE IF NOT EXISTS scrape_runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source TEXT NOT NULL,
  started_at TEXT NOT NULL,
  finished_at TEXT NOT NULL,
  pages_fetched INTEGER DEFAULT 0,
  jobs_found INTEGER DEFAULT 0,
  jobs_new INTEGER DEFAULT 0,
  errors INTEGER DEFAULT 0,
  error_log TEXT
);

CREATE TABLE IF NOT EXISTS applications (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  job_id TEXT NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
  status TEXT NOT NULL,                      -- saved | applied | interview | offer | rejected
  applied_on TEXT,
  follow_up_on TEXT,
  notes TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS student_profile (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  country TEXT DEFAULT 'Australia',
  visa_type TEXT DEFAULT 'Student (Subclass 500)',
  current_weekly_hours REAL DEFAULT 0,
  in_study_period INTEGER DEFAULT 1,
  home_city TEXT DEFAULT 'Adelaide'
);

-- Seed default profile row if empty
INSERT OR IGNORE INTO student_profile (id, country, visa_type, current_weekly_hours, in_study_period, home_city)
VALUES (1, 'Australia', 'Student (Subclass 500)', 12.0, 1, 'Adelaide');
