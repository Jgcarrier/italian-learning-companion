#!/usr/bin/env python3
"""
Add GCSE, B1, and B2 content to the Italian Learning Companion database.
This script imports:
- 1,115 GCSE vocabulary entries from Cambridge syllabus
- B1 level sentence examples
- B2 level sentence examples
"""

import sqlite3
import json
import re
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent / 'data' / 'curriculum.db'

def parse_italian_word(italian_text):
    """Parse Italian word to extract gender, plural, and clean word."""
    # Remove parentheses content for clean word
    clean = re.sub(r'\([^)]+\)', '', italian_text).strip()

    # Extract gender
    gender = None
    if '(m)' in italian_text:
        gender = 'masculine'
    elif '(f)' in italian_text:
        gender = 'feminine'

    # Determine word type (basic heuristic)
    word_type = 'phrase' if ' ' in clean else 'noun'  # Most GCSE vocab are nouns

    # Extract plural if present
    plural = None
    plural_match = re.search(r'\((.*?)\)(?!.*\()', italian_text)
    if plural_match and not plural_match.group(1) in ['m', 'f']:
        plural = plural_match.group(1)

    return clean, gender, word_type, plural


def get_english_translation(english_context, italian):
    """Generate basic English translation from context."""
    # This is a simplified version - ideally would use a translation API
    context_map = {
        'Espressioni di tempo': 'time expression',
        'Il cibo e le bevande': 'food/drink',
        'Saluti': 'greeting',
        'La famiglia': 'family',
        'I giorni della settimana': 'day of week',
        'I mesi': 'month',
        'Le stagioni': 'season',
    }

    # Return context hint as placeholder
    return context_map.get(english_context, f"[{english_context}]")


def import_gcse_vocabulary(db_path):
    """Import GCSE vocabulary from JSON file."""
    json_path = Path(__file__).parent / 'cambridge_gcse_vocab_final.json'

    if not json_path.exists():
        print(f"❌ JSON file not found: {json_path}")
        return 0

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Load JSON data
    with open(json_path, 'r', encoding='utf-8') as f:
        vocab_data = json.load(f)

    imported_count = 0
    skipped_count = 0

    for entry in vocab_data:
        italian_raw = entry.get('italian', '')
        english_context = entry.get('english_context', '')
        category = entry.get('category', '')

        # Skip category headers
        if not english_context or 'Attività giornaliere' in italian_raw:
            skipped_count += 1
            continue

        # Parse Italian word
        italian, gender, word_type, plural = parse_italian_word(italian_raw)

        if not italian:
            skipped_count += 1
            continue

        # Get English translation (placeholder)
        english = get_english_translation(english_context, italian)

        # Insert into database
        try:
            cursor.execute("""
                INSERT INTO vocabulary (italian, english, word_type, gender, plural, level, category)
                VALUES (?, ?, ?, ?, ?, 'GCSE', ?)
            """, (italian, english, word_type, gender, plural, f"GCSE-{category}"))
            imported_count += 1
        except sqlite3.IntegrityError:
            # Word already exists
            skipped_count += 1
        except Exception as e:
            print(f"⚠️  Error importing '{italian}': {e}")
            skipped_count += 1

    conn.commit()
    conn.close()

    print(f"✓ Imported {imported_count} GCSE vocabulary entries")
    print(f"  Skipped {skipped_count} entries (headers/duplicates)")

    return imported_count


def add_b1_sentences(db_path):
    """Add B1 level sentence translation examples."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    b1_sentences = [
        ("Quando ero piccolo, giocavo sempre al parco.", "When I was little, I always played in the park.", "B1"),
        ("Se avessi tempo, viaggerei di più.", "If I had time, I would travel more.", "B1"),
        ("Spero che tu stia bene.", "I hope you are well.", "B1"),
        ("Non sapevo che tu fossi arrivato.", "I didn't know that you had arrived.", "B1"),
        ("Dopo aver mangiato, siamo usciti.", "After eating, we went out.", "B1"),
        ("È importante che tu capisca.", "It's important that you understand.", "B1"),
        ("Pensavo che fosse troppo tardi.", "I thought it was too late.", "B1"),
        ("Sebbene piova, usciremo lo stesso.", "Although it's raining, we'll go out anyway.", "B1"),
        ("Mi ha detto di aspettare.", "He told me to wait.", "B1"),
        ("Vorrei che tu venissi con me.", "I wish you would come with me.", "B1"),
    ]

    imported_count = 0
    for italian, english, level in b1_sentences:
        try:
            cursor.execute("""
                INSERT INTO sentences (italian, english, level)
                VALUES (?, ?, ?)
            """, (italian, english, level))
            imported_count += 1
        except:
            pass  # Table might not exist or sentence already added

    conn.commit()
    conn.close()

    print(f"✓ Added {imported_count} B1 sentence examples")
    return imported_count


def add_b2_sentences(db_path):
    """Add B2 level sentence translation examples."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    b2_sentences = [
        ("Se avessi saputo, sarei venuto prima.", "If I had known, I would have come earlier.", "B2"),
        ("Nonostante avesse studiato molto, non ha superato l'esame.", "Despite having studied a lot, he didn't pass the exam.", "B2"),
        ("Qualora ci fossero problemi, chiamami.", "Should there be any problems, call me.", "B2"),
        ("Avendo finito il lavoro, sono andato a casa.", "Having finished work, I went home.", "B2"),
        ("È stato detto che la situazione migliorerebbe.", "It was said that the situation would improve.", "B2"),
        ("Benché fosse stanco, ha continuato a lavorare.", "Although he was tired, he continued working.", "B2"),
        ("Suppongo che abbiano già mangiato.", "I suppose they have already eaten.", "B2"),
        ("Era necessario che tutti fossero presenti.", "It was necessary that everyone be present.", "B2"),
        ("Facendo così, otterrai migliori risultati.", "By doing this, you'll get better results.", "B2"),
        ("Non che io sappia.", "Not that I know of.", "B2"),
    ]

    imported_count = 0
    for italian, english, level in b2_sentences:
        try:
            cursor.execute("""
                INSERT INTO sentences (italian, english, level)
                VALUES (?, ?, ?)
            """, (italian, english, level))
            imported_count += 1
        except:
            pass  # Table might not exist or sentence already added

    conn.commit()
    conn.close()

    print(f"✓ Added {imported_count} B2 sentence examples")
    return imported_count


def main():
    """Main execution function."""
    print("="*60)
    print("Italian Learning Companion - Content Import")
    print("Adding GCSE, B1, and B2 Content")
    print("="*60)
    print()

    if not DB_PATH.exists():
        print(f"❌ Database not found: {DB_PATH}")
        print("   Please run import_data.py first to create the database.")
        return

    # Import GCSE vocabulary
    print("Importing GCSE vocabulary...")
    gcse_count = import_gcse_vocabulary(DB_PATH)
    print()

    # Add B1 sentences
    print("Adding B1 sentence examples...")
    b1_count = add_b1_sentences(DB_PATH)
    print()

    # Add B2 sentences
    print("Adding B2 sentence examples...")
    b2_count = add_b2_sentences(DB_PATH)
    print()

    print("="*60)
    print("✓ Import Complete!")
    print(f"  - {gcse_count} GCSE vocabulary entries")
    print(f"  - {b1_count} B1 sentences")
    print(f"  - {b2_count} B2 sentences")
    print("="*60)


if __name__ == "__main__":
    main()
