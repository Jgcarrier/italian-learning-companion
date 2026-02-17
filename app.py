"""
Italian Learning Companion - Flask Web Application
"""

import sys
import os
import logging
import json
import random
from pathlib import Path
from flask import Flask, render_template, request, session, redirect, url_for, jsonify, g
import time
from datetime import datetime

# Add src directory to path so we can import existing modules
# Try local src/ first (for deployment), then parent (for development)
current_dir = Path(__file__).parent
if (current_dir / 'src').exists():
    sys.path.insert(0, str(current_dir / 'src'))
else:
    sys.path.insert(0, str(current_dir.parent / 'src'))

from database import ItalianDatabase
from practice_generator import PracticeGenerator

app = Flask(__name__)
# Use environment variable in production, fallback to development key
app.secret_key = os.environ.get('SECRET_KEY', 'italian-learning-companion-secret-key-2024')

# Configure logging
if not app.debug:
    # Production logging
    handler = logging.StreamHandler()
    handler.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.ERROR)
else:
    # Development logging
    app.logger.setLevel(logging.INFO)

# Database path - use absolute path to avoid path resolution issues
# Try local data/ first (deployment), then parent (development)
if (current_dir / 'data' / 'curriculum.db').exists():
    DB_PATH = str(current_dir / 'data' / 'curriculum.db')
else:
    DB_PATH = str(current_dir.parent / 'data' / 'curriculum.db')

# Simple in-memory cache for static data (vocabulary lists, verb lists)
# Cache expires when app restarts - perfect for static database content
_CACHE = {
    'vocab_by_level': {},
    'verbs_by_level': {},
    'cache_time': None
}


def get_db():
    """Get a database connection for the current request, reusing if available."""
    if 'db' not in g:
        g.db = ItalianDatabase(DB_PATH)
    return g.db


def get_generator():
    """Get a practice generator with the current request's database connection."""
    return PracticeGenerator(get_db())


def get_cached_vocab_count(level: str) -> int:
    """Get vocabulary count for a level from cache or database."""
    if level not in _CACHE['vocab_by_level']:
        db = get_db()
        cursor = db.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM vocabulary WHERE level = ?', (level,))
        count = cursor.fetchone()[0]
        _CACHE['vocab_by_level'][level] = count
    return _CACHE['vocab_by_level'][level]


def get_cached_verb_count(level: str) -> int:
    """Get verb count for a level from cache or database."""
    # GCSE uses B2 verbs
    query_level = 'B2' if level == 'GCSE' else level

    if query_level not in _CACHE['verbs_by_level']:
        db = get_db()
        cursor = db.conn.cursor()
        cursor.execute('SELECT COUNT(DISTINCT infinitive) FROM verb_conjugations WHERE level = ?', (query_level,))
        count = cursor.fetchone()[0]
        _CACHE['verbs_by_level'][query_level] = count
    return _CACHE['verbs_by_level'][query_level]


