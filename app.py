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


@app.template_filter('parse_conjugate_question')
def parse_conjugate_question(question_text: str) -> dict:
    """
    For conjugation questions, strips the English meaning from the question string
    so it can be rendered as a chip below the answer input instead.
    E.g. "Conjugate 'venire' (to come) in passato prossimo for noi"
      -> main: "Conjugate 'venire' in passato prossimo for noi"
      -> english: "to come"
    Non-conjugation questions are returned unchanged.
    """
    import re
    result = {'main': question_text, 'english': '', 'is_conjugate': False}

    # Only applies to Conjugate questions
    if not re.match(r"Conjugate(?:\s+reflexive)?:", question_text, re.IGNORECASE) and \
       not question_text.startswith("Conjugate '"):
        return result

    result['is_conjugate'] = True

    # Extract and remove the English meaning: (to ...) immediately after the verb name
    eng_match = re.search(r"('\w[\w\s]*')\s*\(([^)]+)\)", question_text)
    if eng_match:
        result['english'] = eng_match.group(2)
        # Rebuild: keep the verb name, drop the (english) part
        question_text = question_text[:eng_match.end(1)] + question_text[eng_match.end():]

    result['main'] = re.sub(r'\s+', ' ', question_text).strip()
    return result

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
    'verb_prepositions': ('verb_prepositions', ['level']),
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
    """Get an etymology fact or Italian fun fact for any word."""
    etymology_facts = {
        # ── Days of the week ──────────────────────────────────────────────────
        'lunedì':    'Named after Luna (the Moon) — "Moon\'s day". Same logic as English Monday.',
        'martedì':   'Named after Mars, god of war — "Mars\' day". Like English Tuesday (Tiw\'s day).',
        'mercoledì': 'Named after Mercury, god of commerce — "Mercury\'s day". Like English Wednesday.',
        'giovedì':   'Named after Jupiter/Jove, king of the gods — "Jupiter\'s day". Like Thursday.',
        'venerdì':   'Named after Venus, goddess of love — "Venus\' day". Like English Friday.',
        'sabato':    'From Hebrew "Shabbat" (day of rest) — one of the few Hebrew borrowings in Italian.',
        'domenica':  'From Latin "dies dominica" (the Lord\'s day) — a Christian renaming of the old sun-day.',

        # ── Months ────────────────────────────────────────────────────────────
        'gennaio':   'From Latin "Ianuarius" — named after Janus, the two-faced god of beginnings.',
        'febbraio':  'From Latin "februum" (purification) — Romans held purification rites this month.',
        'marzo':     'Named after Mars, god of war — the original first month of the Roman calendar.',
        'aprile':    'Possibly from Latin "aperire" (to open) — spring opens the earth.',
        'maggio':    'From Latin "Maius" — named after Maia, goddess of growth.',
        'giugno':    'From Latin "Iunius" — named after Juno, queen of the gods.',
        'luglio':    'From Latin "Iulius" — named after Julius Caesar.',
        'agosto':    'From Latin "Augustus" — named after Emperor Augustus.',
        'settembre': 'From Latin "septem" (seven) — it was the 7th month in the original Roman calendar.',
        'ottobre':   'From Latin "octo" (eight) — the 8th month of the old Roman calendar.',
        'novembre':  'From Latin "novem" (nine) — the 9th month of the old Roman calendar.',
        'dicembre':  'From Latin "decem" (ten) — the 10th month of the old Roman calendar.',

        # ── Seasons ───────────────────────────────────────────────────────────
        'primavera': 'From Latin "primo vere" (first spring) — literally "the first green".',
        'estate':    'From Latin "aestas" (summer heat) — root of "estival" (relating to summer).',
        'autunno':   'From Latin "autumnus" — possibly Etruscan in origin, predating Roman Latin.',
        'inverno':   'From Latin "hibernum" (winter) — same root as "hibernate".',

        # ── Food & drink ──────────────────────────────────────────────────────
        'caffè':       'From Turkish "kahve", originally from Arabic "qahwah". Coffee reached Italy via Venice in the 1570s.',
        'pasta':       'From Greek "pastē" (barley porridge). Contrary to legend, Italy had pasta before Marco Polo.',
        'pizza':       'First documented in Gaeta in 997 AD. The word may come from Latin "pinsa" (flatbread). Margherita pizza was created in 1889 for Queen Margherita.',
        'pane':        'From Latin "panis" — same root as English "pantry" and "companion" (com + panis = sharing bread).',
        'vino':        'From Latin "vinum" — one of the oldest cultivated words, related to Greek "oinos". Italy produces more wine than any other country.',
        'acqua':       'From Latin "aqua" — root of "aquatic", "aquarium", and "aqueduct". Romans built 11 aqueducts serving Rome.',
        'latte':       'From Latin "lac/lactis" — root of "lactose" and "galaxy" (the Milky Way).',
        'burro':       'From Latin "butyrum", itself from Greek "boutyron" (ox-cheese). Same root as English "butter".',
        'formaggio':   'From Latin "formaticus" (made in a mould) — the French "fromage" has the same origin.',
        'gelato':      'From Latin "gelatus" (frozen) — related to "gelid". Italian gelato has less air than ice cream, making it denser.',
        'prosciutto':  'From Latin "perexsuctum" (thoroughly dried) — cured for months, sometimes years.',
        'zucchero':    'From Arabic "sukkar" via Sanskrit "śárkarā" (gravel/sand, for sugar crystals).',
        'riso':        'From Latin "oryza", itself from Greek/Persian, originally from Sanskrit "vrīhi".',
        'pesce':       'From Latin "piscis" — same root as Pisces (the zodiac fish) and "piscina" (fish pond → pool).',
        'carne':       'From Latin "caro/carnis" (flesh) — root of "carnivore", "carnival" (farewell to meat), and "incarnate".',
        'uovo':        'From Latin "ovum" — root of "oval" and "ovary". Unusual plural: un uovo → le uova (changes gender in plural).',
        'sale':        'From Latin "sal" — root of "salary" (Roman soldiers were partly paid in salt) and "salad" (salted greens).',
        'olio':        'From Latin "oleum", from Greek "elaion" (olive oil) — root of "petroleum" (rock oil).',
        'aglio':       'From Latin "allium" — ancient Romans ate garlic daily for strength. Same root as English "allium".',
        'pomodoro':    'Literally "golden apple" (pomo d\'oro) — early tomatoes brought from America were yellow, not red.',
        'limone':      'From Arabic "laymūn" via Persian "līmūn" — citrus fruits came to Europe via Arab traders.',
        'arancia':     'From Arabic "nāranj" via Persian — the \'n\' was lost when Italian speakers thought it was the article.',
        'ananas':      'From the Tupi word "nanas" (excellent fruit) — brought from South America by Portuguese explorers.',
        'albicocca':   'From Arabic "al-barquq" — apricots came to Europe via Arab traders.',
        'fragola':     'From Latin "fragrans" (fragrant) — named for its sweet smell.',
        'uva':         'From Latin "uva" (grape/grape cluster). Italy has over 350 native grape varieties.',
        'antipasto':   'Literally "before the meal" (anti + pasto). The tradition dates to Roman "gustatio" starters.',
        'colazione':   'From Latin "collatio" (a bringing together) — originally a monastic light meal.',
        'dolce':       'From Latin "dulcis" (sweet) — root of "dulcet". Also means "gentle/soft" in Italian.',
        'birra':       'From Germanic "bier" — beer was introduced to Italy by northern European tribes.',
        'cioccolato':  'From Aztec "xocolātl" (bitter water) — brought to Europe by Spanish conquistadors in 1528.',

        # ── Animals ───────────────────────────────────────────────────────────
        'gatto':    'From Late Latin "cattus" — the domestic cat was so valued in Rome that stealing one was a crime.',
        'cane':     'From Latin "canis" — root of "canine". The word "cancel" also derives from it (latticed bars like a kennel).',
        'cavallo':  'From Latin "caballus" (work horse) — root of "cavalry" and "chivalry".',
        'uccello':  'From Latin "aucellus" (small bird) — root of "augur" (divination by watching birds).',

        # ── Home & places ─────────────────────────────────────────────────────
        'casa':       'From Latin "casa" (cottage/hut) — in ancient Rome, the grand word for house was "domus" (root of "domestic").',
        'finestra':   'From Latin "fenestra" (window) — root of "fenestrated" and "defenestration" (throwing someone out a window).',
        'porta':      'From Latin "porta" (gate/door) — root of "portal", "porter", and "portfolio".',
        'cucina':     'From Latin "coquina" (kitchen) — root of "cook", "cuisine", and "biscuit".',
        'biblioteca': 'From Greek "bibliotheke" (book storage) — "biblio" means book, root of "bibliography".',
        'chiesa':     'From Greek "ekklesia" (assembly) — root of "ecclesiastical".',
        'piazza':     'From Latin "platea" (broad street) — root of English "place" and "plaza".',
        'stazione':   'From Latin "statio" (a standing, a post) — root of "station", "static", "statue".',

        # ── City & transport ──────────────────────────────────────────────────
        'treno':      'From English "train" — borrowed in the 1800s when railways arrived in Italy.',
        'aereo':      'From Greek "aer" (air) — Italy had pioneering aviators; D\'Annunzio dropped leaflets over Vienna in 1918.',
        'autobus':    'From Latin "auto" (self) + Latin "omnibus" (for all) — literally "self-moving for everyone".',
        'bicicletta': 'From Latin "bi" (two) + Greek "kyklos" (circle/wheel) — the modern bicycle was perfected in the 1880s.',
        'macchina':   'From Greek "mechane" (contrivance/machine) — Italians called the car "the machine" when it arrived.',
        'nave':       'From Latin "navis" (ship) — root of "navigate", "navy", "naval".',
        'porto':      'From Latin "portus" (harbour) — root of "port", "transport", "import", "export".',
        'passaporto': 'Literally "pass the port/gate" (passa + porto) — a document letting you through the harbour gate.',
        'biglietto':  'From French "billet" (note/ticket) — diminutive of "bille" (seal on a document).',

        # ── People & family ───────────────────────────────────────────────────
        'madre':   'From Latin "mater" — one of the most ancient human words, almost identical across Indo-European languages.',
        'padre':   'From Latin "pater" — found in Sanskrit "pitā", Greek "patēr", English "father".',
        'fratello':'From Latin "fraternus" (brotherly) — root of "fraternity" and "fraternise".',
        'sorella': 'From Latin "soror" (sister) — root of "sorority". Shakespeare used the Latin form in legal texts.',
        'figlio':  'From Latin "filius" (son) — root of "filial" (relating to a son or daughter).',
        'nonno':   'A playful reduplication of "nono" — Italian children\'s language often doubles syllables for family words.',
        'marito':  'From Latin "maritus" (husband) — root of "marital" and "matrimony".',
        'moglie':  'From Latin "mulier" (woman) — one of the few words where Italian diverged completely from "femina".',
        'amico':   'From Latin "amicus" (friend) — root of "amicable", "amiable". Also root of "enemy" (in-amicus).',

        # ── Body & health ─────────────────────────────────────────────────────
        'testa':    'From Latin "testa" (pot/shell) — Romans used "caput" for head in classical Latin; "testa" was slang, like saying "noggin".',
        'mano':     'From Latin "manus" (hand) — root of "manual", "manufacture", "manuscript", "manage".',
        'piede':    'From Latin "pes/pedis" (foot) — root of "pedestrian", "pedal", "expedite".',
        'occhio':   'From Latin "oculus" (eye) — root of "ocular", "binoculars", "inoculate".',
        'naso':     'From Latin "nasus" (nose) — root of "nasal". Italian has the expression "avere il naso fino" (to have a fine nose = sharp intuition).',
        'cuore':    'From Latin "cor/cordis" (heart) — root of "cordial", "courage", "accord", "record".',
        'febbre':   'From Latin "febris" (fever) — root of "February" (the purification month, possibly linked to illness).',
        'medicina': 'From Latin "medicina" — the word "doctor" comes from Latin "docere" (to teach); early doctors were teachers of medicine.',

        # ── School & learning ─────────────────────────────────────────────────
        'scuola':     'From Greek "skholē" — the original meaning was "leisure", as only those with free time could learn.',
        'libro':      'From Latin "liber" (book, but also the inner bark of a tree, where Romans wrote) — root of "library" and "liberate".',
        'lingua':     'From Latin "lingua" (tongue/language) — root of "bilingual", "linguistics", "linguine" (little tongues).',
        'matematica': 'From Greek "mathēmatikē" (relating to learning) — root of "mathematics".',
        'storia':     'From Greek "historia" (inquiry, knowledge from research) — root of "history" and "story".',
        'arte':       'From Latin "ars/artis" — root of "art", "artisan", "artificial".',
        'musica':     'From Greek "mousikē" — named after the Muses, the nine goddesses of creative arts.',
        'università': 'From Latin "universitas" (the whole, a corporation) — Bologna (1088) is the world\'s oldest university.',
        'esame':      'From Latin "examen" (the tongue of a balance) — originally meant careful weighing/testing.',

        # ── Work ──────────────────────────────────────────────────────────────
        'lavoro':    'From Latin "laborare" (to toil) — root of "labour". The Latin root also gave us "elaborate".',
        'ufficio':   'From Latin "officium" (duty/service) — root of "official", "officer", "officious".',
        'stipendio': 'From Latin "stipendium" (soldiers\' pay, coins + weight) — Roman soldiers were weighed their pay.',
        'medico':    'From Latin "medicus" (healer) — root of "medical", "medicine", "remedy".',
        'ingegnere': 'From Latin "ingenium" (cleverness/talent) — root of "engineer", "engine", "ingenious".',

        # ── Nature & environment ──────────────────────────────────────────────
        'mare':      'From Latin "mare" (sea) — root of "marine", "maritime", "submarine". Italy has 7,600 km of coastline.',
        'montagna':  'From Latin "montanea" (mountainous region) — root of "mountain", "Montana", "Paramount".',
        'fiume':     'From Latin "flumen" (river, flow) — root of "fluid", "fluent", "influence".',
        'lago':      'From Latin "lacus" (lake/basin) — root of "lacuna" (a gap/missing part).',
        'bosco':     'From Germanic "busc" (forest) — root of "bush". Italy\'s forests cover 37% of the country.',
        'sole':      'From Latin "sol" (sun) — root of "solar", "solstice", "parasol". Same root in almost all European languages.',
        'luna':      'From Latin "luna" (moon) — root of "lunar", "lunatic" (once thought caused by the moon).',
        'pioggia':   'From Latin "pluvia" (rain) — root of "pluvial". Italy\'s name may come from "Vitalia" (land of cattle, needing rain).',
        'neve':      'From Latin "nix/nivis" (snow) — root of "niveous" (snowy). The Alps receive up to 10 metres of snow per year.',
        'vento':     'From Latin "ventus" (wind) — root of "ventilate", "vent".',
        'ambiente':  'From Latin "ambire" (to go around) — root of "ambient", "ambience".',
        'inquinamento': 'From Latin "inquinare" (to stain/pollute) — "in" (not) + "quinus" (pure).',

        # ── Clothes ───────────────────────────────────────────────────────────
        'vestito':  'From Latin "vestire" (to clothe) — root of "vest", "invest" (to clothe in authority), "divest".',
        'scarpe':   'From Germanic "skarpa" (something scraped/sharp) — shoes were made by scraping leather flat.',
        'cappello': 'From Latin "capa" (hood/cape) — root of "cap", "cape", "escape" (slip out of your cape).',
        'giacca':   'From French "jaque" (a short coat) — possibly named after Jacques Bonhomme, a common French name.',

        # ── Common verbs ──────────────────────────────────────────────────────
        'essere':   'From two Latin verbs merged: "esse" (to be) and "sedere" (to sit). That\'s why its conjugation is so irregular!',
        'avere':    'From Latin "habere" (to have/hold) — root of "habit" (what you hold/keep) and "inhibit".',
        'fare':     'From Latin "facere" (to make/do) — root of "fact", "factory", "affect", "perfect", "fashion".',
        'andare':   'Uncertain origin — possibly from Latin "ambulare" (to walk), root of "ambulance" and "amble".',
        'venire':   'From Latin "venire" (to come) — root of "advent", "convention", "prevent", "adventure".',
        'dare':     'From Latin "dare" (to give) — root of "data" (things given), "donation", "edition".',
        'stare':    'From Latin "stare" (to stand) — root of "stable", "statue", "state", "station", "instant".',
        'sapere':   'From Latin "sapere" (to taste/be wise) — root of "savour", "sapient", "Homo sapiens".',
        'potere':   'From Latin "potere" (to be able) — root of "potent", "possible", "possess", "power".',
        'volere':   'From Latin "velle/volere" (to wish) — root of "voluntary", "volition", "benevolent".',
        'dovere':   'From Latin "debere" (to owe) — root of "debt", "due", "duty".',
        'parlare':  'From Latin "parabola" (parable/speech) via Greek — the same root as "parliament" (place of speaking).',
        'mangiare': 'From Latin "manducare" (to chew) — the French "manger" has the same origin.',
        'bere':     'From Latin "bibere" (to drink) — root of "beverage", "imbibe".',
        'dormire':  'From Latin "dormire" — root of "dormitory", "dormant", "dormouse".',
        'studiare': 'From Latin "studium" (zeal/study) — root of "student", "studio", "study".',
        'leggere':  'From Latin "legere" (to gather/read) — root of "lecture", "legend", "elect", "intelligent".',
        'scrivere': 'From Latin "scribere" (to write) — root of "script", "describe", "prescribe", "manuscript".',
        'vedere':   'From Latin "videre" (to see) — root of "video", "vision", "evidence", "provide".',
        'sentire':  'From Latin "sentire" (to feel/hear) — root of "sense", "sentence", "sentiment", "consent".',
        'capire':   'From Latin "capere" (to grasp) — root of "capture", "concept", "capable", "accept".',
        'vivere':   'From Latin "vivere" (to live) — root of "vivid", "survive", "revive", "vital".',
        'correre':  'From Latin "currere" (to run) — root of "current", "course", "occur", "corridor".',
        'aprire':   'From Latin "aperire" (to open) — root of "aperture", "aperitif" (opens the appetite).',
        'trovare':  'Possibly from Greek "tropos" (turn) via "tropare" (to compose verse) — troubadours "found" melodies.',
        'chiamare': 'From Latin "clamare" (to shout/call) — root of "claim", "exclaim", "proclaim".',
        'portare':  'From Latin "portare" (to carry) — root of "transport", "import", "export", "portfolio".',
        'lasciare': 'From Latin "laxare" (to loosen) — root of "lax", "relax", "lease".',
        'pensare':  'From Latin "pensare" (to weigh carefully) — root of "pensive", "pension", "compensate".',
        'lavorare': 'From Latin "laborare" (to toil) — root of "labour", "elaborate", "laboratory".',
        'comprare': 'From Latin "comparare" (to get together/procure) — related to "compare".',
        'pagare':   'From Latin "pacare" (to appease, to satisfy a creditor) — root of "pacify", "peace".',
        'usare':    'From Latin "usare" (to use) — root of "use", "usual", "abuse", "refuse".',
        'uscire':   'From Latin "exire" (to go out) — root of "exit". Italian uscire is technically "ex + ire" (to go out).',
        'partire':  'From Latin "partire" (to divide/depart) — root of "part", "department", "compartment".',
        'arrivare': 'From Latin "arripare" (to reach the shore) — literally "to reach the riverbank" (ripa = bank).',
        'aiutare':  'From Latin "adiutare" (to help) — root of "adjutant" (a military assistant).',
        'giocare':  'From Latin "iocari" (to jest/play) — root of "joke" and "juggler".',
        'vincere':  'From Latin "vincere" (to conquer) — root of "victory", "convince", "invincible".',
        'perdere':  'From Latin "perdere" (to destroy/lose) — root of "perdition", "perdurable".',
        'camminare':'From Latin "caminare" (to walk along a road) — related to "camino" (path), root of "Camino de Santiago".',
        'abitare':  'From Latin "habitare" (to dwell) — root of "habitat", "inhabit", "habit".',
        'tornare':  'From Latin "tornare" (to turn on a lathe) — root of "turn", "tournament", "return".',
        'ricordare':'From Latin "re + cor/cordis" (heart) — to remember is literally "to bring back to the heart".',
        'sperare':  'From Latin "sperare" (to hope) — root of "desperate" (without hope) and "prosper".',
        'cercare':  'From Latin "circare" (to go around/search) — root of "search", "research", "circa".',
        'guardare': 'From Germanic "wardon" (to watch/guard) — root of "guard", "regard", "reward".',
        'ascoltare':'From Latin "auscultare" (to listen carefully) — root of "auscultation" (a doctor listening to the body).',

        # ── Adjectives ────────────────────────────────────────────────────────
        'bello':      'From Latin "bellus" (pretty/fine) — root of "belle", "embellish". Unrelated to "bellum" (war).',
        'buono':      'From Latin "bonus" (good) — root of "bonus", "boon", "bonfire" (good fire).',
        'grande':     'From Latin "grandis" (large/great) — root of "grand", "grandeur", "aggrandise".',
        'piccolo':    'Uncertain origin, possibly pre-Roman. Now famous worldwide as a small flute.',
        'nuovo':      'From Latin "novus" (new) — root of "novel", "novice", "innovation", "renovate".',
        'vecchio':    'From Latin "vetulus" (elderly) — root of "veteran", "inveterate".',
        'lungo':      'From Latin "longus" (long) — root of "longitude", "elongate", "lounge" (a long, relaxed room).',
        'alto':       'From Latin "altus" (high/deep) — root of "altitude", "alto" (high voice), "exalt".',
        'basso':      'From Latin "bassus" (low/stout) — root of "bass" (low voice/sound), "bassoon".',
        'giovane':    'From Latin "iuvenis" (young) — root of "juvenile", "rejuvenate".',
        'vecchio':    'From Latin "vetulus" — root of "veteran". In Italian "vecchio" is affectionate, not rude.',
        'difficile':  'From Latin "difficilis" (not easy) — root of "difficult". Italian uses it far more than English speakers expect.',
        'importante': 'From Latin "importare" (to bring in, to matter) — same root as "import".',
        'simpatico':  'From Greek "sympathetikos" — in Italian it means "nice/likeable", NOT sympathetic! A classic false friend.',
        'morbido':    'From Latin "morbidus" — in Italian means SOFT/GENTLE, not morbid. One of the most surprising false friends!',
        'bravo':      'From Latin "barbarus" (foreign/wild) — evolved to mean "skilled" in Italian, then became a universal cheer.',
        'furbo':      'Possibly from Latin "fur" (thief) — in Italian means "cunning/crafty", used with a hint of admiration.',

        # ── Common expressions ────────────────────────────────────────────────
        'ciao':      'From Venetian "s-ciào vostro" (I am your slave) — a humble greeting that became the world\'s most recognised Italian word.',
        'grazie':    'From Latin "gratia" (grace/favour) — root of "gratitude", "gratuitous", "congratulate".',
        'prego':     'From Latin "precari" (to pray/beg) — used for "you\'re welcome", "please", "go ahead". Wonderfully versatile!',
        'benvenuto': 'Literally "well come" (bene + venuto) — same structure as English "welcome" (well + come).',
        'allora':    'From Latin "ad illam horam" (at that hour) — now means "so/well/then". One of Italians\' favourite filler words.',
        'magari':    'From Greek "makários" (blessed/happy) — in Italian means "maybe/if only". Used to express wistful hope.',
        'purtroppo': 'Literally "too much" (pur + troppo) — evolved to mean "unfortunately". Shows how emphasis can flip meaning.',
        'comunque':  'From Latin "quomodo + unque" — means "anyway/however". One of the most useful Italian connectors.',

        # ── Numbers & quantities ──────────────────────────────────────────────
        'mille':   'From Latin "mille" (thousand) — root of "mile" (mille passuum = a thousand paces), "millennium", "million".',
        'cento':   'From Latin "centum" (hundred) — root of "century", "percent", "centimetre".',
        'numero':  'From Latin "numerus" — root of "number", "numeral", "innumerable".',
        'molto':   'From Latin "multum" (much) — root of "multiply", "multitude", "multiple".',
        'poco':    'From Latin "paucus" (few/little) — root of "pauper" (few possessions).',
        'troppo':  'Possibly from Latin "tropus" (a turn/trope) — in Italian means "too much". Operas end "è troppo tardi!" (it\'s too late!)',

        # ── Technology & modern ───────────────────────────────────────────────
        'computer':   'English loanword — Italian adopted it wholesale in the 1950s, though "calcolatore" was also used.',
        'telefono':   'From Greek "tele" (far) + "phone" (voice) — literally "far-voice". Invented by Antonio Meucci, an Italian, in 1854.',
        'internet':   'English compound. Italy was connected to the internet in 1986, one of the earliest European countries.',
        'cellulare':  'From Latin "cellula" (small room) — refers to the cellular network structure of small transmission zones.',

        # ── Culture & extras ──────────────────────────────────────────────────
        'carnevale':  'From Latin "carne vale" (farewell to meat) — the feast before Lent began. Venice\'s carnival dates to the 11th century.',
        'opera':      'From Latin "opus/operis" (work) — literally "a work". Italy invented opera around 1600 in Florence.',
        'gondola':    'Possibly from Latin "cymba" or Greek "kondy" — Venice has had gondolas since the 11th century.',
        'balcone':    'From Italian "balcone" — root of English "balcony". Romeo and Juliet\'s scene made it famous worldwide.',
        'ombrello':   'From Latin "umbra" (shadow) — root of "umbrella" (little shadow) and "ombre".',
        'banca':      'From Germanic "bank" (bench) — medieval money-changers did business on benches in the marketplace.',
        'giornale':   'From Latin "diurnalis" (daily) — root of "journal", "journey" (a day\'s travel), "diurnal".',
        'campagna':   'From Latin "campania" (open flat land) — root of "campaign" (military operations in open fields).',
        'festa':      'From Latin "festum" (feast/holiday) — root of "festival", "feast", "festive".',
        'musica':     'From Greek "mousikē" — named after the Muses. Italy gave the world musical notation, the piano, opera, and the violin.',
        'violino':    'From Italian "viola" (stringed instrument) — Cremona, Italy, is still considered the world capital of violin-making (Stradivari was from here).',
        'pianoforte': 'Invented by Bartolomeo Cristofori in Florence around 1700 — literally "soft-loud" (piano + forte), describing its dynamic range.',
        'cappuccino': 'Named after the Capuchin friars — the drink\'s colour resembles their brown robes and tonsured heads.',
    }

    # General Italian fun facts shown when no word-specific entry is found
    general_facts = [
        '🇮🇹 Italian is one of the closest living languages to Latin — about 89% of Italian words come directly from Latin.',
        '🎵 Italian is the language of music — nearly all musical terms worldwide (allegro, forte, piano, soprano) are Italian.',
        '🍕 Italy has over 350 distinct pasta shapes, each designed for different sauces and regional traditions.',
        '📚 The first university in the world was the University of Bologna, founded in 1088.',
        '🏛️ Rome was founded in 753 BC — the city is over 2,700 years old.',
        '🎨 Italian was the language of the Renaissance — da Vinci, Michelangelo, Raphael, and Botticelli all wrote in Italian.',
        '🌍 Italian is spoken by about 85 million people worldwide, and is one of the EU\'s 24 official languages.',
        '🗺️ Italy only became a unified country in 1861 — before that it was a patchwork of kingdoms, city-states, and duchies.',
        '🍷 Italy produces more wine than any other country in the world — over 5 billion litres per year.',
        '👗 Italy is home to many of the world\'s top fashion houses: Gucci, Versace, Prada, Armani, and Dolce & Gabbana.',
        '🚗 The world\'s oldest car race, the Mille Miglia, is Italian — 1,000 miles through the Italian countryside.',
        '🏗️ Italian has two words for "you": "tu" (informal) and "Lei" (formal) — the formal uses the 3rd person, a historical quirk.',
        '🔤 The letters J, K, W, X, and Y do not appear in native Italian words — they only appear in foreign loanwords.',
        '🎭 Italy invented the theatrical form of Commedia dell\'Arte in the 16th century — the origins of clowns and pantomime.',
        '⚽ The Italian national football team is called the "Azzurri" (the Blues) — after the blue of the House of Savoy.',
        '🌋 Italy has more active volcanoes than any other European country: Vesuvius, Etna, Stromboli, and Campi Flegrei.',
        '🤌 Italian has a rich tradition of hand gestures — some linguists count over 250 distinct gesture meanings.',
        '📖 Dante\'s Divine Comedy (written 1308–1320) did more to standardise Italian than any other single work.',
        '🏆 Italy has won the FIFA World Cup four times (1934, 1938, 1982, 2006) — second only to Brazil.',
        '🍦 Gelato has a lower fat content and less air than ice cream, making it denser and more intensely flavoured.',
    ]

    import random as _random

    # Strip articles and normalise the lookup word
    word_clean = (word.lower()
                  .replace('il ', '').replace('la ', '').replace('i ', '')
                  .replace('le ', '').replace('gli ', '').replace('lo ', '')
                  .replace("l'", '').strip())

    # Direct lookup first
    fact = etymology_facts.get(word_clean)
    if fact:
        return fact

    # Try the first word only (handles phrases like "fare il bucato")
    first_word = word_clean.split()[0] if ' ' in word_clean else None
    if first_word:
        fact = etymology_facts.get(first_word)
        if fact:
            return fact

    # Fall back to a random general Italian fact
    return _random.choice(general_facts)


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

    # Normalise apostrophe spacing: "l' isola" → "l'isola"
    def _norm(s):
        return re.sub(r"'\s+", "'", remove_accents(s.strip().lower()))
    user_normalized = _norm(user_answer)
    correct_normalized = _norm(correct_answer)

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

    # For negation transform questions: strip punctuation before comparing (Bug-0118)
    # Users shouldn't fail just because they omitted a period or exclamation mark
    if question_type == 'negation':
        import string as _string
        strip_punct = lambda t: t.translate(str.maketrans('', '', _string.punctuation))
        if strip_punct(user_normalized) == strip_punct(correct_normalized):
            return True, correct_answer

    # Standard matching for other types
    # Split correct answer by "/" or ", " to get all acceptable answers
    # e.g. "under/below" or "under, below" should both accept just "under"
    raw_answers = re.split(r'/|,\s*', correct_answer)
    acceptable_answers = [remove_accents(ans.strip().lower()) for ans in raw_answers]

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

    # Synonym / near-match check for vocabulary (single words or short phrases)
    # Catches cases like "small" vs "little", "bike" vs "bicycle", etc.
    if not is_correct:
        vocab_synonyms = {
            # Size / degree
            'small': ['little', 'tiny', 'petite'],
            'little': ['small', 'tiny'],
            'big': ['large', 'great'],
            'large': ['big', 'great'],
            # Bike
            'bike': ['bicycle', 'bici'],
            'bicycle': ['bike', 'bici'],
            'bici': ['bicycle', 'bike', 'bicicletta'],
            'bicicletta': ['bike', 'bicycle', 'bici'],
            # Common verb synonyms
            'to go': ['to leave', 'to walk'],
            'to look': ['to watch', 'to see'],
            'to see': ['to look', 'to watch'],
            'to wish': ['to want', 'to desire'],
            'to want': ['to wish', 'to desire'],
            'to speak': ['to talk', 'to say'],
            'to talk': ['to speak', 'to chat'],
            'to listen': ['to hear'],
            'to hear': ['to listen'],
            'to get': ['to obtain', 'to receive', 'to take'],
            'to take': ['to get', 'to grab'],
            'to like': ['to enjoy', 'to love'],
            'to enjoy': ['to like', 'to love'],
            'to begin': ['to start'],
            'to start': ['to begin'],
            'to finish': ['to end', 'to complete'],
            'to end': ['to finish', 'to complete'],
            'to live': ['to reside'],
            'to work': ['to labour', 'to labor'],
            'to wait': ['to wait for'],
            'to wait for': ['to wait'],
            'to know': ['to understand', 'to recognise', 'to recognize'],
            'to understand': ['to know', 'to comprehend'],
            'to help': ['to assist', 'to aid'],
            'to try': ['to attempt'],
            'to walk': ['to go on foot', 'to stroll'],
            # Adjective synonyms
            'beautiful': ['pretty', 'lovely', 'gorgeous'],
            'pretty': ['beautiful', 'lovely'],
            'lovely': ['beautiful', 'pretty'],
            'happy': ['glad', 'joyful', 'pleased'],
            'glad': ['happy', 'pleased'],
            'sad': ['unhappy', 'upset'],
            'tired': ['exhausted', 'sleepy', 'weary'],
            'angry': ['upset', 'annoyed', 'cross'],
            'correct': ['right'],
            'right': ['correct'],
            'wrong': ['incorrect'],
            'incorrect': ['wrong'],
            'fast': ['quick', 'rapid'],
            'quick': ['fast', 'rapid'],
            'slow': ['sluggish'],
            # Noun synonyms
            'mum': ['mom', 'mother', 'mamma'],
            'mom': ['mum', 'mother', 'mamma'],
            'mother': ['mum', 'mom', 'mamma'],
            'dad': ['father', 'papa', 'papà'],
            'father': ['dad', 'papa', 'papà'],
            'flat': ['apartment'],
            'apartment': ['flat'],
            'shop': ['store', 'negozio'],
            'store': ['shop'],
            'film': ['movie', 'cinema'],
            'movie': ['film', 'cinema'],
            'friend': ['mate', 'pal'],
            # Holiday / vacation
            'holiday': ['vacation', 'holidays'],
            'vacation': ['holiday', 'holidays'],
            'holidays': ['holiday', 'vacation'],
            # Autumn / fall
            'autumn': ['fall'],
            'fall': ['autumn'],
            # Lift / elevator
            'lift': ['elevator'],
            'elevator': ['lift'],
            # Jumper / sweater
            'jumper': ['sweater', 'pullover'],
            'sweater': ['jumper', 'pullover'],
            # Trousers / pants
            'trousers': ['pants'],
            'pants': ['trousers'],
            # Chemist / pharmacy
            'chemist': ['pharmacy', 'pharmacist'],
            'pharmacy': ['chemist', 'drugstore'],
            # Theatre / theater
            'theatre': ['theater'],
            'theater': ['theatre'],
            # Colour / color
            'colour': ['color'],
            'color': ['colour'],
            # Neighbour / neighbor
            'neighbour': ['neighbor'],
            'neighbor': ['neighbour'],
            # Travelling / traveling
            'travelling': ['traveling'],
            'traveling': ['travelling'],
            # Rubbish / garbage / trash
            'rubbish': ['garbage', 'trash'],
            'garbage': ['rubbish', 'trash'],
            'trash': ['rubbish', 'garbage'],
            # Mobile phone / cell phone
            'mobile phone': ['cell phone', 'cellphone', 'mobile'],
            'cell phone': ['mobile phone', 'mobile'],
            'mobile': ['mobile phone', 'cell phone'],
            # Football / soccer
            'football': ['soccer'],
            'soccer': ['football'],
            # Post office / mail
            'post office': ['mail office'],
            # Town hall / city hall
            'town hall': ['city hall'],
            'city hall': ['town hall'],
            # Healthcare noun synonyms
            'illness': ['sickness', 'disease'],
            'sickness': ['illness', 'disease'],
            'disease': ['illness', 'sickness'],
            'stomach ache': ['stomachache', 'stomach pain'],
            'stomachache': ['stomach ache', 'stomach pain'],
            'headache': ['head ache'],
            'toothache': ['tooth ache'],
            # Clever / intelligent / smart
            'clever': ['intelligent', 'smart', 'bright'],
            'intelligent': ['clever', 'smart', 'bright'],
            'smart': ['clever', 'intelligent'],
            # Hardworking / diligent / studious
            'hardworking': ['diligent', 'studious', 'hard-working'],
            'diligent': ['hardworking', 'studious'],
            # Brave / courageous
            'brave': ['courageous', 'bold'],
            'courageous': ['brave', 'bold'],
            # Kind / nice / gentle
            'kind': ['nice', 'gentle', 'caring'],
            'gentle': ['kind', 'nice'],
            # Selfish / self-centred
            'selfish': ['self-centred', 'self-centered'],
            # Shy / timid
            'shy': ['timid', 'bashful'],
            'timid': ['shy', 'bashful'],
        }

        user_strip = user_normalized.lstrip('to ') if user_normalized.startswith('to ') else user_normalized
        user_no_the = user_normalized[4:] if user_normalized.startswith('the ') else user_normalized
        for acc in all_acceptable:
            acc_strip = acc.lstrip('to ') if acc.startswith('to ') else acc
            acc_no_the = acc[4:] if acc.startswith('the ') else acc
            syns = (vocab_synonyms.get(acc, []) +
                    vocab_synonyms.get(acc_no_the, []) +
                    vocab_synonyms.get(f'to {acc_strip}', []))
            # Build a flat set of synonym bare forms for comparison
            syns_no_the = [s[4:] if s.startswith('the ') else s for s in syns]
            if (user_normalized in syns or
                    user_strip in [s.lstrip('to ') for s in syns] or
                    user_no_the in syns_no_the):
                is_correct = True
                break

    # Bug-0125: Accept if user wrote a longer answer that contains all words of
    # the correct answer (e.g. "the beach and the sea" for "the beach")
    if not is_correct:
        correct_words_set = set(correct_normalized.split())
        user_words_set = set(user_normalized.split())
        if correct_words_set and correct_words_set.issubset(user_words_set) and len(user_words_set) > len(correct_words_set):
            is_correct = True

    # For display, use the first option if multiple (handles both "/" and ", " separators)
    display_answer = re.split(r'/|,\s*', correct_answer)[0].strip() if ('/' in correct_answer or ',' in correct_answer) else correct_answer

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

    if request.method == 'GET':
        # Always show setup form; pre-select direction if passed in URL
        direction_hint = request.args.get('direction', 'it_to_en')
        return render_template('vocabulary_quiz_setup.html', level=level, direction_hint=direction_hint)

    # POST: get direction and count from form
    direction = request.form.get('direction', 'it_to_en')
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

    # Add etymology / fun fact — shown on all question types
    # Try the Italian word in the question first, then fall back to a general fact
    italian_word = (question.get('italian')
                    or question.get('infinitive')
                    or display_answer)
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


@app.route('/reflexive-passato-prossimo', methods=['GET', 'POST'])
def reflexive_passato_prossimo():
    """Reflexive verbs in passato prossimo practice (A2)."""
    return create_practice_route(
        practice_type='reflexive_passato_prossimo',
        generator_method='generate_reflexive_passato_prossimo',
        setup_template='reflexive_passato_prossimo_setup.html',
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


@app.route('/verb-prepositions', methods=['GET', 'POST'])
def verb_prepositions():
    """Verbs with fixed prepositions practice (verbi con preposizione)."""
    return create_practice_route(
        practice_type='verb_prepositions',
        generator_method='generate_verb_prepositions',
        setup_template='verb_prepositions_setup.html',
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
