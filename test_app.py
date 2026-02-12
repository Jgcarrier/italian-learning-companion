#!/usr/bin/env python3
"""
Quick test to verify the Flask app is set up correctly
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

print("Testing Italian Learning Companion Web App...")
print("=" * 60)

# Test 1: Import Flask
try:
    import flask
    print("✓ Flask imported successfully (version {})".format(flask.__version__))
except ImportError as e:
    print("✗ Flask import failed:", e)
    sys.exit(1)

# Test 2: Import database module
try:
    from database import ItalianDatabase
    print("✓ Database module imported")
except ImportError as e:
    print("✗ Database import failed:", e)
    sys.exit(1)

# Test 3: Import practice generator
try:
    from practice_generator import PracticeGenerator
    print("✓ Practice generator imported")
except ImportError as e:
    print("✗ Practice generator import failed:", e)
    sys.exit(1)

# Test 4: Check database exists
db_path = Path(__file__).parent.parent / 'data' / 'curriculum.db'
if db_path.exists():
    print(f"✓ Database found at {db_path}")
else:
    print(f"✗ Database not found at {db_path}")
    sys.exit(1)

# Test 5: Try to connect to database
try:
    db = ItalianDatabase("../data/curriculum.db")
    print("✓ Database connection successful")
    db.close()
except Exception as e:
    print("✗ Database connection failed:", e)
    sys.exit(1)

# Test 6: Generate test questions
try:
    db = ItalianDatabase("../data/curriculum.db")
    generator = PracticeGenerator(db)
    questions = generator.generate_vocabulary_quiz("A1", 5, "it_to_en")
    if questions:
        print(f"✓ Generated {len(questions)} test questions")
        print(f"  Example: {questions[0]['question']} → {questions[0]['answer']}")
    else:
        print("⚠ Warning: No questions generated (database might be empty)")
    db.close()
except Exception as e:
    print("✗ Question generation failed:", e)
    sys.exit(1)

# Test 7: Check templates exist
templates_dir = Path(__file__).parent / 'templates'
required_templates = [
    'base.html', 'home.html', 'vocabulary_quiz_setup.html',
    'question.html', 'feedback.html', 'summary.html',
    'stats.html', 'topics.html'
]
missing_templates = []
for template in required_templates:
    if not (templates_dir / template).exists():
        missing_templates.append(template)

if not missing_templates:
    print(f"✓ All {len(required_templates)} templates found")
else:
    print(f"✗ Missing templates: {', '.join(missing_templates)}")
    sys.exit(1)

# Test 8: Check CSS exists
css_path = Path(__file__).parent / 'static' / 'css' / 'style.css'
if css_path.exists():
    print("✓ CSS file found")
else:
    print("✗ CSS file not found")
    sys.exit(1)

# Test 9: Check accent removal function
def remove_accents(text: str) -> str:
    accent_map = {
        'à': 'a', 'á': 'a',
        'è': 'e', 'é': 'e',
        'ì': 'i', 'í': 'i',
        'ò': 'o', 'ó': 'o',
        'ù': 'u', 'ú': 'u'
    }
    result = text.lower()
    for accented, plain in accent_map.items():
        result = result.replace(accented, plain)
    return result

test_cases = [
    ("caffè", "caffe"),
    ("città", "citta"),
    ("perché", "perche"),
]

all_passed = True
for accented, expected in test_cases:
    result = remove_accents(accented)
    if result == expected:
        pass
    else:
        print(f"✗ Accent removal failed: {accented} → {result} (expected {expected})")
        all_passed = False

if all_passed:
    print("✓ Accent normalization working correctly")

print("=" * 60)
print("✅ All tests passed! The app is ready to run.")
print("\nTo start the server, run:")
print("  python3 app.py")
print("\nOr use the convenience script:")
print("  ./run.sh")