@app.teardown_appcontext
def close_db(error):
    """Close the database connection at the end of the request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()


# Constants for validation
VALID_LEVELS = ['A1', 'A2', 'B1', 'B2', 'GCSE']
DEFAULT_QUESTION_COUNT = 10
MIN_QUESTION_COUNT = 1
MAX_QUESTION_COUNT = 50

# Practice type to route mapping for summary page
# Format: practice_type -> (route_name, required_params)
PRACTICE_ROUTES = {
    'vocabulary_quiz': ('vocabulary_quiz', ['level', 'direction']),
    'verb_conjugation': ('verb_conjugation', ['level']),
    'regular_passato': ('regular_passato', ['level']),
    'irregular_passato': ('irregular_passato', ['level']),
    'imperfect_tense': ('imperfect_tense', ['level']),
    'auxiliary_choice': ('auxiliary_choice', ['level']),
    'futuro_semplice': ('futuro_semplice', ['level']),
    'reflexive_verbs': ('reflexive_verbs', ['level']),
    'noun_gender_number': ('noun_gender_number', ['level']),
    'articulated_prepositions': ('articulated_prepositions', ['level']),
    'time_prepositions': ('time_prepositions', ['level']),
    'negations': ('negations', ['level']),
    'fill_in_blank': ('fill_in_blank', ['level']),
    'multiple_choice': ('multiple_choice', ['level']),
    'sentence_translation': ('sentence_translator', ['level', 'direction']),
    'present_tense': ('present_tense', ['level']),
    'pronouns': ('pronouns', ['level']),
    'conditional_present': ('conditional_present', ['level']),
    'imperative': ('imperative', ['level']),
    'adverbs': ('adverbs', ['level']),
    'subjunctive_present': ('subjunctive_present', ['level']),
    'pronominal_verbs': ('pronominal_verbs', ['level']),
    'passive_voice': ('passive_voice', ['level']),
    'combined_pronouns': ('combined_pronouns', ['level']),
    'conditional_past': ('conditional_past', ['level']),
    'past_perfect': ('past_perfect', ['level']),
    'subjunctive_past': ('subjunctive_past', ['level']),
    'subjunctive_imperfect': ('subjunctive_imperfect', ['level']),
    'subjunctive_past_perfect': ('subjunctive_past_perfect', ['level']),
    'passato_remoto': ('passato_remoto', ['level']),
    'impersonal_si': ('impersonal_si', ['level']),
    'relative_pronouns': ('relative_pronouns', ['level']),
    'comprehensive_subjunctives': ('comprehensive_subjunctives', ['level']),
    'unreal_past': ('unreal_past', ['level']),
    'unreal_present': ('unreal_present', ['level']),
    'progressive_gerund': ('progressive_gerund', ['level']),
    'causative': ('causative', ['level']),
    'advanced_pronouns': ('advanced_pronouns', ['level']),
}


def validate_level(level: str) -> str:
    """Validate and return a safe level value."""
    if level not in VALID_LEVELS:
        return 'A2'  # Safe default
    return level


def validate_count(count_str: str) -> int:
    """Validate and return a safe question count."""
    try:
        count = int(count_str)
        if count < MIN_QUESTION_COUNT:
            return MIN_QUESTION_COUNT
        if count > MAX_QUESTION_COUNT:
            return MAX_QUESTION_COUNT
        return count
    except (ValueError, TypeError):
        return DEFAULT_QUESTION_COUNT


def create_practice_route(practice_type: str, generator_method: str, setup_template: str,
                          menu_type: str = 'verbs_menu', requires_level: bool = False):
    """
    Factory function to create standardized practice route handlers.

    Args:
        practice_type: Type identifier for the practice (e.g., 'verb_conjugation')
        generator_method: Name of the method on PracticeGenerator (e.g., 'generate_verb_conjugation_drill')
        setup_template: Template name for the setup page (e.g., 'verb_conjugation_setup.html')
        menu_type: The menu to return to on error (default: 'verbs_menu')
        requires_level: Whether the generator method takes level as first param (default: False)

    Returns:
        A Flask route handler function
    """
    def route_handler():
        level = validate_level(request.args.get('level') or request.form.get('level') or session.get('level', 'A2'))

        if request.method == 'GET':
            session['level'] = level
            return render_template(setup_template, level=level)

        # POST: Start new practice
        count = validate_count(request.form.get('count', 10))
        generator = get_generator()

        # Call the generator method
        method = getattr(generator, generator_method)
        if requires_level:
            questions = method(level, count)
        else:
            questions = method(count)

        # Check if questions were generated
        if not questions or len(questions) == 0:
            session['level'] = level
            return render_template('error.html',
                                 error_message=f"No {practice_type.replace('_', ' ')} exercises available for {level}. Please try a different level.",
                                 back_link=url_for(menu_type, level=level))

        # Store in session
        session['practice_type'] = practice_type
        session['questions'] = questions
        session['current_question'] = 0
        session['correct_count'] = 0
        session['answers'] = []
        session['start_time'] = time.time()
        session['level'] = level

        return redirect(url_for('practice_question'))

    return route_handler


def get_menu_for_practice_type(practice_type: str) -> str:
    """Get the appropriate menu route for a given practice type."""
    verb_types = ['verb_conjugation', 'irregular_passato', 'auxiliary_choice',
                  'imperfect_tense', 'futuro_semplice', 'reflexive_verbs', 'regular_passato',
                  'conditional_present']
    grammar_types = ['noun_gender_number', 'articulated_prepositions',
                     'time_prepositions', 'negations', 'pronouns', 'adverbs', 'imperative']
    vocabulary_types = ['vocabulary_quiz', 'sentence_translator']
    mixed_types = ['fill_in_blank', 'multiple_choice']
    reading_types = ['reading_comprehension']

    if practice_type in verb_types:
        return 'verbs_menu'
    elif practice_type in grammar_types:
        return 'grammar_menu'
    elif practice_type in vocabulary_types:
        return 'vocabulary_menu'
    elif practice_type in mixed_types:
        return 'mixed_menu'
    elif practice_type in reading_types:
        return 'reading_menu'
    else:
        return 'category_menu'


def remove_accents(text: str) -> str:
    """Remove Italian accents from text for flexible answer checking."""
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


def get_etymology_fact(word: str) -> str:
    """Get an interesting etymology fact for Italian vocabulary words."""
    etymology_facts = {
        # Days of the week
        'lunedì': 'Named after Luna (the Moon) - "Moon\'s day"',
        'martedì': 'Named after Mars (god of war) - "Mars\' day"',
        'mercoledì': 'Named after Mercury (god of commerce) - "Mercury\'s day"',
        'giovedì': 'Named after Jupiter/Jove (king of gods) - "Jupiter\'s day"',
        'venerdì': 'Named after Venus (goddess of love) - "Venus\' day"',
        'sabato': 'From Hebrew "Shabbat" (day of rest)',
        'domenica': 'From Latin "dies dominica" (the Lord\'s day)',

        # Common words
        'caffè': 'From Turkish "kahve", originally from Arabic "qahwah"',
        'pasta': 'From Greek "pasta" meaning "barley porridge"',
        'pizza': 'Possibly from Greek "pitta" (flatbread) or Latin "pinsa" (to pound)',
        'ciao': 'From Venetian "s-ciào" meaning "I am your slave" (polite greeting)',
        'piano': 'Means "soft" or "slow", also related to "pianoforte" (soft-loud)',
        'solo': 'From Latin "solus" meaning "alone" - used worldwide in music',
        'soprano': 'From Italian "sopra" (above) - the highest singing voice',
        'maestro': 'From Latin "magister" (master/teacher)',
        'libretto': 'Diminutive of "libro" (book) - literally "little book"',
        'tempo': 'From Latin "tempus" (time) - used globally in music',
        'allegro': 'Means "cheerful/lively" in Italian, used in music for fast tempo',

        # Food and drink
        'vino': 'From Latin "vinum", one of the oldest cultivated words',
        'pane': 'From Latin "panis" - same root as English "pantry"',
        'acqua': 'From Latin "aqua" - root of "aquatic", "aquarium"',
        'formaggio': 'From Latin "formaticus" (made in a mold)',
        'gelato': 'From Latin "gelatus" (frozen) - related to "gelid"',
        'limone': 'From Arabic "laymūn" via Persian',
        'zucchero': 'From Arabic "sukkar" via Sanskrit "śárkarā" (gravel/sand)',

        # Common verbs
        'parlare': 'From Latin "parabola" (parable/speech) via Greek',
        'mangiare': 'From Latin "manducare" (to chew)',
        'bere': 'From Latin "bibere" (to drink) - root of "beverage"',
        'dormire': 'From Latin "dormire" - root of "dormitory"',
        'studiare': 'From Latin "studium" (zeal/study) - root of "student"',

        # Colors
        'rosso': 'From Latin "russus" (red) - related to "rust"',
        'bianco': 'From Germanic "blank" (white/shining)',
        'nero': 'From Latin "niger" (black)',
        'verde': 'From Latin "viridis" (green) - root of "verdant"',
        'azzurro': 'From Persian "lāžward" (lapis lazuli stone)',

        # Family
        'madre': 'From Latin "mater" - one of the oldest human words',
        'padre': 'From Latin "pater" - found in similar forms across Indo-European languages',
        'fratello': 'From Latin "fraternus" (brotherly) - root of "fraternity"',
        'sorella': 'From Latin "soror" (sister) - root of "sorority"',
    }

    # Remove articles and normalize
    word_clean = word.lower().replace('il ', '').replace('la ', '').replace('i ', '').replace('le ', '').replace('gli ', '').replace('lo ', '').replace("l'", '').strip()

    return etymology_facts.get(word_clean, None)


def check_answer(user_answer: str, correct_answer: str, question_type: str = None) -> tuple[bool, str]:
    """
    Check if user answer matches the correct answer with flexible matching.

    Returns:
        (is_correct, display_answer) - bool indicating correctness, and the answer to display

    Handles:
    - Accent-forgiving matching
    - Multiple acceptable answers separated by "/" (e.g., "small/low")
    - Optional "to" for verb infinitives (e.g., "to speak" or "speak")
    - Number flexibility (e.g., "27" = "twenty-seven", "3" = "three")
    - Extra whitespace
    - Sentence translation: Very lenient, checks if key words are present
    """
    import re

    user_normalized = remove_accents(user_answer.strip().lower())
    correct_normalized = remove_accents(correct_answer.strip().lower())

    # Number word to digit mapping
    number_words = {
        'zero': '0', 'one': '1', 'two': '2', 'three': '3', 'four': '4', 'five': '5',
        'six': '6', 'seven': '7', 'eight': '8', 'nine': '9', 'ten': '10',
        'eleven': '11', 'twelve': '12', 'thirteen': '13', 'fourteen': '14', 'fifteen': '15',
        'sixteen': '16', 'seventeen': '17', 'eighteen': '18', 'nineteen': '19', 'twenty': '20',
        'twenty-one': '21', 'twenty-two': '22', 'twenty-three': '23', 'twenty-four': '24',
        'twenty-five': '25', 'twenty-six': '26', 'twenty-seven': '27', 'twenty-eight': '28',
        'twenty-nine': '29', 'thirty': '30', 'forty': '40', 'fifty': '50', 'sixty': '60',
        'seventy': '70', 'eighty': '80', 'ninety': '90', 'hundred': '100'
    }

    # Create reverse mapping (digit to word)
    digit_to_word = {v: k for k, v in number_words.items()}

    # Convert numbers in both user and correct answers
    def normalize_numbers(text):
        """Convert number words to digits for comparison."""
        # Replace number words with digits
        for word, digit in number_words.items():
            text = re.sub(r'\b' + word + r'\b', digit, text)
        return text

    def denormalize_numbers(text):
        """Convert digits to number words for comparison."""
        # Replace digits with number words (sort by length desc to handle 27 before 7)
        for digit in sorted(digit_to_word.keys(), key=len, reverse=True):
            word = digit_to_word[digit]
            text = re.sub(r'\b' + digit + r'\b', word, text)
        return text

    user_with_digits = normalize_numbers(user_normalized)
    correct_with_digits = normalize_numbers(correct_normalized)
    user_with_words = denormalize_numbers(user_normalized)
    correct_with_words = denormalize_numbers(correct_normalized)

    # For sentence translation, use very flexible matching
    if question_type == 'sentence_translation':
        # Remove punctuation from both answers
        import string
        user_no_punct = user_with_digits.translate(str.maketrans('', '', string.punctuation))
        correct_no_punct = correct_with_digits.translate(str.maketrans('', '', string.punctuation))

        # Split into words
        user_words = user_no_punct.split()
        correct_words = correct_no_punct.split()

        # Remove common words that don't affect meaning (expanded list)
        stopwords = {
            'the', 'a', 'an', 'is', 'am', 'are', 'was', 'were', 'be', 'been', 'being',
            'il', 'lo', 'la', 'i', 'gli', 'le', "l'", 'un', 'una', 'uno',
            'di', 'da', 'in', 'con', 'su', 'per', 'tra', 'fra',
            'to', 'at', 'on', 'of', 'from', 'with', 'by', 'for'
        }

        # Keep words that are NOT stopwords
        user_content_words = [w for w in user_words if w not in stopwords]
        correct_content_words = [w for w in correct_words if w not in stopwords]

        # Also check for semantic equivalents
        synonyms = {
            'cinema': ['movies', 'movie', 'theater', 'theatre'],
            'movies': ['cinema', 'movie', 'theater', 'theatre'],
            'movie': ['cinema', 'movies', 'theater', 'theatre'],
            'theater': ['cinema', 'movies', 'movie', 'theatre'],
            'go': ['going', 'went'],
            'went': ['go', 'going'],
            'going': ['go', 'went'],
            'tired': ['sleepy', 'exhausted'],
            'hungry': ['starving'],
            'thirsty': ['parched'],
        }

        # Check matches with synonyms
        matches = 0
        for correct_word in correct_content_words:
            # Direct match
            if correct_word in user_content_words:
                matches += 1
            # Synonym match
            elif correct_word in synonyms:
                if any(syn in user_content_words for syn in synonyms[correct_word]):
                    matches += 1

        # Very lenient: accept if 50% of content words match
        if len(correct_content_words) > 0:
            similarity = matches / len(correct_content_words)

            # Accept if 50% of key words match (lowered from 70%)
            if similarity >= 0.5:
                return True, correct_answer

        # Also accept if user answer contains most of the correct answer
        if len(user_content_words) > 0 and len(correct_content_words) > 0:
            reverse_matches = sum(1 for word in user_content_words if word in correct_content_words or word in str(synonyms.get(word, [])))
            reverse_similarity = reverse_matches / len(user_content_words)
            if reverse_similarity >= 0.6:
                return True, correct_answer

    # Standard matching for other types
    # Split correct answer by "/" to get all acceptable answers
    acceptable_answers = [remove_accents(ans.strip().lower()) for ans in correct_answer.split('/')]

    # For each acceptable answer, also check variants
    all_acceptable = []
    for ans in acceptable_answers:
        all_acceptable.append(ans)
        # Also add the number-normalized version
        all_acceptable.append(normalize_numbers(ans))

        # If answer starts with "to ", also accept without "to"
        if ans.startswith('to '):
            all_acceptable.append(ans[3:])  # Remove "to "
            all_acceptable.append(normalize_numbers(ans[3:]))
        # If answer doesn't start with "to ", also accept with "to "
        else:
            # Check if this looks like a verb (heuristic: single word, not a noun with article)
            if ' ' not in ans and not ans.startswith(('il ', 'la ', 'i ', 'gli ', 'le ', "l'")):
                all_acceptable.append(f'to {ans}')
                all_acceptable.append(f'to {normalize_numbers(ans)}')

    # Check if user answer matches any acceptable variant (with or without number conversion)
    # Also normalize all acceptable answers for number comparison
    all_acceptable_normalized = []
    for acc in all_acceptable:
        all_acceptable_normalized.append(acc)
        all_acceptable_normalized.append(normalize_numbers(acc))
        all_acceptable_normalized.append(denormalize_numbers(acc))

    is_correct = (user_normalized in all_acceptable_normalized or
                  user_with_digits in all_acceptable_normalized or
                  user_with_words in all_acceptable_normalized)

    # For display, use the first option if multiple
    display_answer = correct_answer.split('/')[0] if '/' in correct_answer else correct_answer

    return is_correct, display_answer


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def page_not_found(error):
    """Handle 404 errors with user-friendly message."""
    return render_template('error.html',
                          error_message="Page not found. The page you're looking for doesn't exist.",
                          back_link=url_for('home')), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors with user-friendly message."""
    # Log the actual error for debugging
    app.logger.error(f'Internal error: {error}')

    # Close any open database connections
    db = g.pop('db', None)
    if db is not None:
        try:
            db.close()
        except:
            pass

    return render_template('error.html',
                          error_message="Something went wrong on our end. Please try again.",
                          back_link=url_for('home')), 500


