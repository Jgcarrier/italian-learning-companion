#!/usr/bin/env python3
"""
Import CEFR vocabulary from Profilo della lingua italiana PDFs
Extracts vocabulary from A1, A2, B1, B2 levels and imports to database
"""

import re
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

# Word type abbreviations mapping
WORD_TYPE_MAP = {
    'v.t.': 'verb (transitive)',
    'v.int.': 'verb (intransitive)',
    'v. rifl.': 'verb (reflexive)',
    'v.t. pron.': 'verb (transitive pronominal)',
    'v.int. pron.': 'verb (intransitive pronominal)',
    'v. int. pron.': 'verb (intransitive pronominal)',
    'v.t.pron.': 'verb (transitive pronominal)',
    'v.int.pron.': 'verb (intransitive pronominal)',
    'v. rifl. recip.': 'verb (reflexive reciprocal)',
    's.m.': 'noun (masculine)',
    's.f.': 'noun (feminine)',
    's.m. - s.f.': 'noun (both)',
    's.m.- s.f.': 'noun (both)',
    'agg.': 'adjective',
    'avv.': 'adverb',
    'pron.': 'pronoun',
    'prep.': 'preposition',
    'art.': 'article',
    'cong.': 'conjunction',
    'inter.': 'interjection',
    'part. pron.': 'pronominal particle',
    'loc.': 'locution',
    's.m. - agg.': 'noun/adjective (masculine)',
    's.m. - avv.': 'noun/adverb (masculine)',
    'avv. - cong.': 'adverb/conjunction',
    'avv. - s.m.': 'adverb/noun (masculine)',
    'agg. - avv.': 'adjective/adverb',
    'agg. - pron.': 'adjective/pronoun',
    'agg. - inter.': 'adjective/interjection',
    'agg. - s.m.': 'adjective/noun (masculine)',
    'v.int. - s.m.': 'verb/noun',
    's.f. - inter.': 'noun/interjection (feminine)',
    'avv. - prep.': 'adverb/preposition',
    'pron. - avv.': 'pronoun/adverb',
    'prep.- avv.': 'preposition/adverb',
    's.f)': 'noun (feminine)',  # Handle malformed entries
}

def extract_word_type(type_str: str) -> Tuple[str, str]:
    """
    Extract word type and gender from type string
    Returns: (word_type, gender)
    """
    type_str = type_str.strip()

    # Get the mapped type
    word_type = WORD_TYPE_MAP.get(type_str, type_str)

    # Determine gender
    gender = None
    if 's.m.' in type_str and 's.f.' in type_str:
        gender = 'both'
    elif 's.m.' in type_str or 'masculine' in word_type.lower():
        gender = 'masculine'
    elif 's.f.' in type_str or 'feminine' in word_type.lower():
        gender = 'feminine'

    # Simplify word type for database
    if word_type.startswith('verb'):
        word_type = 'verb'
    elif word_type.startswith('noun'):
        word_type = 'noun'
    elif word_type.startswith('adjective'):
        word_type = 'adjective'
    elif word_type.startswith('adverb'):
        word_type = 'adverb'
    elif word_type.startswith('pronoun'):
        word_type = 'pronoun'
    elif word_type.startswith('preposition'):
        word_type = 'preposition'
    elif word_type.startswith('article'):
        word_type = 'article'
    elif word_type.startswith('conjunction'):
        word_type = 'conjunction'
    elif word_type.startswith('interjection'):
        word_type = 'interjection'

    return word_type, gender

