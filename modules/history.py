import sqlite3
from datetime import datetime

DB_NAME = "coderisk_history.db"

def init_db():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        risk_score REAL,
        severity TEXT,
        complexity REAL
    )
    """)

    conn.commit()
    conn.close()


def save_scan(score, severity, complexity):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO scans(timestamp, risk_score, severity, complexity)
    VALUES (?, ?, ?, ?)
    """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), score, severity, complexity))

    conn.commit()
    conn.close()