import sqlite3
import json
from datetime import datetime

DB_PATH = "data/jobs.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS jobs (
        id TEXT PRIMARY KEY,
        title TEXT,
        company TEXT,
        location TEXT,
        description TEXT,
        source TEXT,
        apply_url TEXT,
        posted_date TEXT,
        salary TEXT,
        job_type TEXT,
        fetched_at TEXT,
        match_score INTEGER,
        matched_skills TEXT,
        missing_skills TEXT,
        missing_info TEXT,
        recommendation TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS applications (
        job_id TEXT PRIMARY KEY,
        status TEXT,
        applied_at TEXT,
        resume_used TEXT,
        notes TEXT,
        next_action TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS question_memory (
        question_key TEXT PRIMARY KEY,
        answer TEXT,
        context TEXT,
        added_at TEXT
    )''')

    conn.commit()
    conn.close()
    print("Database ready.")

def save_job(job: dict):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO jobs VALUES
        (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
        (
            job['id'], job['title'], job['company'],
            job['location'], job['description'], job['source'],
            job['apply_url'], job.get('posted_date'),
            job.get('salary'), job.get('job_type'),
            job.get('fetched_at', str(datetime.now())),
            job.get('match_score'),
            json.dumps(job.get('matched_skills', [])),
            json.dumps(job.get('missing_skills', [])),
            json.dumps(job.get('missing_info', [])),
            job.get('recommendation')
        )
    )
    conn.commit()
    conn.close()

def get_jobs(recommendation=None, min_score=None):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    query = "SELECT * FROM jobs WHERE 1=1"
    params = []

    if recommendation:
        query += " AND recommendation = ?"
        params.append(recommendation)
    if min_score:
        query += " AND match_score >= ?"
        params.append(min_score)

    query += " ORDER BY match_score DESC"
    rows = c.execute(query, params).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def save_application(app: dict):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO applications VALUES
        (?,?,?,?,?,?)''',
        (
            app['job_id'], app['status'],
            app.get('applied_at'), app.get('resume_used'),
            app.get('notes'), app.get('next_action')
        )
    )
    conn.commit()
    conn.close()

def save_question_memory(key: str, answer: str, context: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO question_memory VALUES
        (?,?,?,?)''',
        (key, answer, context, str(datetime.now()))
    )
    conn.commit()
    conn.close()

def get_question_memory():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    rows = c.execute("SELECT * FROM question_memory").fetchall()
    conn.close()
    return {row['question_key']: row['answer'] for row in rows}