@app.errorhandler(Exception)
def handle_exception(error):
    """Catch-all handler for unexpected exceptions."""
    # Log the actual error for debugging
    app.logger.error(f'Unhandled exception: {error}', exc_info=True)

    # Close any open database connections
    db = g.pop('db', None)
    if db is not None:
        try:
            db.close()
        except:
            pass

    # Return 500 error page
    return render_template('error.html',
                          error_message="An unexpected error occurred. Please try again.",
                          back_link=url_for('home')), 500


# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def home():
    """Home page - level selection."""
    return render_template('level_select.html')


@app.route('/category/<level>')
def category_menu(level):
    """Category menu for a specific level."""
    return render_template('category_menu.html', level=level)


@app.route('/verbs/<level>')
def verbs_menu(level):
    """Verbs submenu for a specific level."""
    return render_template('verbs_menu.html', level=level)


@app.route('/vocabulary/<level>')
def vocabulary_menu(level):
    """Vocabulary submenu for a specific level."""
    return render_template('vocabulary_menu.html', level=level)


@app.route('/grammar/<level>')
def grammar_menu(level):
    """Grammar submenu for a specific level."""
    return render_template('grammar_menu.html', level=level)


@app.route('/mixed/<level>')
def mixed_menu(level):
    """Mixed practice submenu for a specific level."""
    return render_template('mixed_menu.html', level=level)


