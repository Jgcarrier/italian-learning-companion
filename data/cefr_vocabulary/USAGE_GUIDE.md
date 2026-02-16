# CEFR Vocabulary Usage Guide

## Quick Reference

### Database Location
```
/Users/jamescarrier/Desktop/Parkinglot/Code-Projects/italian-learning-companion/data/curriculum.db
```

### JSON Files Location
```
/Users/jamescarrier/Desktop/Parkinglot/Code-Projects/italian-learning-companion/data/cefr_vocabulary/
```

---

## Database Query Examples

### Get all vocabulary for a specific level
```sql
SELECT * FROM vocabulary WHERE level = 'A1' ORDER BY italian;
```

### Get all nouns with gender information
```sql
SELECT italian, english, gender
FROM vocabulary
WHERE word_type = 'noun' AND gender IS NOT NULL
ORDER BY level, italian;
```

### Get verbs by level
```sql
SELECT italian, english, level
FROM vocabulary
WHERE word_type = 'verb'
ORDER BY level, italian;
```

### Count vocabulary by level
```sql
SELECT level, COUNT(*) as count
FROM vocabulary
GROUP BY level
ORDER BY level;
```

### Find vocabulary that needs translation
```sql
SELECT italian, word_type, gender, level
FROM vocabulary
WHERE english = 'Translation needed'
ORDER BY level, italian;
```

### Get random words for practice (10 random A1 words)
```sql
SELECT italian, english, word_type
FROM vocabulary
WHERE level = 'A1'
ORDER BY RANDOM()
LIMIT 10;
```

### Get all masculine nouns for a level
```sql
SELECT italian, english
FROM vocabulary
WHERE level = 'A1'
  AND word_type = 'noun'
  AND gender = 'masculine';
```

### Search for specific words
```sql
SELECT * FROM vocabulary
WHERE italian LIKE '%casa%'
ORDER BY level;
```

---

## Python Usage Examples

### Connect to Database
```python
import sqlite3

db_path = '/Users/jamescarrier/Desktop/Parkinglot/Code-Projects/italian-learning-companion/data/curriculum.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
```

### Get Level Vocabulary
```python
def get_vocabulary_by_level(level):
    cursor.execute("""
        SELECT italian, english, word_type, gender
        FROM vocabulary
        WHERE level = ?
        ORDER BY italian
    """, (level,))
    return cursor.fetchall()

# Usage
a1_vocab = get_vocabulary_by_level('A1')
```

### Get Vocabulary by Type
```python
def get_vocabulary_by_type(level, word_type):
    cursor.execute("""
        SELECT italian, english, gender
        FROM vocabulary
        WHERE level = ? AND word_type = ?
        ORDER BY italian
    """, (level, word_type))
    return cursor.fetchall()

# Usage
a1_nouns = get_vocabulary_by_type('A1', 'noun')
```

### Random Vocabulary for Practice
```python
def get_random_vocabulary(level, count=10):
    cursor.execute("""
        SELECT italian, english, word_type
        FROM vocabulary
        WHERE level = ?
        ORDER BY RANDOM()
        LIMIT ?
    """, (level, count))
    return cursor.fetchall()

# Usage
practice_words = get_random_vocabulary('A2', 20)
```

### Load from JSON
```python
import json

def load_cefr_json(level):
    file_path = f'/Users/jamescarrier/Desktop/Parkinglot/Code-Projects/italian-learning-companion/data/cefr_vocabulary/cefr_{level.lower()}_vocabulary.json'
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Usage
a1_vocab = load_cefr_json('A1')
```

---

## Vocabulary Statistics

### Overall Distribution
- **Total CEFR Words:** 5,123
- **Nouns:** 2,879 (56%)
- **Verbs:** 782 (15%)
- **Adjectives:** 712 (14%)
- **Adverbs:** 272 (5%)
- **Other:** 478 (9%)

### Gender Distribution (Nouns)
- **Masculine:** 1,548 (54%)
- **Feminine:** 1,176 (41%)
- **Both:** 154 (5%)

### Progressive Growth
- **A1:** 485 words (foundation)
- **A2:** 1,033 words (+548 new)
- **B1:** 1,533 words (+500 new)
- **B2:** 2,072 words (+539 new)

---

## Word Type Categories

### Primary Categories
1. **noun** - Nouns (with gender: masculine, feminine, both)
2. **verb** - All verb forms
3. **adjective** - Descriptive words
4. **adverb** - Modifying words
5. **pronoun** - Pronouns
6. **preposition** - Prepositions
7. **article** - Articles (il, la, i, le, etc.)
8. **conjunction** - Conjunctions (e, ma, o, etc.)
9. **interjection** - Exclamations (ciao, grazie, etc.)

### Gender Values
- **masculine** - Masculine nouns (il ragazzo)
- **feminine** - Feminine nouns (la ragazza)
- **both** - Words with both forms (amico/amica)
- **null** - No gender (verbs, adjectives, etc.)

---

## Integration Ideas

### 1. Flashcard System
```python
def create_flashcard_deck(level, word_type=None):
    query = "SELECT italian, english FROM vocabulary WHERE level = ?"
    params = [level]

    if word_type:
        query += " AND word_type = ?"
        params.append(word_type)

    query += " ORDER BY RANDOM()"
    cursor.execute(query, params)
    return cursor.fetchall()
```

### 2. Gender Practice
```python
def get_gender_practice(level, count=20):
    cursor.execute("""
        SELECT italian, gender
        FROM vocabulary
        WHERE level = ?
          AND word_type = 'noun'
          AND gender IS NOT NULL
        ORDER BY RANDOM()
        LIMIT ?
    """, (level, count))
    return cursor.fetchall()
```

