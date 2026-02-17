#!/usr/bin/env python3
"""
Generate 120 reading comprehension stories for Italian Learning Companion.
24 stories per level × 5 levels (A1, A2, B1, B2, GCSE).

Each story includes:
- Title
- Italian text (appropriate length and complexity for level)
- Vocabulary hints
- 5 comprehension questions with multiple choice answers
"""

import json
from pathlib import Path
from typing import List, Dict

# Story templates and data
STORIES_A1 = [
    {
        "id": "a1_001",
        "title": "La Giornata di Maria",
        "text": """Maria si sveglia alle sette. Fa colazione con latte e biscotti. Poi va a scuola in autobus.

A scuola, Maria studia italiano, matematica e inglese. Le piace molto l'inglese.

A mezzogiorno, Maria mangia in mensa con le sue amiche. Mangiano pasta e insalata.

Nel pomeriggio, Maria torna a casa. Fa i compiti e guarda la televisione.

La sera, Maria cena con la famiglia. Mangiano insieme alle sette e mezza. Dopo cena, Maria legge un libro. Va a letto alle dieci.""",
        "vocab_hints": "si sveglia = wakes up, fa colazione = has breakfast, mensa = canteen, compiti = homework",
        "questions": [
            {"question": "What time does Maria wake up?", "choices": ["6:00", "7:00", "8:00", "9:00"], "correct": "7:00"},
            {"question": "How does Maria go to school?", "choices": ["by car", "by bus", "by bike", "on foot"], "correct": "by bus"},
            {"question": "Which subject does Maria like?", "choices": ["Math", "Italian", "English", "Science"], "correct": "English"},
            {"question": "What does Maria eat for lunch?", "choices": ["pizza", "pasta and salad", "soup", "fish"], "correct": "pasta and salad"},
            {"question": "What time does Maria go to bed?", "choices": ["9:00", "10:00", "11:00", "12:00"], "correct": "10:00"}
        ]
    },
    {
        "id": "a1_002",
        "title": "La Famiglia di Marco",
        "text": """Marco ha una famiglia grande. Suo padre si chiama Giuseppe e lavora in un ufficio. Sua madre si chiama Anna ed è insegnante.

Marco ha due fratelli: Luca e Sofia. Luca ha quindici anni e Sofia ha dodici anni. Marco ha tredici anni.

La famiglia abita in un appartamento in centro. L'appartamento ha tre camere da letto, un salotto, una cucina e due bagni.

Marco ama la sua famiglia. Il weekend, la famiglia va sempre al parco o al cinema insieme.

Il cane della famiglia si chiama Max. Max è grande e marrone. Tutti amano Max.""",
        "vocab_hints": "fratelli = siblings/brothers, appartamento = apartment, camere da letto = bedrooms, cane = dog",
        "questions": [
            {"question": "What does Marco's father do?", "choices": ["teacher", "works in office", "doctor", "chef"], "correct": "works in office"},
            {"question": "How many siblings does Marco have?", "choices": ["1", "2", "3", "4"], "correct": "2"},
            {"question": "How old is Marco?", "choices": ["12", "13", "14", "15"], "correct": "13"},
            {"question": "Where does the family live?", "choices": ["house", "apartment", "farm", "villa"], "correct": "apartment"},
            {"question": "What is the dog's name?", "choices": ["Rex", "Fido", "Max", "Bruno"], "correct": "Max"}
        ]
    }
]

# This is just a starting template - we'll need to generate 24 per level
# For now, let's create a framework that can be expanded

def generate_all_stories():
    """Generate all 120 reading stories and save to JSON files."""

    output_dir = Path(__file__).parent / "data" / "reading_stories"
    output_dir.mkdir(parents=True, exist_ok=True)

    levels = {
        "A1": generate_a1_stories(),
        "A2": generate_a2_stories(),
        "B1": generate_b1_stories(),
        "B2": generate_b2_stories(),
        "GCSE": generate_gcse_stories()
    }

    for level, stories in levels.items():
        output_file = output_dir / f"{level.lower()}_stories.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(stories, f, ensure_ascii=False, indent=2)

        print(f"✓ Created {level}: {len(stories)} stories → {output_file.name}")

    print(f"\nTotal stories created: {sum(len(s) for s in levels.values())}")

def generate_a1_stories() -> List[Dict]:
    """Generate 24 A1-level stories (100-150 words, present tense, basic vocabulary)."""
    return STORIES_A1  # TODO: Expand to 24 stories

def generate_a2_stories() -> List[Dict]:
    """Generate 24 A2-level stories (150-200 words, past tense, wider vocabulary)."""
    return []  # TODO: Generate 24 stories

def generate_b1_stories() -> List[Dict]:
    """Generate 24 B1-level stories (200-250 words, subjunctive, complex clauses)."""
    return []  # TODO: Generate 24 stories

def generate_b2_stories() -> List[Dict]:
    """Generate 24 B2-level stories (250-300 words, advanced grammar, sophisticated vocabulary)."""
    return []  # TODO: Generate 24 stories

def generate_gcse_stories() -> List[Dict]:
    """Generate 24 GCSE-level stories (similar to B1 but UK curriculum topics)."""
    return []  # TODO: Generate 24 stories

if __name__ == "__main__":
    generate_all_stories()