@app.route('/reading/<level>')
def reading_menu(level):
    """Reading comprehension menu for a specific level."""
    return render_template('reading_menu.html', level=level)


@app.route('/reading-comprehension', methods=['GET', 'POST'])
def reading_comprehension():
    """Reading comprehension practice with Italian stories."""
    level = validate_level(request.args.get('level') or request.form.get('level') or session.get('level', 'A2'))

    if request.method == 'GET':
        session['level'] = level
        # Generate a new story for this level
        story = generate_story_for_level(level)
        questions = generate_comprehension_questions(story, level)

        # Store in session
        session['reading_story'] = story
        session['reading_questions'] = questions
        session['reading_current'] = 0
        session['reading_correct'] = 0
        session['reading_answers'] = []

        return render_template('reading_story.html', story=story, level=level)

    # POST: Submit answer to comprehension question
    answer = request.form.get('answer', '').strip()
    current_idx = session.get('reading_current', 0)
    questions = session.get('reading_questions', [])

    if current_idx < len(questions):
        question = questions[current_idx]
        is_correct = answer.lower() == question['correct'].lower()

        if is_correct:
            session['reading_correct'] = session.get('reading_correct', 0) + 1

        # Store answer
        answers = session.get('reading_answers', [])
        answers.append({
            'question': question['question'],
            'user_answer': answer,
            'correct_answer': question['correct'],
            'is_correct': is_correct
        })
        session['reading_answers'] = answers
        session['reading_current'] = current_idx + 1

    # Check if quiz is complete
    if session.get('reading_current', 0) >= len(questions):
        return redirect(url_for('reading_summary'))

    return redirect(url_for('reading_question'))


@app.route('/reading/question')
def reading_question():
    """Show current reading comprehension question."""
    if 'reading_questions' not in session:
        return redirect(url_for('home'))

    current_idx = session.get('reading_current', 0)
    questions = session.get('reading_questions', [])
    story = session.get('reading_story', {})
    level = session.get('level', 'A2')

    if current_idx >= len(questions):
        return redirect(url_for('reading_summary'))

    question = questions[current_idx]

    # Get the appropriate menu for the back button
    menu_route = 'reading_menu'

    return render_template('reading_question.html',
                          story=story,
                          question=question,
                          question_num=current_idx + 1,
                          total_questions=len(questions),
                          menu_route=menu_route,
                          level=level)


@app.route('/reading/summary')
def reading_summary():
    """Show reading comprehension summary."""
    if 'reading_questions' not in session:
        return redirect(url_for('home'))

    questions = session.get('reading_questions', [])
    correct_count = session.get('reading_correct', 0)
    answers = session.get('reading_answers', [])
    level = session.get('level', 'A2')

    total_questions = len(questions)
    accuracy = (correct_count / total_questions * 100) if total_questions > 0 else 0

    # Clear session
    session.pop('reading_story', None)
    session.pop('reading_questions', None)
    session.pop('reading_current', None)
    session.pop('reading_correct', None)
    session.pop('reading_answers', None)

    return render_template('reading_summary.html',
                          correct_count=correct_count,
                          total_questions=total_questions,
                          accuracy=accuracy,
                          answers=answers,
                          level=level)