def parse_vocabulary_file(file_path: str, level: str) -> List[Dict]:
    """
    Parse vocabulary from extracted PDF text file
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    vocabulary = []

    # Pattern to match vocabulary entries like:
    # 1. a (prep.)
    # 79. aereo(aeroplano) (s.m.)
    # 18. amico/a (s.m. – s.f.)

    pattern = r'^\s*\d+\.\s+(.+?)\s+\(([^)]+)\)\s*$'

    for line in content.split('\n'):
        match = re.match(pattern, line)
        if match:
            word_part = match.group(1).strip()
            type_part = match.group(2).strip()

            # Extract the main Italian word
            # Handle cases like "aereo(aeroplano)" or "amico/a"
            italian_word = word_part.split('(')[0].strip()
            italian_word = re.sub(r'/[a-z]$', '', italian_word)  # Remove /a, /o endings for main entry

            # Extract word type and gender
            word_type, gender = extract_word_type(type_part)

            vocab_entry = {
                'italian': italian_word,
                'english': '',  # These PDFs don't include English translations
                'word_type': word_type,
                'gender': gender,
                'level': level,
                'category': None,
                'source': 'Profilo della lingua italiana'
            }

            vocabulary.append(vocab_entry)

    return vocabulary

def check_existing_vocabulary(db_path: str, level: str) -> set:
    """
    Get existing vocabulary words for a given level
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT italian FROM vocabulary WHERE level = ?
    """, (level,))

    existing = {row[0] for row in cursor.fetchall()}
    conn.close()

    return existing

def import_to_database(vocabulary: List[Dict], db_path: str, skip_existing: bool = True):
    """
    Import vocabulary entries to database
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get existing words to avoid duplicates
    existing_words = set()
    if skip_existing:
        cursor.execute("SELECT italian, level FROM vocabulary")
        existing_words = {(row[0], row[1]) for row in cursor.fetchall()}

    inserted_count = 0
    skipped_count = 0

    for entry in vocabulary:
        word_key = (entry['italian'], entry['level'])

        if skip_existing and word_key in existing_words:
            skipped_count += 1
            continue

        cursor.execute("""
            INSERT INTO vocabulary (italian, english, word_type, gender, level, category)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            entry['italian'],
            entry['english'] or 'Translation needed',
            entry['word_type'],
            entry['gender'],
            entry['level'],
            entry['category']
        ))
        inserted_count += 1

    conn.commit()
    conn.close()

    return inserted_count, skipped_count

def generate_statistics(vocabulary_by_level: Dict[str, List[Dict]], db_path: str):
    """
    Generate comprehensive statistics about the vocabulary
    """
    print("\n" + "="*70)
    print("CEFR VOCABULARY EXTRACTION STATISTICS")
    print("="*70)

    total_words = 0

    for level in ['A1', 'A2', 'B1', 'B2']:
        vocab = vocabulary_by_level[level]
        total_words += len(vocab)

        print(f"\n{level} Level:")
        print(f"  Total words: {len(vocab)}")

        # Count by word type
        type_counts = defaultdict(int)
        gender_counts = defaultdict(int)

        for entry in vocab:
            type_counts[entry['word_type']] += 1
            if entry['gender']:
                gender_counts[entry['gender']] += 1

        print(f"  Word types:")
        for word_type, count in sorted(type_counts.items(), key=lambda x: -x[1]):
            print(f"    {word_type}: {count}")

        if gender_counts:
            print(f"  Gender distribution:")
            for gender, count in sorted(gender_counts.items()):
                print(f"    {gender}: {count}")

    print(f"\n{'='*70}")
    print(f"TOTAL VOCABULARY EXTRACTED: {total_words} words")
    print(f"{'='*70}")

    # Check for duplicates with existing GCSE vocabulary
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("\n" + "="*70)
    print("OVERLAP WITH EXISTING VOCABULARY")
    print("="*70)

    for level in ['A1', 'A2', 'B1', 'B2']:
        vocab = vocabulary_by_level[level]
        italian_words = [v['italian'] for v in vocab]

        # Find words already in database (any level)
        placeholders = ','.join(['?'] * len(italian_words))
        cursor.execute(f"""
            SELECT italian, level, COUNT(*)
            FROM vocabulary
            WHERE italian IN ({placeholders})
            GROUP BY italian, level
        """, italian_words)

        overlaps = cursor.fetchall()
        if overlaps:
            print(f"\n{level} words found in existing vocabulary:")
            level_overlap = defaultdict(int)
            for italian, existing_level, count in overlaps:
                level_overlap[existing_level] += 1

            for existing_level, count in sorted(level_overlap.items()):
                print(f"  {existing_level}: {count} words")
        else:
            print(f"\n{level}: No overlaps with existing vocabulary")

    conn.close()
    print("\n" + "="*70 + "\n")

def main():
    # File paths
    base_path = Path("/Users/jamescarrier/Desktop/Parkinglot/Code-Projects/italian-learning-companion")
    db_path = base_path / "data" / "curriculum.db"
    output_dir = base_path / "data" / "cefr_vocabulary"
    output_dir.mkdir(exist_ok=True)

    # Extracted text files
    text_files = {
        'A1': '/tmp/a1_vocab.txt',
        'A2': '/tmp/a2_vocab.txt',
        'B1': '/tmp/b1_vocab.txt',
        'B2': '/tmp/b2_vocab.txt'
    }

    print("Starting CEFR vocabulary extraction...")
    print(f"Database: {db_path}")

    vocabulary_by_level = {}

    # Parse each level
    for level, file_path in text_files.items():
        print(f"\nProcessing {level} vocabulary...")
        vocab = parse_vocabulary_file(file_path, level)
        vocabulary_by_level[level] = vocab

        # Save to JSON
        json_path = output_dir / f"cefr_{level.lower()}_vocabulary.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(vocab, f, ensure_ascii=False, indent=2)
        print(f"  Extracted {len(vocab)} words")
        print(f"  Saved to: {json_path}")

    # Generate statistics before import
    generate_statistics(vocabulary_by_level, str(db_path))

    # Import to database
    print("\nImporting vocabulary to database...")
    total_inserted = 0
    total_skipped = 0

    for level, vocab in vocabulary_by_level.items():
        print(f"\nImporting {level} vocabulary...")
        inserted, skipped = import_to_database(vocab, str(db_path), skip_existing=True)
        total_inserted += inserted
        total_skipped += skipped
        print(f"  Inserted: {inserted}")
        print(f"  Skipped (already exists): {skipped}")

    print("\n" + "="*70)
    print("IMPORT COMPLETE")
    print("="*70)
    print(f"Total words inserted: {total_inserted}")
    print(f"Total words skipped: {total_skipped}")
    print(f"Database updated: {db_path}")
    print("="*70 + "\n")

if __name__ == '__main__':
    main()
