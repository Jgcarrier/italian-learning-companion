"""
Italian Learning Companion - Database Module
Manages all data storage and retrieval for the learning system.
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import json

class ItalianDatabase:
    def __init__(self, db_path: str = "../data/curriculum.db"):
        """Initialize database connection and create tables if needed."""
        self.db_path = Path(__file__).parent / db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        self.create_tables()
    
    def create_tables(self):
        """Create all necessary tables for the learning system."""
        cursor = self.conn.cursor()
        
        # Topics table - stores grammar topics and their details
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,  -- 'verbs', 'pronouns', 'prepositions', 'articles', etc.
                level TEXT NOT NULL,     -- 'A1', 'A2', 'B1', etc.
                description TEXT,
                lesson_reference TEXT,   -- e.g., "Nuovo Espresso 1, Lezione 7"
                completed BOOLEAN DEFAULT 0,
                date_added TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Vocabulary table - stores words and phrases
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vocabulary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                italian TEXT NOT NULL,
                english TEXT NOT NULL,
                word_type TEXT,          -- 'noun', 'verb', 'adjective', 'phrase', etc.
                gender TEXT,             -- 'masculine', 'feminine', 'both', NULL
                plural TEXT,             -- plural form if applicable
                category TEXT,           -- 'food', 'travel', 'family', etc.
                level TEXT NOT NULL,     -- 'A1', 'A2', etc.
                example_sentence TEXT,
                date_added TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Verb conjugations table - stores verb forms
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS verb_conjugations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                infinitive TEXT NOT NULL,
                english TEXT NOT NULL,
                verb_type TEXT NOT NULL, -- 'regular_are', 'regular_ere', 'regular_ire', 'irregular'
                tense TEXT NOT NULL,     -- 'presente', 'passato_prossimo', 'imperfetto', etc.
                person TEXT NOT NULL,    -- 'io', 'tu', 'lui_lei', 'noi', 'voi', 'loro'
                conjugated_form TEXT NOT NULL,
                auxiliary TEXT,          -- 'avere', 'essere', NULL (for past tenses)
                level TEXT NOT NULL,
                UNIQUE(infinitive, tense, person)
            )
        """)
        
        # Practice sessions table - tracks all practice attempts
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS practice_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_date TEXT DEFAULT CURRENT_TIMESTAMP,
                session_type TEXT NOT NULL,  -- 'verb_drill', 'vocabulary_quiz', 'fill_blank', etc.
                topic_id INTEGER,
                total_questions INTEGER NOT NULL,
                correct_answers INTEGER NOT NULL,
                time_spent_seconds INTEGER,
                FOREIGN KEY (topic_id) REFERENCES topics(id)
            )
        """)
        
        # Question results table - stores individual question performance
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS question_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                question_text TEXT NOT NULL,
                correct_answer TEXT NOT NULL,
                user_answer TEXT NOT NULL,
                is_correct BOOLEAN NOT NULL,
                topic_id INTEGER,
                vocab_id INTEGER,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES practice_sessions(id),
                FOREIGN KEY (topic_id) REFERENCES topics(id),
                FOREIGN KEY (vocab_id) REFERENCES vocabulary(id)
            )
        """)
        
        # User progress table - tracks mastery of each topic
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_id INTEGER NOT NULL,
                mastery_level REAL DEFAULT 0.0,  -- 0.0 to 1.0
                last_practiced TEXT,
                times_practiced INTEGER DEFAULT 0,
                consecutive_correct INTEGER DEFAULT 0,
                needs_review BOOLEAN DEFAULT 1,
                FOREIGN KEY (topic_id) REFERENCES topics(id),
                UNIQUE(topic_id)
            )
        """)
        
        # Weak areas table - tracks areas needing extra practice
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS weak_areas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_id INTEGER,
                vocab_id INTEGER,
                error_count INTEGER DEFAULT 1,
                last_error_date TEXT DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (topic_id) REFERENCES topics(id),
                FOREIGN KEY (vocab_id) REFERENCES vocabulary(id)
            )
        """)
        
        self.conn.commit()
        print("✓ Database tables created successfully")
    
    def add_topic(self, name: str, category: str, level: str, 
                  description: str = "", lesson_ref: str = "", 
                  completed: bool = False) -> int:
        """Add a new grammar topic to track."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO topics (name, category, level, description, lesson_reference, completed)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, category, level, description, lesson_ref, completed))
        self.conn.commit()
        return cursor.lastrowid
    
    def add_vocabulary(self, italian: str, english: str, word_type: str,
                       level: str, gender: str = None, plural: str = None,
                       category: str = None, example: str = None) -> int:
        """Add a new vocabulary word."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO vocabulary (italian, english, word_type, gender, plural, category, level, example_sentence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (italian, english, word_type, gender, plural, category, level, example))
        self.conn.commit()
        return cursor.lastrowid
    
    def add_verb_conjugation(self, infinitive: str, english: str, verb_type: str,
                            tense: str, person: str, conjugated_form: str,
                            level: str, auxiliary: str = None) -> int:
        """Add a verb conjugation."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO verb_conjugations 
            (infinitive, english, verb_type, tense, person, conjugated_form, auxiliary, level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (infinitive, english, verb_type, tense, person, conjugated_form, auxiliary, level))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_topics_by_level(self, level: str) -> List[Dict]:
        """Get all topics for a specific level."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM topics WHERE level = ?", (level,))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_weak_areas(self, limit: int = 10) -> List[Dict]:
        """Get topics/vocabulary that need extra practice."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT wa.*, t.name as topic_name, v.italian as vocab_word
            FROM weak_areas wa
            LEFT JOIN topics t ON wa.topic_id = t.id
            LEFT JOIN vocabulary v ON wa.vocab_id = v.id
            ORDER BY wa.error_count DESC, wa.last_error_date DESC
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]
    
    def record_practice_session(self, session_type: str, total_questions: int,
                                correct_answers: int, topic_id: int = None,
                                time_spent: int = None) -> int:
        """Record a completed practice session."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO practice_sessions (session_type, total_questions, correct_answers, topic_id, time_spent_seconds)
            VALUES (?, ?, ?, ?, ?)
        """, (session_type, total_questions, correct_answers, topic_id, time_spent))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_performance_stats(self, days: int = 30) -> Dict:
        """Get performance statistics for the last N days."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                COUNT(*) as total_sessions,
                SUM(total_questions) as total_questions,
                SUM(correct_answers) as correct_answers,
                AVG(CAST(correct_answers AS FLOAT) / total_questions * 100) as avg_accuracy
            FROM practice_sessions
            WHERE date(session_date) >= date('now', '-' || ? || ' days')
        """, (days,))
        return dict(cursor.fetchone())
    
    def close(self):
        """Close the database connection."""
        self.conn.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensure connection is closed."""
        self.close()


# Initialize database when module is imported
if __name__ == "__main__":
    # Test database creation
    print("Initializing Italian Learning Companion Database...")
    db = ItalianDatabase()
    print("Database initialized successfully!")
    db.close()
