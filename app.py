"""
Italian Learning Companion - Flask Web Application
"""

import sys
import os
from pathlib import Path
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import time
from datetime import datetime

# Add src directory to path so we can import existing modules
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from database import ItalianDatabase
from practice_generator import PracticeGenerator

app = Flask(__name__)
app.secret_key = 'italian-learning-companion-secret-key-2024'  # Change this in production

# Database path
DB_PATH = "../data/curriculum.db"


def get_db():
    """Get a database connection for the current request."""
    return ItalianDatabase(DB_PATH)


def get_generator():
    """Get a practice generator with a fresh database connection."""
    return PracticeGenerator(get_db())


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
    count = int(request.form.get('count', 10))

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
    session['direction'] = direction

    return redirect(url_for('practice_question'))


@app.route('/practice/question')
def practice_question():
    """Show current question."""
    if 'questions' not in session or 'current_question' not in session:
        return redirect(url_for('home'))

    questions = session['questions']
    current_idx = session['current_question']

    # Check if quiz is complete
    if current_idx >= len(questions):
        return redirect(url_for('practice_summary'))

    question = questions[current_idx]
    total_questions = len(questions)

    return render_template('question.html',
                          question=question,
                          question_num=current_idx + 1,
                          total_questions=total_questions)


@app.route('/practice/submit', methods=['POST'])
def submit_answer():
    """Process submitted answer."""
    if 'questions' not in session:
        return redirect(url_for('home'))

    user_answer = request.form.get('answer', '').strip()
    questions = session['questions']
    current_idx = session['current_question']
    question = questions[current_idx]

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

    # Show feedback
    return render_template('feedback.html',
                          is_correct=is_correct,
                          user_answer=user_answer,
                          correct_answer=display_answer,
                          question_type=question_type,
                          question_num=current_idx + 1,
                          total_questions=len(questions))


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

    # Clear session
    session.pop('questions', None)
    session.pop('current_question', None)
    session.pop('correct_count', None)
    session.pop('answers', None)
    session.pop('start_time', None)
    session.pop('practice_type', None)

    return render_template('summary.html', summary=summary)


@app.route('/verb-conjugation', methods=['GET', 'POST'])
def verb_conjugation():
    """General verb conjugation practice."""
    level = request.args.get('level') or request.form.get('level', 'A2')
    count = int(request.form.get('count', 10))

    # Generate questions using fresh generator
    generator = get_generator()
    questions = generator.generate_verb_conjugation_drill(level, count)

    # Store in session
    session['practice_type'] = 'verb_conjugation'
    session['questions'] = questions
    session['current_question'] = 0
    session['correct_count'] = 0
    session['answers'] = []
    session['start_time'] = time.time()

    return redirect(url_for('practice_question'))


@app.route('/irregular-passato', methods=['GET', 'POST'])
def irregular_passato():
    """Irregular passato prossimo practice."""
    if request.method == 'GET':
        # Show setup form
        level = request.args.get('level') or request.form.get('level', 'A2')
        return render_template('irregular_passato_setup.html', level=level)

    # POST: Start new practice
    count = int(request.form.get('count', 10))

    # Generate questions using fresh generator
    generator = get_generator()
    questions = generator.generate_irregular_passato_prossimo(count)

    # Store in session
    session['practice_type'] = 'irregular_passato'
    session['questions'] = questions
    session['current_question'] = 0
    session['correct_count'] = 0
    session['answers'] = []
    session['start_time'] = time.time()

    return redirect(url_for('practice_question'))


@app.route('/regular-passato', methods=['GET', 'POST'])
def regular_passato():
    """Regular passato prossimo practice."""
    if request.method == 'GET':
        level = request.args.get('level') or request.form.get('level', 'A2')
        return render_template('regular_passato_setup.html', level=level)

    # POST: Start new practice
    count = int(request.form.get('count', 10))
    generator = get_generator()
    questions = generator.generate_regular_passato_prossimo(count)

    session['practice_type'] = 'regular_passato'
    session['questions'] = questions
    session['current_question'] = 0
    session['correct_count'] = 0
    session['answers'] = []
    session['start_time'] = time.time()

    return redirect(url_for('practice_question'))


@app.route('/imperfect-tense', methods=['GET', 'POST'])
def imperfect_tense():
    """Imperfect tense (imperfetto) practice."""
    if request.method == 'GET':
        level = request.args.get('level') or request.form.get('level', 'A2')
        return render_template('imperfect_tense_setup.html', level=level)

    # POST: Start new practice
    count = int(request.form.get('count', 10))
    generator = get_generator()
    questions = generator.generate_imperfect_tense(count)

    session['practice_type'] = 'imperfect_tense'
    session['questions'] = questions
    session['current_question'] = 0
    session['correct_count'] = 0
    session['answers'] = []
    session['start_time'] = time.time()

    return redirect(url_for('practice_question'))


@app.route('/auxiliary-choice', methods=['GET', 'POST'])
def auxiliary_choice():
    """Avere vs Essere auxiliary choice practice."""
    if request.method == 'GET':
        level = request.args.get('level') or request.form.get('level', 'A2')
        return render_template('auxiliary_choice_setup.html', level=level)

    count = int(request.form.get('count', 10))
    generator = get_generator()
    questions = generator.generate_auxiliary_choice(count)

    session['practice_type'] = 'auxiliary_choice'
    session['questions'] = questions
    session['current_question'] = 0
    session['correct_count'] = 0
    session['answers'] = []
    session['start_time'] = time.time()

    return redirect(url_for('practice_question'))