### 3. Verb Conjugation Practice
```python
def get_verbs_for_practice(level):
    cursor.execute("""
        SELECT italian, english
        FROM vocabulary
        WHERE level = ? AND word_type = 'verb'
        ORDER BY italian
    """, (level,))
    return cursor.fetchall()
```

### 4. Vocabulary Quiz Generator
```python
def generate_quiz(level, count=10):
    cursor.execute("""
        SELECT italian, english, word_type, gender
        FROM vocabulary
        WHERE level = ? AND english != 'Translation needed'
        ORDER BY RANDOM()
        LIMIT ?
    """, (level, count))
    return cursor.fetchall()
```

### 5. Progressive Learning Path
```python
def get_learning_path():
    """Get vocabulary in progressive order"""
    levels = ['A1', 'A2', 'B1', 'B2']
    learning_path = {}

    for level in levels:
        cursor.execute("""
            SELECT italian, english, word_type
            FROM vocabulary
            WHERE level = ?
            ORDER BY word_type, italian
        """, (level,))
        learning_path[level] = cursor.fetchall()

    return learning_path
```

---

## Translation Integration

### Add Translations via API
```python
def add_translation(word_id, english_translation):
    cursor.execute("""
        UPDATE vocabulary
        SET english = ?
        WHERE id = ?
    """, (english_translation, word_id))
    conn.commit()

def get_words_needing_translation(level=None):
    query = "SELECT id, italian, level FROM vocabulary WHERE english = 'Translation needed'"
    if level:
        query += " AND level = ?"
        cursor.execute(query, (level,))
    else:
        cursor.execute(query)
    return cursor.fetchall()
```

### Bulk Translation Script Template
```python
import deepl  # or googletrans

def bulk_translate_vocabulary(level):
    words = get_words_needing_translation(level)
    translator = deepl.Translator("YOUR_API_KEY")

    for word_id, italian, level in words:
        try:
            translation = translator.translate_text(italian, target_lang="EN-US")
            add_translation(word_id, translation.text)
            print(f"Translated: {italian} -> {translation.text}")
        except Exception as e:
            print(f"Error translating {italian}: {e}")
```

---

## Data Quality Checks

### Find Potential Duplicates
```sql
SELECT italian, level, COUNT(*) as count
FROM vocabulary
GROUP BY italian, level
HAVING count > 1;
```

### Check for Missing Gender on Nouns
```sql
SELECT italian, level
FROM vocabulary
WHERE word_type = 'noun' AND gender IS NULL
ORDER BY level, italian;
```

### Words Without Translation
```sql
SELECT level, COUNT(*) as needs_translation
FROM vocabulary
WHERE english = 'Translation needed'
GROUP BY level;
```

---

## Rerunning Import Script

If you need to reimport or update the vocabulary:

```bash
cd /Users/jamescarrier/Desktop/Parkinglot/Code-Projects/italian-learning-companion
python3 scripts/import_cefr_vocabulary.py
```

The script will:
1. Extract vocabulary from PDF text files
2. Skip existing entries (duplicate detection)
3. Generate comprehensive statistics
4. Create JSON backup files
5. Import new entries to database

---

## Backup and Restore

### Backup Database
```bash
cp /Users/jamescarrier/Desktop/Parkinglot/Code-Projects/italian-learning-companion/data/curriculum.db \
   /Users/jamescarrier/Desktop/Parkinglot/Code-Projects/italian-learning-companion/data/curriculum.db.backup
```

### Export Vocabulary to CSV
```bash
sqlite3 -header -csv /Users/jamescarrier/Desktop/Parkinglot/Code-Projects/italian-learning-companion/data/curriculum.db \
  "SELECT * FROM vocabulary ORDER BY level, italian" > vocabulary_export.csv
```

### Export by Level
```bash
sqlite3 -header -csv /Users/jamescarrier/Desktop/Parkinglot/Code-Projects/italian-learning-companion/data/curriculum.db \
  "SELECT * FROM vocabulary WHERE level = 'A1'" > a1_vocabulary.csv
```

---

## Tips for Learning Application Integration

1. **Start with A1:** Focus on A1 vocabulary for beginners (485 essential words)

2. **Progressive Unlocking:** Unlock levels progressively (A1 → A2 → B1 → B2)

3. **Gender Focus:** Emphasize gender learning for nouns from the start

4. **Verb Conjugation:** Integrate verb conjugation practice with verb vocabulary

5. **Thematic Grouping:** Consider adding category tags for thematic learning

6. **Spaced Repetition:** Use the data with spaced repetition algorithms (Anki, SM-2)

7. **Context Examples:** Add example sentences to make vocabulary memorable

8. **Audio Integration:** Consider adding pronunciation audio for each word

9. **Common Words First:** Within each level, prioritize high-frequency words

10. **Review System:** Build review systems that incorporate words from previous levels

---

## Support and Maintenance

- **JSON Files:** Use as backup or for migration to other systems
- **Import Script:** Reusable for future vocabulary updates
- **Database Schema:** Extensible for additional fields (pronunciation, audio_url, frequency, etc.)
- **Documentation:** Keep this guide updated with new features

---

## Contact Information

For questions about the vocabulary data or import process, refer to:
- **Import Summary:** `IMPORT_SUMMARY.md`
- **Import Script:** `/scripts/import_cefr_vocabulary.py`
- **Source PDFs:** `/Italian Docs (JC saved down)/`