def _load_stories_for_level(level: str) -> list:
    """Load stories JSON for the given level, with fallback to legacy hardcoded story."""
    level_map = {'A1': 'a1', 'A2': 'a2', 'B1': 'b1', 'B2': 'b2', 'GCSE': 'gcse'}
    key = level_map.get(level, 'a2')
    stories_dir = Path(__file__).parent / 'data' / 'reading_stories'
    json_path = stories_dir / f'{key}_stories.json'
    if json_path.exists():
        try:
            with open(json_path, encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return []


def generate_story_for_level(level: str) -> dict:
    """Pick a random story appropriate for the given CEFR level from JSON files."""
    stories = _load_stories_for_level(level)
    if stories:
        story = random.choice(stories)
        # Normalise vocab_hints to a string for template compatibility
        vh = story.get('vocab_hints', '')
        if isinstance(vh, dict):
            story['vocab_hints'] = ', '.join(f'{k} = {v}' for k, v in vh.items())
        return story
    # Fallback: minimal inline story if JSON missing
    return {
        'id': f'{level.lower()}_fallback',
        'title': 'Una Giornata Italiana',
        'text': 'Marco abita a Roma. Ogni mattina va al bar e prende un caffè. Poi va al lavoro. La sera mangia con la famiglia.',
        'vocab_hints': 'abita = lives, prende = takes/has, mangia = eats',
        'questions': []
    }


def generate_comprehension_questions(story: dict, level: str) -> list:
    """Return comprehension questions from the story dict (already embedded in JSON)."""
    raw_questions = story.get('questions', [])
    normalised = []
    for q in raw_questions:
        correct_raw = q.get('correct')
        choices = q.get('choices', [])
        # Normalise: if correct is an int index, convert to the choice text
        if isinstance(correct_raw, int):
            correct_text = choices[correct_raw] if 0 <= correct_raw < len(choices) else ''
        else:
            correct_text = str(correct_raw)
        normalised.append({
            'question': q.get('question', ''),
            'choices': choices,
            'correct': correct_text
        })
    return normalised


@app.route('/vocabulary-quiz', methods=['GET', 'POST'])
def vocabulary_quiz():
    """Vocabulary quiz practice."""
    # Get level from query params (from menu) or form (from setup)
    level = request.args.get('level') or request.form.get('level', 'A2')
    direction = request.args.get('direction')

    if request.method == 'GET' and not direction:
        # Show setup form
        return render_template('vocabulary_quiz_setup.html', level=level)

    # Get direction and count
    direction = direction or request.form.get('direction', 'it_to_en')
    count = validate_count(request.form.get('count', 10))

    # Generate questions using fresh generator
    generator = get_generator()
    questions = generator.generate_vocabulary_quiz(level, count, direction)

    # Store in session
    session['practice_type'] = 'vocabulary_quiz'
    session['questions'] = questions
    session['current_question'] = 0
    session['correct_count'] = 0
    session['answers'] = []
    session['start_time'] = time.time()
    session['level'] = level  # Store level for navigation
    session['direction'] = direction
    session['level'] = level  # Store level for navigation

    return redirect(url_for('practice_question'))


@app.route('/practice/question')
def practice_question():
    """Show current question."""
    try:
        if 'questions' not in session or 'current_question' not in session:
            return redirect(url_for('home'))

        questions = session.get('questions', [])
        current_idx = session.get('current_question', 0)

        # Check if quiz is complete
        if current_idx >= len(questions):
            return redirect(url_for('practice_summary'))

        if not questions:
            return render_template('error.html',
                                  error_message="No questions available. Please start a new practice session.",
                                  back_link=url_for('home'))

        question = questions[current_idx]
        total_questions = len(questions)

        # Get the appropriate menu for the back button
        practice_type = session.get('practice_type', '')
        menu_route = get_menu_for_practice_type(practice_type)
        level = session.get('level', 'A2')

        return render_template('question.html',
                              question=question,
                              question_num=current_idx + 1,
                              total_questions=total_questions,
                              menu_route=menu_route,
                              level=level)
    except (KeyError, IndexError, TypeError) as e:
        app.logger.error(f'Error in practice_question: {e}')
        return render_template('error.html',
                              error_message="Session error. Please start a new practice session.",
                              back_link=url_for('home'))


@app.route('/practice/submit', methods=['POST'])
def submit_answer():
    """Process submitted answer."""
    try:
        if 'questions' not in session:
            return redirect(url_for('home'))

        user_answer = request.form.get('answer', '').strip()
        questions = session.get('questions', [])
        current_idx = session.get('current_question', 0)

        if not questions or current_idx >= len(questions):
            return render_template('error.html',
                                  error_message="Session expired. Please start a new practice session.",
                                  back_link=url_for('home'))

        question = questions[current_idx]
    except (KeyError, IndexError, TypeError) as e:
        app.logger.error(f'Error in submit_answer: {e}')
        return render_template('error.html',
                              error_message="Session error. Please start a new practice session.",
                              back_link=url_for('home'))

    # Check answer with flexible matching, passing question type for special handling
    question_type = question.get('type', None)
    is_correct, display_answer = check_answer(user_answer, question['answer'], question_type)

    # Track answer
    if is_correct:
        session['correct_count'] = session.get('correct_count', 0) + 1

    # Store result
    answers = session.get('answers', [])
    answers.append({
        'question': question['question'],
        'user_answer': user_answer,
        'correct_answer': display_answer,
        'is_correct': is_correct
    })
    session['answers'] = answers

    # Show feedback (with explanation if available)
    explanation = question.get('explanation', None) or question.get('reason', None)
    hint = question.get('hint', None)

    # Add etymology fact for vocabulary questions
    etymology = None
    if question_type == 'vocabulary':
        # Try to get etymology from the Italian word
        italian_word = question.get('italian', display_answer)
        etymology = get_etymology_fact(italian_word)

    # Get the appropriate menu for the back button
    practice_type = session.get('practice_type', '')
    menu_route = get_menu_for_practice_type(practice_type)
    level = session.get('level', 'A2')

    return render_template('feedback.html',
                          is_correct=is_correct,
                          user_answer=user_answer,
                          correct_answer=display_answer,
                          question_type=question_type,
                          explanation=explanation,
                          hint=hint,
                          etymology=etymology,
                          question_num=current_idx + 1,
                          total_questions=len(questions),
                          menu_route=menu_route,
                          level=level)


@app.route('/practice/next')
def next_question():
    """Move to next question."""
    if 'questions' not in session:
        return redirect(url_for('home'))

    session['current_question'] = session.get('current_question', 0) + 1
    return redirect(url_for('practice_question'))


@app.route('/practice/summary')
def practice_summary():
    """Show practice session summary."""
    if 'questions' not in session:
        return redirect(url_for('home'))

    questions = session['questions']
    correct_count = session.get('correct_count', 0)
    total_questions = len(questions)

    # Calculate stats
    elapsed_time = int(time.time() - session.get('start_time', time.time()))
    accuracy = (correct_count / total_questions * 100) if total_questions > 0 else 0

    # Determine grade
    if accuracy >= 90:
        grade = "Excellent!"
        grade_emoji = "🌟"
    elif accuracy >= 75:
        grade = "Good job!"
        grade_emoji = "👍"
    elif accuracy >= 60:
        grade = "Keep practicing!"
        grade_emoji = "📚"
    else:
        grade = "More practice needed!"
        grade_emoji = "💪"

    # Save to database using fresh connection
    practice_type = session.get('practice_type', 'vocabulary_quiz')
    db = get_db()
    session_id = db.record_practice_session(
        session_type=practice_type,
        total_questions=total_questions,
        correct_answers=correct_count,
        time_spent=elapsed_time
    )
    db.close()

    # Format time
    minutes = elapsed_time // 60
    seconds = elapsed_time % 60
    time_str = f"{minutes}m {seconds}s"

    summary = {
        'correct': correct_count,
        'total': total_questions,
        'accuracy': accuracy,
        'time': time_str,
        'grade': grade,
        'grade_emoji': grade_emoji,
        'session_id': session_id,
        'answers': session.get('answers', [])
    }

    # Get level and practice type before clearing session
    level = session.get('level', 'A2')
    practice_type = session.get('practice_type', 'vocabulary_quiz')
    direction = session.get('direction', None)  # For vocabulary quiz

    # Build practice_again_url using PRACTICE_ROUTES mapping
    practice_again_url = url_for('category_menu', level=level)  # Default fallback
    if practice_type in PRACTICE_ROUTES:
        route_name, required_params = PRACTICE_ROUTES[practice_type]
        params = {'level': level}
        if 'direction' in required_params and direction:
            params['direction'] = direction
        practice_again_url = url_for(route_name, **params)

    # Clear session
    session.pop('questions', None)
    session.pop('current_question', None)
    session.pop('correct_count', None)
    session.pop('answers', None)
    session.pop('start_time', None)
    session.pop('practice_type', None)
    session.pop('level', None)
    session.pop('direction', None)

    return render_template('summary.html',
                          summary=summary,
                          level=level,
                          practice_type=practice_type,
                          direction=direction,
                          practice_again_url=practice_again_url)


@app.route('/verb-conjugation', methods=['GET', 'POST'])
def verb_conjugation():
    """General verb conjugation practice."""
    return create_practice_route(
        practice_type='verb_conjugation',
        generator_method='generate_verb_conjugation_drill',
        setup_template='verb_conjugation_setup.html',
        menu_type='verbs_menu',
        requires_level=True
    )()


@app.route('/irregular-passato', methods=['GET', 'POST'])
def irregular_passato():
    """Irregular passato prossimo practice."""
    return create_practice_route(
        practice_type='irregular_passato',
        generator_method='generate_irregular_passato_prossimo',
        setup_template='irregular_passato_setup.html',
        menu_type='verbs_menu'
    )()


@app.route('/regular-passato', methods=['GET', 'POST'])
def regular_passato():
    """Regular passato prossimo practice."""
    return create_practice_route(
        practice_type='regular_passato',
        generator_method='generate_regular_passato_prossimo',
        setup_template='regular_passato_setup.html',
        menu_type='verbs_menu'
    )()


@app.route('/imperfect-tense', methods=['GET', 'POST'])
def imperfect_tense():
    """Imperfect tense (imperfetto) practice."""
    return create_practice_route(
        practice_type='imperfect_tense',
        generator_method='generate_imperfect_tense',
        setup_template='imperfect_tense_setup.html',
        menu_type='verbs_menu'
    )()


@app.route('/auxiliary-choice', methods=['GET', 'POST'])
def auxiliary_choice():
    """Avere vs Essere auxiliary choice practice."""
    return create_practice_route(
        practice_type='auxiliary_choice',
        generator_method='generate_auxiliary_choice',
        setup_template='auxiliary_choice_setup.html',
        menu_type='verbs_menu'
    )()


@app.route('/futuro-semplice', methods=['GET', 'POST'])
def futuro_semplice():
    """Futuro semplice practice."""
    return create_practice_route(
        practice_type='futuro_semplice',
        generator_method='generate_futuro_semplice',
        setup_template='futuro_semplice_setup.html',
        menu_type='verbs_menu'
    )()


@app.route('/reflexive-verbs', methods=['GET', 'POST'])
def reflexive_verbs():
    """Reflexive verbs practice."""
    return create_practice_route(
        practice_type='reflexive_verbs',
        generator_method='generate_reflexive_verbs',
        setup_template='reflexive_verbs_setup.html',
        menu_type='verbs_menu'
    )()


@app.route('/conditional-present', methods=['GET', 'POST'])
def conditional_present():
    """Conditional present tense practice."""
    return create_practice_route(
        practice_type='conditional_present',
        generator_method='generate_conditional_present',
        setup_template='conditional_present_setup.html',
        menu_type='verbs_menu'
    )()


@app.route('/imperative', methods=['GET', 'POST'])
def imperative():
    """Imperative (command) tense practice."""
    return create_practice_route(
        practice_type='imperative',
        generator_method='generate_imperative_practice',
        setup_template='imperative_setup.html',
        menu_type='grammar_menu'
    )()


@app.route('/progressive-gerund', methods=['GET', 'POST'])
def progressive_gerund():
    """Progressive forms and gerund practice (B1 level)."""
    return create_practice_route(
        practice_type='progressive_gerund',
        generator_method='generate_progressive_gerund',
        setup_template='progressive_gerund_setup.html',
        menu_type='grammar_menu',
        requires_level=False
    )()


@app.route('/causative', methods=['GET', 'POST'])
def causative():
    """Causative constructions with fare/lasciare (B1 level)."""
    return create_practice_route(
        practice_type='causative',
        generator_method='generate_causative_constructions',
        setup_template='causative_setup.html',
        menu_type='grammar_menu',
        requires_level=False
    )()


@app.route('/advanced-pronouns', methods=['GET', 'POST'])
def advanced_pronouns():
    """Advanced pronouns ci and ne practice (B1 level)."""
    return create_practice_route(
        practice_type='advanced_pronouns',
        generator_method='generate_advanced_pronouns_ci_ne',
        setup_template='advanced_pronouns_setup.html',
        menu_type='grammar_menu',
        requires_level=False
    )()


@app.route('/conditional-past', methods=['GET', 'POST'])
def conditional_past():
    """Conditional past (condizionale passato) practice (B1 level)."""
    return create_practice_route(
        practice_type='conditional_past',
        generator_method='generate_conditional_past',
        setup_template='conditional_past_setup.html',
        menu_type='verbs_menu'
    )()


@app.route('/past-perfect', methods=['GET', 'POST'])
def past_perfect():
    """Past perfect (trapassato prossimo) practice (B1 level)."""
    return create_practice_route(
        practice_type='past_perfect',
        generator_method='generate_past_perfect',
        setup_template='past_perfect_setup.html',
        menu_type='verbs_menu'
    )()


@app.route('/passive-voice', methods=['GET', 'POST'])
def passive_voice():
    """Passive voice (forma passiva) practice (B1 level)."""
    return create_practice_route(
        practice_type='passive_voice',
        generator_method='generate_passive_voice',
        setup_template='passive_voice_setup.html',
        menu_type='verbs_menu'
    )()


@app.route('/pronominal-verbs', methods=['GET', 'POST'])
def pronominal_verbs():
    """Pronominal verbs practice (A2 level)."""
    return create_practice_route(
        practice_type='pronominal_verbs',
        generator_method='generate_pronominal_verbs',
        setup_template='pronominal_verbs_setup.html',
        menu_type='verbs_menu'
    )()


@app.route('/subjunctive-present', methods=['GET', 'POST'])
def subjunctive_present():
    """Subjunctive present (congiuntivo presente) practice (A2 level)."""
    return create_practice_route(
        practice_type='subjunctive_present',
        generator_method='generate_subjunctive_present',
        setup_template='subjunctive_present_setup.html',
        menu_type='verbs_menu'
    )()


@app.route('/subjunctive-past', methods=['GET', 'POST'])
def subjunctive_past():
    """Subjunctive past (congiuntivo passato) practice (B1 level)."""
    return create_practice_route(
        practice_type='subjunctive_past',
        generator_method='generate_subjunctive_past',
        setup_template='subjunctive_past_setup.html',
        menu_type='verbs_menu'
    )()


@app.route('/subjunctive-imperfect', methods=['GET', 'POST'])
def subjunctive_imperfect():
    """Subjunctive imperfect (congiuntivo imperfetto) practice (B1 level)."""
    return create_practice_route(
        practice_type='subjunctive_imperfect',
        generator_method='generate_subjunctive_imperfect',
        setup_template='subjunctive_imperfect_setup.html',
        menu_type='verbs_menu'
    )()


@app.route('/subjunctive-past-perfect', methods=['GET', 'POST'])
def subjunctive_past_perfect():
    """Subjunctive past perfect (congiuntivo trapassato) practice (B1 level)."""
    return create_practice_route(
        practice_type='subjunctive_past_perfect',
        generator_method='generate_subjunctive_past_perfect',
        setup_template='subjunctive_past_perfect_setup.html',
        menu_type='verbs_menu'
    )()


@app.route('/passato-remoto', methods=['GET', 'POST'])
def passato_remoto():
    """Passato remoto practice (B2 level)."""
    return create_practice_route(
        practice_type='passato_remoto',
        generator_method='generate_passato_remoto',
        setup_template='passato_remoto_setup.html',
        menu_type='verbs_menu'
    )()


@app.route('/relative-pronouns', methods=['GET', 'POST'])
def relative_pronouns():
    """Relative pronouns practice (B2 level)."""
    return create_practice_route(
        practice_type='relative_pronouns',
        generator_method='generate_relative_pronouns',
        setup_template='relative_pronouns_setup.html',
        menu_type='grammar_menu'
    )()


@app.route('/impersonal-si', methods=['GET', 'POST'])
def impersonal_si():
    """Impersonal si practice (B2 level)."""
    return create_practice_route(
        practice_type='impersonal_si',
        generator_method='generate_impersonal_si',
        setup_template='impersonal_si_setup.html',
        menu_type='grammar_menu'
    )()


@app.route('/unreal-past', methods=['GET', 'POST'])
def unreal_past():
    """Unreal past conditionals (B2 level)."""
    return create_practice_route(
        practice_type='unreal_past',
        generator_method='generate_unreal_past',
        setup_template='unreal_past_setup.html',
        menu_type='verbs_menu'
    )()


@app.route('/unreal-present', methods=['GET', 'POST'])
def unreal_present():
    """Unreal present conditionals (B1 level) - Se + imperfect subjunctive + conditional."""
    return create_practice_route(
        practice_type='unreal_present',
        generator_method='generate_unreal_present',
        setup_template='unreal_present_setup.html',
        menu_type='verbs_menu'
    )()


@app.route('/comprehensive-subjunctives', methods=['GET', 'POST'])
def comprehensive_subjunctives():
    """Comprehensive subjunctives review (B2 level)."""
    return create_practice_route(
        practice_type='comprehensive_subjunctives',
        generator_method='generate_comprehensive_subjunctives',
        setup_template='comprehensive_subjunctives_setup.html',
        menu_type='verbs_menu'
    )()


@app.route('/present-tense', methods=['GET', 'POST'])
def present_tense():
    """Present tense conjugation practice (A1 level)."""
    level = request.args.get('level') or request.form.get('level') or session.get('level', 'A1')

    if request.method == 'GET':
        session['level'] = level
        return render_template('present_tense_setup.html', level=level)

    count = validate_count(request.form.get('count', 10))
    generator = get_generator()
    questions = generator.generate_present_tense_conjugation(count)

    session['practice_type'] = 'present_tense'
    session['questions'] = questions
    session['current_question'] = 0
    session['correct_count'] = 0
    session['answers'] = []
    session['start_time'] = time.time()
    session['level'] = level  # Store level for navigation

    return redirect(url_for('practice_question'))


# Bug-0088: Focused present-tense conjugation drills by verb ending type

@app.route('/are-verb-present', methods=['GET', 'POST'])
def are_verb_present():
    """Regular -ARE verb present tense conjugation practice (A1 level)."""
    return create_practice_route(
        practice_type='are_verb_present',
        generator_method='generate_are_verb_present',
        setup_template='are_verb_present_setup.html',
        menu_type='verbs_menu'
    )()


@app.route('/ere-verb-present', methods=['GET', 'POST'])
def ere_verb_present():
    """Regular -ERE verb present tense conjugation practice (A2 level)."""
    return create_practice_route(
        practice_type='ere_verb_present',
        generator_method='generate_ere_verb_present',
        setup_template='ere_verb_present_setup.html',
        menu_type='verbs_menu'
    )()


@app.route('/ire-verb-present', methods=['GET', 'POST'])
def ire_verb_present():
    """Regular -IRE verb present tense conjugation practice (A2 level)."""
    return create_practice_route(
        practice_type='ire_verb_present',
        generator_method='generate_ire_verb_present',
        setup_template='ire_verb_present_setup.html',
        menu_type='verbs_menu'
    )()


# Bug-0094: New A1 Italian articles activity

@app.route('/italian-articles', methods=['GET', 'POST'])
def italian_articles():
    """Italian articles practice (A1 level) — definite, indefinite, gender and vowel rules."""
    return create_practice_route(
        practice_type='italian_articles',
        generator_method='generate_italian_articles',
        setup_template='italian_articles_setup.html',
        menu_type='grammar_menu'
    )()


@app.route('/noun-gender-number', methods=['GET', 'POST'])
def noun_gender_number():
    """Noun gender and number identification practice."""
    return create_practice_route(
        practice_type='noun_gender_number',
        generator_method='generate_noun_gender_number',
        setup_template='noun_gender_number_setup.html',
        menu_type='grammar_menu'
    )()


@app.route('/articulated-prepositions', methods=['GET', 'POST'])
def articulated_prepositions():
    """Articulated prepositions practice."""
    return create_practice_route(
        practice_type='articulated_prepositions',
        generator_method='generate_articulated_prepositions',
        setup_template='articulated_prepositions_setup.html',
        menu_type='grammar_menu'
    )()


@app.route('/time-prepositions', methods=['GET', 'POST'])
def time_prepositions():
    """Time prepositions practice."""
    return create_practice_route(
        practice_type='time_prepositions',
        generator_method='generate_time_prepositions',
        setup_template='time_prepositions_setup.html',
        menu_type='grammar_menu'
    )()


@app.route('/negations', methods=['GET', 'POST'])
def negations():
    """Negations practice."""
    return create_practice_route(
        practice_type='negations',
        generator_method='generate_negation_practice',
        setup_template='negations_setup.html',
        menu_type='grammar_menu'
    )()


@app.route('/pronouns', methods=['GET', 'POST'])
def pronouns():
    """Direct and indirect pronouns practice."""
    return create_practice_route(
        practice_type='pronouns',
        generator_method='generate_pronouns_practice',
        setup_template='pronouns_setup.html',
        menu_type='grammar_menu'
    )()


@app.route('/combined-pronouns', methods=['GET', 'POST'])
def combined_pronouns():
    """Combined pronouns practice (B1 level)."""
    return create_practice_route(
        practice_type='combined_pronouns',
        generator_method='generate_combined_pronouns',
        setup_template='combined_pronouns_setup.html',
        menu_type='grammar_menu'
    )()


@app.route('/adverbs', methods=['GET', 'POST'])
def adverbs():
    """Adverbs practice."""
    return create_practice_route(
        practice_type='adverbs',
        generator_method='generate_adverbs_practice',
        setup_template='adverbs_setup.html',
        menu_type='grammar_menu'
    )()


@app.route('/fill-in-blank', methods=['GET', 'POST'])
def fill_in_blank():
    """Fill in the blank practice."""
    level = validate_level(request.args.get('level') or request.form.get('level') or session.get('level', 'A2'))

    if request.method == 'GET':
        session['level'] = level
        return render_template('fill_in_blank_setup.html', level=level)

    count = validate_count(request.form.get('count', 10))
    generator = get_generator()
    questions = generator.generate_fill_in_blank(level, count)

    session['practice_type'] = 'fill_in_blank'
    session['questions'] = questions
    session['current_question'] = 0
    session['correct_count'] = 0
    session['answers'] = []
    session['start_time'] = time.time()
    session['level'] = level  # Store level for navigation

    return redirect(url_for('practice_question'))


@app.route('/multiple-choice', methods=['GET', 'POST'])
def multiple_choice():
    """Multiple choice practice."""
    level = validate_level(request.args.get('level') or request.form.get('level') or session.get('level', 'A2'))

    if request.method == 'GET':
        session['level'] = level
        return render_template('multiple_choice_setup.html', level=level)

    count = validate_count(request.form.get('count', 10))
    generator = get_generator()
    questions = generator.generate_multiple_choice(level, count)

    session['practice_type'] = 'multiple_choice'
    session['questions'] = questions
    session['current_question'] = 0
    session['correct_count'] = 0
    session['answers'] = []
    session['start_time'] = time.time()
    session['level'] = level  # Store level for navigation

    return redirect(url_for('practice_question'))


@app.route('/sentence-translator', methods=['GET', 'POST'])
def sentence_translator():
    """Sentence translation practice."""
    level = validate_level(request.args.get('level') or request.form.get('level') or session.get('level', 'A2'))

    if request.method == 'GET':
        direction = request.args.get('direction', 'it_to_en')
        session['level'] = level
        return render_template('sentence_translator_setup.html', level=level, direction=direction)

    direction = request.form.get('direction', 'it_to_en')
    count = validate_count(request.form.get('count', 10))

    generator = get_generator()
    questions = generator.generate_sentence_translation(level, count, direction)

    # Check if questions were generated
    if not questions or len(questions) == 0:
        session['level'] = level
        return render_template('error.html',
                             error_message=f"No sentence translation exercises available for {level}. Please try a different level.",
                             back_link=url_for('vocabulary_menu', level=level))

    session['practice_type'] = 'sentence_translator'
    session['questions'] = questions
    session['current_question'] = 0
    session['correct_count'] = 0
    session['answers'] = []
    session['start_time'] = time.time()
    session['level'] = level  # Store level for navigation

    return redirect(url_for('practice_question'))


@app.route('/stats')
def view_stats():
    """View progress statistics."""
    # Get fresh database connection
    db = get_db()

    # Get stats for different periods
    stats_7 = db.get_performance_stats(7)
    stats_30 = db.get_performance_stats(30)
    stats_90 = db.get_performance_stats(90)

    # Get weak areas
    weak_areas = db.get_weak_areas(5)

    db.close()

    return render_template('stats.html',
                          stats_7=stats_7,
                          stats_30=stats_30,
                          stats_90=stats_90,
                          weak_areas=weak_areas)


@app.route('/topics')
def view_topics():
    """View all topics by level."""
    # Get fresh database connection
    db = get_db()

    topics_a1 = db.get_topics_by_level("A1")
    topics_a2 = db.get_topics_by_level("A2")

    db.close()

    return render_template('topics.html',
                          topics_a1=topics_a1,
                          topics_a2=topics_a2)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