@app.route('/futuro-semplice', methods=['GET', 'POST'])
def futuro_semplice():
    """Futuro semplice practice."""
    if request.method == 'GET':
        level = request.args.get('level') or request.form.get('level', 'A2')
        return render_template('futuro_semplice_setup.html', level=level)

    count = int(request.form.get('count', 10))
    generator = get_generator()
    questions = generator.generate_futuro_semplice(count)

    session['practice_type'] = 'futuro_semplice'
    session['questions'] = questions
    session['current_question'] = 0
    session['correct_count'] = 0
    session['answers'] = []
    session['start_time'] = time.time()

    return redirect(url_for('practice_question'))


@app.route('/reflexive-verbs', methods=['GET', 'POST'])
def reflexive_verbs():
    """Reflexive verbs practice."""
    if request.method == 'GET':
        level = request.args.get('level') or request.form.get('level', 'A2')
        return render_template('reflexive_verbs_setup.html', level=level)

    count = int(request.form.get('count', 10))
    generator = get_generator()
    questions = generator.generate_reflexive_verbs(count)

    session['practice_type'] = 'reflexive_verbs'
    session['questions'] = questions
    session['current_question'] = 0
    session['correct_count'] = 0
    session['answers'] = []
    session['start_time'] = time.time()

    return redirect(url_for('practice_question'))


@app.route('/articulated-prepositions', methods=['GET', 'POST'])
def articulated_prepositions():
    """Articulated prepositions practice."""
    if request.method == 'GET':
        level = request.args.get('level') or request.form.get('level', 'A2')
        return render_template('articulated_prepositions_setup.html', level=level)

    count = int(request.form.get('count', 10))
    generator = get_generator()
    questions = generator.generate_articulated_prepositions(count)

    session['practice_type'] = 'articulated_prepositions'
    session['questions'] = questions
    session['current_question'] = 0
    session['correct_count'] = 0
    session['answers'] = []
    session['start_time'] = time.time()

    return redirect(url_for('practice_question'))


@app.route('/time-prepositions', methods=['GET', 'POST'])
def time_prepositions():
    """Time prepositions practice."""
    if request.method == 'GET':
        level = request.args.get('level') or request.form.get('level', 'A2')
        return render_template('time_prepositions_setup.html', level=level)

    count = int(request.form.get('count', 10))
    generator = get_generator()
    questions = generator.generate_time_prepositions(count)

    session['practice_type'] = 'time_prepositions'
    session['questions'] = questions
    session['current_question'] = 0
    session['correct_count'] = 0
    session['answers'] = []
    session['start_time'] = time.time()

    return redirect(url_for('practice_question'))


@app.route('/negations', methods=['GET', 'POST'])
def negations():
    """Negations practice."""
    if request.method == 'GET':
        level = request.args.get('level') or request.form.get('level', 'A2')
        return render_template('negations_setup.html', level=level)

    count = int(request.form.get('count', 10))
    generator = get_generator()
    questions = generator.generate_negation_practice(count)

    session['practice_type'] = 'negations'
    session['questions'] = questions
    session['current_question'] = 0
    session['correct_count'] = 0
    session['answers'] = []
    session['start_time'] = time.time()

    return redirect(url_for('practice_question'))


@app.route('/fill-in-blank', methods=['GET', 'POST'])
def fill_in_blank():
    """Fill in the blank practice."""
    if request.method == 'GET':
        level = request.args.get('level') or request.form.get('level', 'A2')
        return render_template('fill_in_blank_setup.html', level=level)

    level = request.args.get('level') or request.form.get('level', 'A2')
    count = int(request.form.get('count', 10))
    generator = get_generator()
    questions = generator.generate_fill_in_blank(level, count)

    session['practice_type'] = 'fill_in_blank'
    session['questions'] = questions
    session['current_question'] = 0
    session['correct_count'] = 0
    session['answers'] = []
    session['start_time'] = time.time()

    return redirect(url_for('practice_question'))


@app.route('/multiple-choice', methods=['GET', 'POST'])
def multiple_choice():
    """Multiple choice practice."""
    if request.method == 'GET':
        level = request.args.get('level') or request.form.get('level', 'A2')
        return render_template('multiple_choice_setup.html', level=level)

    level = request.args.get('level') or request.form.get('level', 'A2')
    count = int(request.form.get('count', 10))
    generator = get_generator()
    questions = generator.generate_multiple_choice(level, count)

    session['practice_type'] = 'multiple_choice'
    session['questions'] = questions
    session['current_question'] = 0
    session['correct_count'] = 0
    session['answers'] = []
    session['start_time'] = time.time()

    return redirect(url_for('practice_question'))


@app.route('/sentence-translator', methods=['GET', 'POST'])
def sentence_translator():
    """Sentence translation practice."""
    if request.method == 'GET':
        level = request.args.get('level') or request.form.get('level', 'A2')
        return render_template('sentence_translator_setup.html', level=level)

    level = request.args.get('level') or request.form.get('level', 'A2')
    direction = request.form.get('direction', 'it_to_en')
    count = int(request.form.get('count', 10))

    generator = get_generator()
    questions = generator.generate_sentence_translation(level, count, direction)

    session['practice_type'] = 'sentence_translator'
    session['questions'] = questions
    session['current_question'] = 0
    session['correct_count'] = 0
    session['answers'] = []
    session['start_time'] = time.time()

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
