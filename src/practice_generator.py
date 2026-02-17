"""
Practice Generator Module
Generates different types of practice exercises based on topics and performance.
"""

import random
from typing import List, Dict, Tuple
from database import ItalianDatabase

class PracticeGenerator:
    def __init__(self, db: ItalianDatabase):
        self.db = db

    def _get_verb_level(self, level: str) -> str:
        """Get the appropriate level for verb queries, with GCSE fallback to B2."""
        # GCSE uses B2 verbs as they are similar difficulty
        if level == 'GCSE':
            return 'B2'
        return level

    def generate_verb_conjugation_drill(self, level: str = "A1", count: int = 10) -> List[Dict]:
        """Generate verb conjugation practice questions."""
        cursor = self.db.conn.cursor()

        # Get the appropriate level (GCSE → B2)
        query_level = self._get_verb_level(level)

        # Get random verbs from the specified level
        cursor.execute("""
            SELECT DISTINCT infinitive, english, verb_type, tense
            FROM verb_conjugations
            WHERE level = ?
            ORDER BY RANDOM()
            LIMIT ?
        """, (query_level, count))
        
        verbs = cursor.fetchall()
        questions = []
        
        for verb in verbs:
            infinitive, english, verb_type, tense = verb
            
            # Pick a random person
            persons = ["io", "tu", "lui_lei", "noi", "voi", "loro"]
            person = random.choice(persons)
            
            # Get the correct conjugation
            cursor.execute("""
                SELECT conjugated_form, auxiliary
                FROM verb_conjugations
                WHERE infinitive = ? AND tense = ? AND person = ?
            """, (infinitive, tense, person))
            
            result = cursor.fetchone()
            if result:
                conjugated, auxiliary = result
                
                # Format the question
                person_display = {
                    "io": "io", "tu": "tu", "lui_lei": "lui/lei",
                    "noi": "noi", "voi": "voi", "loro": "loro"
                }
                
                if tense == "passato_prossimo" and auxiliary:
                    # For past tense, show the auxiliary conjugation
                    aux_forms = {
                        "io": "ho" if auxiliary == "avere" else "sono",
                        "tu": "hai" if auxiliary == "avere" else "sei",
                        "lui_lei": "ha" if auxiliary == "avere" else "è",
                        "noi": "abbiamo" if auxiliary == "avere" else "siamo",
                        "voi": "avete" if auxiliary == "avere" else "siete",
                        "loro": "hanno" if auxiliary == "avere" else "sono"
                    }
                    full_answer = f"{aux_forms[person]} {conjugated}"
                    question_text = f"Conjugate '{infinitive}' ({english}) in {tense} for {person_display[person]}"
                else:
                    full_answer = conjugated
                    question_text = f"Conjugate '{infinitive}' ({english}) for {person_display[person]}"
                
                questions.append({
                    "question": question_text,
                    "answer": full_answer,
                    "infinitive": infinitive,
                    "person": person,
                    "tense": tense,
                    "type": "verb_conjugation"
                })
        
        return questions
    
    def generate_vocabulary_quiz(self, level: str = "A1", count: int = 10, 
                                 direction: str = "it_to_en") -> List[Dict]:
        """Generate vocabulary translation questions.
        
        Args:
            level: Language level (A1, A2, etc.)
            count: Number of questions
            direction: 'it_to_en' (Italian to English) or 'en_to_it' (English to Italian)
        """
        cursor = self.db.conn.cursor()
        
        cursor.execute("""
            SELECT italian, english, word_type, gender, category
            FROM vocabulary
            WHERE level = ?
            ORDER BY RANDOM()
            LIMIT ?
        """, (level, count))
        
        words = cursor.fetchall()
        questions = []
        
        for word in words:
            italian, english, word_type, gender, category = word
            
            if direction == "it_to_en":
                question_text = f"Translate: {italian}"
                answer = english
            else:
                question_text = f"Translate: {english}"
                answer = italian
                if gender and word_type == "noun":
                    # Accept answers with or without articles
                    article = "il" if gender == "masculine" else "la"
                    answer = f"{article} {italian}"
            
            questions.append({
                "question": question_text,
                "answer": answer,
                "italian": italian,
                "english": english,
                "type": "vocabulary",
                "category": category
            })
        
        return questions
    
    def generate_fill_in_blank(self, level: str = "A1", count: int = 10) -> List[Dict]:
        """Generate fill-in-the-blank exercises with common sentence patterns."""
        
        # Sample sentence templates (you can expand this)
        templates = [
            ("Io ____ italiano.", "parlo", "I speak Italian", "verb"),
            ("Tu ____ al cinema?", "vai", "Do you go to the cinema?", "verb"),
            ("Lei ____ una studentessa.", "è", "She is a student", "verb"),
            ("Noi ____ a casa.", "siamo", "We are at home", "verb"),
            ("____ mi chiamo Marco.", "Io", "I am called Marco", "pronoun"),
            ("Voi ____ fame?", "avete", "Are you hungry?", "verb"),
            ("Loro ____ al bar.", "vanno", "They go to the bar", "verb"),
            ("____ è il tuo nome?", "Qual", "What is your name?", "question_word"),
            ("Mi piace ____ caffè.", "il", "I like coffee", "article"),
            ("Vorrei ____ acqua.", "dell'", "I would like some water", "partitive"),
        ]
        
        # Select random templates
        selected = random.sample(templates, min(count, len(templates)))
        questions = []
        
        for template, answer, english, blank_type in selected:
            questions.append({
                "question": f"Fill in the blank: {template}\n(English: {english})",
                "answer": answer,
                "type": "fill_in_blank",
                "blank_type": blank_type
            })
        
        return questions
    
    def generate_multiple_choice(self, level: str = "A1", count: int = 10) -> List[Dict]:
        """Generate multiple choice questions covering all grammar areas."""
        all_questions = []
        
        # 1. VERB CONJUGATIONS (present, passato, futuro)
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT DISTINCT infinitive, english, verb_type, tense
            FROM verb_conjugations
            WHERE level = ?
            ORDER BY RANDOM()
            LIMIT 3
        """, (level,))
        
        verbs = cursor.fetchall()
        
        for verb in verbs:
            infinitive, english, verb_type, tense = verb
            person = random.choice(["io", "tu", "lui_lei", "noi", "voi", "loro"])
            
            # Get correct answer
            cursor.execute("""
                SELECT conjugated_form
                FROM verb_conjugations
                WHERE infinitive = ? AND tense = ? AND person = ?
            """, (infinitive, tense, person))
            
            correct = cursor.fetchone()
            if not correct:
                continue
            
            correct_answer = correct[0]
            
            # Get wrong answers (other conjugations of same verb)
            cursor.execute("""
                SELECT conjugated_form
                FROM verb_conjugations
                WHERE infinitive = ? AND tense = ? AND person != ? AND conjugated_form != ?
                ORDER BY RANDOM()
                LIMIT 3
            """, (infinitive, tense, person, correct_answer))
            
            wrong_answers = [row[0] for row in cursor.fetchall()]
            
            if len(wrong_answers) < 3:
                continue
            
            # Combine and shuffle
            all_choices = [correct_answer] + wrong_answers
            random.shuffle(all_choices)
            
            person_display = {
                "io": "io", "tu": "tu", "lui_lei": "lui/lei",
                "noi": "noi", "voi": "voi", "loro": "loro"
            }
            
            all_questions.append({
                "question": f"Conjugate '{infinitive}' ({english}) for {person_display[person]}",
                "choices": all_choices,
                "answer": correct_answer,
                "type": "multiple_choice"
            })
        
        # 2. IRREGULAR PASSATO PROSSIMO
        irregular_verbs = [
            ("fare", "fatto"), ("dire", "detto"), ("leggere", "letto"),
            ("vedere", "visto"), ("scrivere", "scritto"), ("prendere", "preso"),
            ("mettere", "messo"), ("essere", "stato"), ("venire", "venuto"),
        ]
        
        for infinitive, correct_pp in random.sample(irregular_verbs, 2):
            # Generate plausible wrong answers
            wrong_endings = ["ato", "uto", "ito"]
            stem = infinitive[:-3] if infinitive.endswith(("are", "ere", "ire")) else infinitive[:-2]
            wrong_answers = [stem + ending for ending in wrong_endings if stem + ending != correct_pp]
            
            # Add some other real irregular forms
            other_irregulars = [pp for _, pp in irregular_verbs if pp != correct_pp]
            wrong_answers.extend(random.sample(other_irregulars, min(2, len(other_irregulars))))
            wrong_answers = wrong_answers[:3]
            
            all_choices = [correct_pp] + wrong_answers
            random.shuffle(all_choices)
            
            all_questions.append({
                "question": f"What is the past participle of '{infinitive}'?",
                "choices": all_choices,
                "answer": correct_pp,
                "type": "multiple_choice"
            })
        
        # 3. AVERE VS ESSERE
        auxiliary_choices = [
            ("andare", "essere", "movement"), ("mangiare", "avere", "transitive"),
            ("arrivare", "essere", "movement"), ("parlare", "avere", "transitive"),
            ("uscire", "essere", "movement"), ("dormire", "avere", "no movement"),
        ]
        
        for infinitive, correct_aux, reason in random.sample(auxiliary_choices, 2):
            all_choices = ["avere", "essere"]
            
            all_questions.append({
                "question": f"Which auxiliary for '{infinitive}' in passato prossimo?",
                "choices": all_choices,
                "answer": correct_aux,
                "type": "multiple_choice"
            })
        
        # 4. ARTICULATED PREPOSITIONS
        prep_choices = [
            ("Vado ___ cinema", ["al", "del", "nel", "dal"], "al"),
            ("Vengo ___ stazione", ["dalla", "alla", "nella", "sulla"], "dalla"),
            ("Sono ___ parco", ["nel", "al", "del", "sul"], "nel"),
            ("Il libro ___ studente", ["dello", "allo", "nello", "sullo"], "dello"),
        ]
        
        for question, choices, answer in random.sample(prep_choices, 2):
            all_questions.append({
                "question": f"Fill in: {question}",
                "choices": choices,
                "answer": answer,
                "type": "multiple_choice"
            })
        
        # 5. TIME PREPOSITIONS
        time_prep_choices = [
            ("Ho studiato italiano ___ tre anni", ["per", "da", "a", "fa"], "per"),
            ("Studio italiano ___ due anni", ["da", "per", "a", "fa"], "da"),
            ("Ho finito la scuola ___ 18 anni", ["a", "per", "da", "fa"], "a"),
            ("Sono arrivato due ore ___", ["fa", "per", "da", "a"], "fa"),
        ]
        
        for question, choices, answer in random.sample(time_prep_choices, 2):
            all_questions.append({
                "question": question,
                "choices": choices,
                "answer": answer,
                "type": "multiple_choice"
            })
        
        # 6. NEGATIONS
        negation_choices = [
            ("Non vado ___ al cinema", ["mai", "più", "niente", "nessuno"], "mai"),
            ("Non lavoro ___ qui", ["più", "mai", "niente", "nessuno"], "più"),
            ("Non ho ___ da fare", ["niente", "mai", "più", "nessuno"], "niente"),
            ("Non conosco ___", ["nessuno", "niente", "mai", "più"], "nessuno"),
        ]
        
        for question, choices, answer in random.sample(negation_choices, 2):
            all_questions.append({
                "question": f"Fill in the negation: {question}",
                "choices": choices,
                "answer": answer,
                "type": "multiple_choice"
            })
        
        # 7. REFLEXIVE PRONOUNS
        reflexive_choices = [
            ("Io ___ alzo", ["mi", "ti", "si", "ci"], "mi"),
            ("Tu ___ chiami come?", ["ti", "mi", "si", "vi"], "ti"),
            ("Noi ___ divertiamo", ["ci", "vi", "si", "mi"], "ci"),
            ("Loro ___ preparano", ["si", "ci", "vi", "ti"], "si"),
        ]
        
        for question, choices, answer in random.sample(reflexive_choices, 2):
            all_questions.append({
                "question": question,
                "choices": choices,
                "answer": answer,
                "type": "multiple_choice"
            })
        
        # Shuffle all questions and return the requested count
        random.shuffle(all_questions)
        return all_questions[:count]
    
    def get_focused_practice(self, topic_name: str, count: int = 10) -> List[Dict]:
        """Generate practice focused on a specific topic."""
        cursor = self.db.conn.cursor()
        
        # Get the topic
        cursor.execute("SELECT * FROM topics WHERE name = ?", (topic_name,))
        topic = cursor.fetchone()
        
        if not topic:
            return []
        
        topic_dict = dict(topic)
        category = topic_dict['category']
        level = topic_dict['level']
        
        # Generate appropriate practice based on category
        if category == "verbs":
            return self.generate_verb_conjugation_drill(level, count)
        elif category in ["pronouns", "articles", "prepositions"]:
            return self.generate_fill_in_blank(level, count)
        else:
            return self.generate_vocabulary_quiz(level, count)
    
    def generate_irregular_passato_prossimo(self, count: int = 10) -> List[Dict]:
        """Practice irregular passato prossimo forms."""
        
        # Irregular past participles from your notes
        irregular_verbs = [
            ("fare", "to do/make", "fatto"),
            ("dire", "to say", "detto"),
            ("leggere", "to read", "letto"),
            ("aprire", "to open", "aperto"),
            ("spegnere", "to turn off", "spento"),
            ("scegliere", "to choose", "scelto"),
            ("prendere", "to take", "preso"),
            ("spendere", "to spend", "speso"),
            ("decidere", "to decide", "deciso"),
            ("chiudere", "to close", "chiuso"),
            ("chiedere", "to ask", "chiesto"),
            ("perdere", "to lose", "perso"),
            ("correre", "to run", "corso"),
            ("mettere", "to put", "messo"),
            ("essere", "to be", "stato"),
            ("vivere", "to live", "vissuto"),
            ("venire", "to come", "venuto"),
            ("scrivere", "to write", "scritto"),
            ("vedere", "to see", "visto"),
            ("rispondere", "to answer", "risposto"),
        ]
        
        questions = []
        selected = random.sample(irregular_verbs, min(count, len(irregular_verbs)))
        
        for infinitive, english, past_participle in selected:
            person = random.choice(["io", "tu", "lui_lei", "noi", "voi", "loro"])
            
            person_display = {
                "io": "io", "tu": "tu", "lui_lei": "lui/lei",
                "noi": "noi", "voi": "voi", "loro": "loro"
            }
            
            questions.append({
                "question": f"What is the past participle of '{infinitive}' ({english})?",
                "answer": past_participle,
                "type": "irregular_passato",
                "infinitive": infinitive
            })
        
        return questions
    
    def generate_auxiliary_choice(self, count: int = 10) -> List[Dict]:
        """Practice choosing between avere and essere for passato prossimo."""
        
        # Verbs and their correct auxiliaries
        verb_auxiliaries = [
            # AVERE verbs (transitive, no movement)
            ("parlare", "to speak", "avere", "Transitive verb"),
            ("mangiare", "to eat", "avere", "Transitive verb"),
            ("vedere", "to see", "avere", "Transitive verb"),
            ("fare", "to do/make", "avere", "Transitive verb"),
            ("leggere", "to read", "avere", "Transitive verb"),
            ("scrivere", "to write", "avere", "Transitive verb"),
            ("dormire", "to sleep", "avere", "No movement"),
            ("lavorare", "to work", "avere", "No movement"),
            ("bere", "to drink", "avere", "Transitive verb"),
            ("comprare", "to buy", "avere", "Transitive verb"),
            ("vendere", "to sell", "avere", "Transitive verb"),
            ("sentire", "to hear/feel", "avere", "Transitive verb"),
            ("aprire", "to open", "avere", "Transitive verb"),
            ("chiudere", "to close", "avere", "Transitive verb"),
            ("prendere", "to take", "avere", "Transitive verb"),
            ("mettere", "to put", "avere", "Transitive verb"),
            ("dire", "to say", "avere", "Transitive verb"),
            ("sapere", "to know", "avere", "Mental state"),
            ("conoscere", "to know (person)", "avere", "Transitive verb"),
            ("capire", "to understand", "avere", "Mental state"),
            ("pensare", "to think", "avere", "Mental state"),
            ("credere", "to believe", "avere", "Mental state"),
            ("volere", "to want", "avere", "Modal verb"),
            ("potere", "to be able", "avere", "Modal verb"),
            ("dovere", "to have to", "avere", "Modal verb"),
            ("cercare", "to look for", "avere", "Transitive verb"),
            ("trovare", "to find", "avere", "Transitive verb"),
            ("perdere", "to lose", "avere", "Transitive verb"),
            ("ricevere", "to receive", "avere", "Transitive verb"),
            ("dare", "to give", "avere", "Transitive verb"),
            ("portare", "to bring/carry", "avere", "Transitive verb"),
            ("pagare", "to pay", "avere", "Transitive verb"),
            ("studiare", "to study", "avere", "Transitive verb"),
            ("imparare", "to learn", "avere", "Transitive verb"),
            ("insegnare", "to teach", "avere", "Transitive verb"),
            ("aiutare", "to help", "avere", "Transitive verb"),
            ("aspettare", "to wait", "avere", "Transitive verb"),
            ("chiamare", "to call", "avere", "Transitive verb"),
            ("ascoltare", "to listen", "avere", "Transitive verb"),
            ("guardare", "to watch", "avere", "Transitive verb"),

            # ESSERE verbs (movement, change of state, reflexive-like)
            ("andare", "to go", "essere", "Movement verb"),
            ("venire", "to come", "essere", "Movement verb"),
            ("arrivare", "to arrive", "essere", "Movement verb"),
            ("partire", "to leave", "essere", "Movement verb"),
            ("uscire", "to go out", "essere", "Movement verb"),
            ("entrare", "to enter", "essere", "Movement verb"),
            ("tornare", "to return", "essere", "Movement verb"),
            ("essere", "to be", "essere", "Essere itself"),
            ("stare", "to stay", "essere", "State verb"),
            ("rimanere", "to remain", "essere", "State verb"),
            ("nascere", "to be born", "essere", "Change of state"),
            ("morire", "to die", "essere", "Change of state"),
            ("cadere", "to fall", "essere", "Movement verb"),
            ("salire", "to go up", "essere", "Movement verb"),
            ("scendere", "to go down", "essere", "Movement verb"),
            ("diventare", "to become", "essere", "Change of state"),
            ("crescere", "to grow", "essere", "Change of state"),
            ("restare", "to stay/remain", "essere", "State verb"),
            ("succedere", "to happen", "essere", "Impersonal verb"),
            ("accadere", "to happen", "essere", "Impersonal verb"),
        ]
        
        questions = []
        selected = random.sample(verb_auxiliaries, min(count, len(verb_auxiliaries)))
        
        for infinitive, english, correct_aux, reason in selected:
            questions.append({
                "question": f"Which auxiliary for '{infinitive}' ({english}) in passato prossimo?",
                "choices": ["avere", "essere"],
                "answer": correct_aux,
                "reason": reason,
                "type": "auxiliary_choice"
            })
        
        return questions
    
    def generate_futuro_semplice(self, count: int = 10) -> List[Dict]:
        """Practice futuro semplice conjugations."""
        
        # Future tense verbs with their forms
        future_verbs = [
            # Regular -ARE (parlare becomes parlerò)
            ("parlare", "to speak", "regular_are", {
                "io": "parlerò", "tu": "parlerai", "lui_lei": "parlerà",
                "noi": "parleremo", "voi": "parlerete", "loro": "parleranno"
            }),
            
            # Regular -ERE (vedere becomes vedrò)
            ("vedere", "to see", "regular_ere", {
                "io": "vedrò", "tu": "vedrai", "lui_lei": "vedrà",
                "noi": "vedremo", "voi": "vedrete", "loro": "vedranno"
            }),
            
            # Regular -IRE (dormire becomes dormirò)
            ("dormire", "to sleep", "regular_ire", {
                "io": "dormirò", "tu": "dormirai", "lui_lei": "dormirà",
                "noi": "dormiremo", "voi": "dormirete", "loro": "dormiranno"
            }),
            
            # Irregular verbs
            ("essere", "to be", "irregular", {
                "io": "sarò", "tu": "sarai", "lui_lei": "sarà",
                "noi": "saremo", "voi": "sarete", "loro": "saranno"
            }),
            
            ("avere", "to have", "irregular", {
                "io": "avrò", "tu": "avrai", "lui_lei": "avrà",
                "noi": "avremo", "voi": "avrete", "loro": "avranno"
            }),
            
            ("fare", "to do/make", "irregular", {
                "io": "farò", "tu": "farai", "lui_lei": "farà",
                "noi": "faremo", "voi": "farete", "loro": "faranno"
            }),
            
            ("andare", "to go", "irregular", {
                "io": "andrò", "tu": "andrai", "lui_lei": "andrà",
                "noi": "andremo", "voi": "andrete", "loro": "andranno"
            }),
            
            ("volere", "to want", "irregular", {
                "io": "vorrò", "tu": "vorrai", "lui_lei": "vorrà",
                "noi": "vorremo", "voi": "vorrete", "loro": "vorranno"
            }),

            # More regular -ARE verbs
            ("mangiare", "to eat", "regular_are", {
                "io": "mangerò", "tu": "mangerai", "lui_lei": "mangerà",
                "noi": "mangeremo", "voi": "mangerete", "loro": "mangeranno"
            }),
            ("lavorare", "to work", "regular_are", {
                "io": "lavorerò", "tu": "lavorerai", "lui_lei": "lavorerà",
                "noi": "lavoreremo", "voi": "lavorerete", "loro": "lavoreranno"
            }),
            ("studiare", "to study", "regular_are", {
                "io": "studierò", "tu": "studierai", "lui_lei": "studierà",
                "noi": "studieremo", "voi": "studierete", "loro": "studieranno"
            }),
            ("comprare", "to buy", "regular_are", {
                "io": "comprerò", "tu": "comprerai", "lui_lei": "comprerà",
                "noi": "compreremo", "voi": "comprerete", "loro": "compreranno"
            }),
            ("ascoltare", "to listen", "regular_are", {
                "io": "ascolterò", "tu": "ascolterai", "lui_lei": "ascolterà",
                "noi": "ascolteremo", "voi": "ascolterete", "loro": "ascolteranno"
            }),
            ("guardare", "to watch", "regular_are", {
                "io": "guarderò", "tu": "guarderai", "lui_lei": "guarderà",
                "noi": "guarderemo", "voi": "guarderete", "loro": "guarderanno"
            }),
            ("chiamare", "to call", "regular_are", {
                "io": "chiamerò", "tu": "chiamerai", "lui_lei": "chiamerà",
                "noi": "chiameremo", "voi": "chiamerete", "loro": "chiameranno"
            }),
            ("arrivare", "to arrive", "regular_are", {
                "io": "arriverò", "tu": "arriverai", "lui_lei": "arriverà",
                "noi": "arriveremo", "voi": "arriverete", "loro": "arriveranno"
            }),
            ("tornare", "to return", "regular_are", {
                "io": "tornerò", "tu": "tornerai", "lui_lei": "tornerà",
                "noi": "torneremo", "voi": "tornerete", "loro": "torneranno"
            }),
            ("visitare", "to visit", "regular_are", {
                "io": "visiterò", "tu": "visiterai", "lui_lei": "visiterà",
                "noi": "visiteremo", "voi": "visiterete", "loro": "visiteranno"
            }),
            ("incontrare", "to meet", "regular_are", {
                "io": "incontrerò", "tu": "incontrerai", "lui_lei": "incontrerà",
                "noi": "incontreremo", "voi": "incontrerete", "loro": "incontreranno"
            }),
            ("viaggiare", "to travel", "regular_are", {
                "io": "viaggerò", "tu": "viaggerai", "lui_lei": "viaggerà",
                "noi": "viaggeremo", "voi": "viaggerete", "loro": "viaggeranno"
            }),
            ("pensare", "to think", "regular_are", {
                "io": "penserò", "tu": "penserai", "lui_lei": "penserà",
                "noi": "penseremo", "voi": "penserete", "loro": "penseranno"
            }),
            ("sperare", "to hope", "regular_are", {
                "io": "spererò", "tu": "spererai", "lui_lei": "spererà",
                "noi": "spereremo", "voi": "spererete", "loro": "spereranno"
            }),
            ("cercare", "to look for", "regular_are", {
                "io": "cercherò", "tu": "cercherai", "lui_lei": "cercherà",
                "noi": "cercheremo", "voi": "cercherete", "loro": "cercheranno"
            }),
            ("pagare", "to pay", "regular_are", {
                "io": "pagherò", "tu": "pagherai", "lui_lei": "pagherà",
                "noi": "pagheremo", "voi": "pagherete", "loro": "pagheranno"
            }),

            # More regular -ERE verbs
            ("prendere", "to take", "regular_ere", {
                "io": "prenderò", "tu": "prenderai", "lui_lei": "prenderà",
                "noi": "prenderemo", "voi": "prenderete", "loro": "prenderanno"
            }),
            ("scrivere", "to write", "regular_ere", {
                "io": "scriverò", "tu": "scriverai", "lui_lei": "scriverà",
                "noi": "scriveremo", "voi": "scriverete", "loro": "scriveranno"
            }),
            ("leggere", "to read", "regular_ere", {
                "io": "leggerò", "tu": "leggerai", "lui_lei": "leggerà",
                "noi": "leggeremo", "voi": "leggerete", "loro": "leggeranno"
            }),
            ("vendere", "to sell", "regular_ere", {
                "io": "venderò", "tu": "venderai", "lui_lei": "venderà",
                "noi": "venderemo", "voi": "venderete", "loro": "venderanno"
            }),
            ("rispondere", "to answer", "regular_ere", {
                "io": "risponderò", "tu": "risponderai", "lui_lei": "risponderà",
                "noi": "risponderemo", "voi": "risponderete", "loro": "risponderanno"
            }),
            ("credere", "to believe", "regular_ere", {
                "io": "crederò", "tu": "crederai", "lui_lei": "crederà",
                "noi": "crederemo", "voi": "crederete", "loro": "crederanno"
            }),
            ("ricevere", "to receive", "regular_ere", {
                "io": "riceverò", "tu": "riceverai", "lui_lei": "riceverà",
                "noi": "riceveremo", "voi": "riceverete", "loro": "riceveranno"
            }),
            ("mettere", "to put", "regular_ere", {
                "io": "metterò", "tu": "metterai", "lui_lei": "metterà",
                "noi": "metteremo", "voi": "metterete", "loro": "metteranno"
            }),
            ("perdere", "to lose", "regular_ere", {
                "io": "perderò", "tu": "perderai", "lui_lei": "perderà",
                "noi": "perderemo", "voi": "perderete", "loro": "perderanno"
            }),
            ("conoscere", "to know", "regular_ere", {
                "io": "conoscerò", "tu": "conoscerai", "lui_lei": "conoscerà",
                "noi": "conosceremo", "voi": "conoscerete", "loro": "conosceranno"
            }),
            ("crescere", "to grow", "regular_ere", {
                "io": "crescerò", "tu": "crescerai", "lui_lei": "crescerà",
                "noi": "cresceremo", "voi": "crescerete", "loro": "cresceranno"
            }),

            # More regular -IRE verbs
            ("partire", "to leave", "regular_ire", {
                "io": "partirò", "tu": "partirai", "lui_lei": "partirà",
                "noi": "partiremo", "voi": "partirete", "loro": "partiranno"
            }),
            ("sentire", "to hear/feel", "regular_ire", {
                "io": "sentirò", "tu": "sentirai", "lui_lei": "sentirà",
                "noi": "sentiremo", "voi": "sentirete", "loro": "sentiranno"
            }),
            ("aprire", "to open", "regular_ire", {
                "io": "aprirò", "tu": "aprirai", "lui_lei": "aprirà",
                "noi": "apriremo", "voi": "aprirete", "loro": "apriranno"
            }),
            ("offrire", "to offer", "regular_ire", {
                "io": "offrirò", "tu": "offrirai", "lui_lei": "offrirà",
                "noi": "offriremo", "voi": "offrirete", "loro": "offriranno"
            }),
            ("seguire", "to follow", "regular_ire", {
                "io": "seguirò", "tu": "seguirai", "lui_lei": "seguirà",
                "noi": "seguiremo", "voi": "seguirete", "loro": "seguiranno"
            }),
            ("capire", "to understand", "regular_ire", {
                "io": "capirò", "tu": "capirai", "lui_lei": "capirà",
                "noi": "capiremo", "voi": "capirete", "loro": "capiranno"
            }),
            ("finire", "to finish", "regular_ire", {
                "io": "finirò", "tu": "finirai", "lui_lei": "finirà",
                "noi": "finiremo", "voi": "finirete", "loro": "finiranno"
            }),
            ("preferire", "to prefer", "regular_ire", {
                "io": "preferirò", "tu": "preferirai", "lui_lei": "preferirà",
                "noi": "preferiremo", "voi": "preferirete", "loro": "preferiranno"
            }),
            ("costruire", "to build", "regular_ire", {
                "io": "costruirò", "tu": "costruirai", "lui_lei": "costruirà",
                "noi": "costruiremo", "voi": "costruirete", "loro": "costruiranno"
            }),
            ("pulire", "to clean", "regular_ire", {
                "io": "pulirò", "tu": "pulirai", "lui_lei": "pulirà",
                "noi": "puliremo", "voi": "pulirete", "loro": "puliranno"
            }),

            # More irregular verbs
            ("dare", "to give", "irregular", {
                "io": "darò", "tu": "darai", "lui_lei": "darà",
                "noi": "daremo", "voi": "darete", "loro": "daranno"
            }),
            ("stare", "to stay", "irregular", {
                "io": "starò", "tu": "starai", "lui_lei": "starà",
                "noi": "staremo", "voi": "starete", "loro": "staranno"
            }),
            ("venire", "to come", "irregular", {
                "io": "verrò", "tu": "verrai", "lui_lei": "verrà",
                "noi": "verremo", "voi": "verrete", "loro": "verranno"
            }),
            ("dovere", "to have to", "irregular", {
                "io": "dovrò", "tu": "dovrai", "lui_lei": "dovrà",
                "noi": "dovremo", "voi": "dovrete", "loro": "dovranno"
            }),
            ("potere", "to be able", "irregular", {
                "io": "potrò", "tu": "potrai", "lui_lei": "potrà",
                "noi": "potremo", "voi": "potrete", "loro": "potranno"
            }),
            ("sapere", "to know", "irregular", {
                "io": "saprò", "tu": "saprai", "lui_lei": "saprà",
                "noi": "sapremo", "voi": "saprete", "loro": "sapranno"
            }),
            ("vedere", "to see", "irregular", {
                "io": "vedrò", "tu": "vedrai", "lui_lei": "vedrà",
                "noi": "vedremo", "voi": "vedrete", "loro": "vedranno"
            }),
            ("vivere", "to live", "irregular", {
                "io": "vivrò", "tu": "vivrai", "lui_lei": "vivrà",
                "noi": "vivremo", "voi": "vivrete", "loro": "vivranno"
            }),
            ("bere", "to drink", "irregular", {
                "io": "berrò", "tu": "berrai", "lui_lei": "berrà",
                "noi": "berremo", "voi": "berrete", "loro": "berranno"
            }),
            ("rimanere", "to remain", "irregular", {
                "io": "rimarrò", "tu": "rimarrai", "lui_lei": "rimarrà",
                "noi": "rimarremo", "voi": "rimarrete", "loro": "rimarranno"
            }),
            ("tenere", "to keep/hold", "irregular", {
                "io": "terrò", "tu": "terrai", "lui_lei": "terrà",
                "noi": "terremo", "voi": "terrete", "loro": "terranno"
            }),
            ("cadere", "to fall", "irregular", {
                "io": "cadrò", "tu": "cadrai", "lui_lei": "cadrà",
                "noi": "cadremo", "voi": "cadrete", "loro": "cadranno"
            }),
            ("tradurre", "to translate", "irregular", {
                "io": "tradurrò", "tu": "tradurrai", "lui_lei": "tradurrà",
                "noi": "tradurremo", "voi": "tradurrete", "loro": "tradurranno"
            }),
            ("porre", "to put/place", "irregular", {
                "io": "porrò", "tu": "porrai", "lui_lei": "porrà",
                "noi": "porremo", "voi": "porrete", "loro": "porranno"
            }),
            ("dire", "to say", "irregular", {
                "io": "dirò", "tu": "dirai", "lui_lei": "dirà",
                "noi": "diremo", "voi": "direte", "loro": "diranno"
            }),
        ]
        
        questions = []
        
        for _ in range(count):
            infinitive, english, verb_type, conjugations = random.choice(future_verbs)
            person = random.choice(["io", "tu", "lui_lei", "noi", "voi", "loro"])
            
            person_display = {
                "io": "io", "tu": "tu", "lui_lei": "lui/lei",
                "noi": "noi", "voi": "voi", "loro": "loro"
            }
            
            questions.append({
                "question": f"Futuro semplice: '{infinitive}' ({english}) for {person_display[person]}",
                "answer": conjugations[person],
                "type": "futuro_semplice",
                "infinitive": infinitive,
                "person": person
            })
        
        return questions
    
    def generate_articulated_prepositions(self, count: int = 10) -> List[Dict]:
        """Practice articulated prepositions (di+il=del, a+la=alla, etc.)."""
        
        # Sentence templates with correct articulated prepositions
        templates = [
            ("Vado ___ cinema.", "al", "di + il", "I go to the cinema"),
            ("Vengo ___ stazione.", "dalla", "da + la", "I come from the station"),
            ("Il libro è ___ tavolo.", "sul", "su + il", "The book is on the table"),
            ("Abito ___ centro.", "nel", "in + il", "I live in the center"),
            ("Parlo ___ studenti.", "degli", "di + gli", "I speak about the students"),
            ("Vado ___ bar.", "al", "a + il", "I go to the bar"),
            ("Torno ___ ufficio.", "dall'", "da + l'", "I return from the office"),
            ("Il gatto è ___ sedia.", "sulla", "su + la", "The cat is on the chair"),
            ("Abito ___ montagna.", "in", "in + (no article)", "I live in the mountains"),
            ("Sono ___ parco.", "nel", "in + il", "I am in the park"),
            ("Vengo ___ mare.", "dal", "da + il", "I come from the sea"),
            ("Vado ___ scuola.", "alla", "a + la", "I go to school"),
            ("Il libro ___ studente.", "dello", "di + lo", "The student's book"),
            ("Parlo ___ amici.", "degli", "di + gli", "I talk about the friends"),
            ("Vado ___ negozi.", "ai", "a + i", "I go to the shops"),
            ("Torno ___ città.", "dalla", "da + la", "I return from the city"),
            ("Sono ___ giardino.", "nel", "in + il", "I am in the garden"),
            ("Il telefono è ___ borsa.", "nella", "in + la", "The phone is in the bag"),
            ("Vengo ___ università.", "dall'", "da + l'", "I come from the university"),
            ("Vado ___ spiaggia.", "alla", "a + la", "I go to the beach"),
        ]
        
        questions = []
        selected = random.sample(templates, min(count, len(templates)))
        
        for sentence, answer, prep_combo, english in selected:
            questions.append({
                "question": f"Fill in: {sentence}\n(English: {english})\n(Hint: {prep_combo})",
                "answer": answer,
                "type": "articulated_prep",
                "full_sentence": sentence.replace("___", answer)
            })
        
        return questions
    
    def generate_reflexive_verbs(self, count: int = 10) -> List[Dict]:
        """Practice reflexive verb conjugations."""
        
        # Common reflexive verbs with their conjugations
        reflexive_verbs = [
            ("alzarsi", "to get up", {
                "io": "mi alzo", "tu": "ti alzi", "lui_lei": "si alza",
                "noi": "ci alziamo", "voi": "vi alzate", "loro": "si alzano"
            }),
            ("svegliarsi", "to wake up", {
                "io": "mi sveglio", "tu": "ti svegli", "lui_lei": "si sveglia",
                "noi": "ci svegliamo", "voi": "vi svegliate", "loro": "si svegliano"
            }),
            ("lavarsi", "to wash oneself", {
                "io": "mi lavo", "tu": "ti lavi", "lui_lei": "si lava",
                "noi": "ci laviamo", "voi": "vi lavate", "loro": "si lavano"
            }),
            ("vestirsi", "to get dressed", {
                "io": "mi vesto", "tu": "ti vesti", "lui_lei": "si veste",
                "noi": "ci vestiamo", "voi": "vi vestite", "loro": "si vestono"
            }),
            ("chiamarsi", "to be called", {
                "io": "mi chiamo", "tu": "ti chiami", "lui_lei": "si chiama",
                "noi": "ci chiamiamo", "voi": "vi chiamate", "loro": "si chiamano"
            }),
            ("sentirsi", "to feel", {
                "io": "mi sento", "tu": "ti senti", "lui_lei": "si sente",
                "noi": "ci sentiamo", "voi": "vi sentite", "loro": "si sentono"
            }),
            ("divertirsi", "to have fun", {
                "io": "mi diverto", "tu": "ti diverti", "lui_lei": "si diverte",
                "noi": "ci divertiamo", "voi": "vi divertite", "loro": "si divertono"
            }),
            ("riposarsi", "to rest", {
                "io": "mi riposo", "tu": "ti riposi", "lui_lei": "si riposa",
                "noi": "ci riposiamo", "voi": "vi riposate", "loro": "si riposano"
            }),
            ("prepararsi", "to get ready", {
                "io": "mi preparo", "tu": "ti prepari", "lui_lei": "si prepara",
                "noi": "ci prepariamo", "voi": "vi preparate", "loro": "si preparano"
            }),
            ("fermarsi", "to stop", {
                "io": "mi fermo", "tu": "ti fermi", "lui_lei": "si ferma",
                "noi": "ci fermiamo", "voi": "vi fermate", "loro": "si fermano"
            }),
            ("sposarsi", "to get married", {
                "io": "mi sposo", "tu": "ti sposi", "lui_lei": "si sposa",
                "noi": "ci sposiamo", "voi": "vi sposate", "loro": "si sposano"
            }),
            ("annoiarsi", "to get bored", {
                "io": "mi annoio", "tu": "ti annoi", "lui_lei": "si annoia",
                "noi": "ci annoiamo", "voi": "vi annoiate", "loro": "si annoiano"
            }),
        ]
        
        questions = []
        
        for _ in range(count):
            infinitive, english, conjugations = random.choice(reflexive_verbs)
            person = random.choice(["io", "tu", "lui_lei", "noi", "voi", "loro"])
            
            person_display = {
                "io": "io", "tu": "tu", "lui_lei": "lui/lei",
                "noi": "noi", "voi": "voi", "loro": "loro"
            }
            
            questions.append({
                "question": f"Conjugate reflexive: '{infinitive}' ({english}) for {person_display[person]}",
                "answer": conjugations[person],
                "type": "reflexive_verb",
                "infinitive": infinitive,
                "person": person
            })
        
        return questions
    
    def generate_time_prepositions(self, count: int = 10) -> List[Dict]:
        """Practice time prepositions: per, da, a, fa."""
        
        # Sentence templates with correct time prepositions
        # per = for a set period (not continuing)
        # da = since (from a time, continuing)
        # a = at (point in time/age)
        # fa = ago (time that has passed)
        templates = [
            # PER - duration that's finished
            ("Ho studiato italiano ___ tre anni.", "per", "per (finished duration)", "I studied Italian for three years"),
            ("Sono rimasto a Roma ___ una settimana.", "per", "per (finished duration)", "I stayed in Rome for a week"),
            ("Ho lavorato lì ___ due mesi.", "per", "per (finished duration)", "I worked there for two months"),
            ("Abbiamo vissuto a Milano ___ cinque anni.", "per", "per (finished duration)", "We lived in Milan for five years"),
            ("Ho aspettato ___ un'ora.", "per", "per (finished duration)", "I waited for an hour"),
            
            # DA - since, from (continuing)
            ("Studio italiano ___ due anni.", "da", "da (since, continuing)", "I've been studying Italian for two years"),
            ("Non vedo Maria ___ lunedì.", "da", "da (since)", "I haven't seen Maria since Monday"),
            ("Abito qui ___ gennaio.", "da", "da (since)", "I've lived here since January"),
            ("Lavoro in questa azienda ___ tre mesi.", "da", "da (since, continuing)", "I've been working at this company for three months"),
            ("Non mangio carne ___ anni.", "da", "da (since, continuing)", "I haven't eaten meat for years"),
            ("Aspetto ___ ore!", "da", "da (since, continuing)", "I've been waiting for hours!"),
            
            # A - at (age, point in time)
            ("Ho finito la scuola ___ 18 anni.", "a", "a (at an age)", "I finished school at 18"),
            ("Sono arrivato ___ mezzanotte.", "a", "a (at a time)", "I arrived at midnight"),
            ("Mi sono sposata ___ 25 anni.", "a", "a (at an age)", "I got married at 25"),
            ("Il film comincia ___ otto.", "a", "a (at a time)", "The movie starts at eight"),
            ("Ci vediamo ___ pranzo.", "a", "a (at a meal time)", "See you at lunch"),
            
            # FA - ago
            ("Sono arrivato tre giorni ___.", "fa", "fa (ago)", "I arrived three days ago"),
            ("Ho visto Maria una settimana ___.", "fa", "fa (ago)", "I saw Maria a week ago"),
            ("Siamo partiti due ore ___.", "fa", "fa (ago)", "We left two hours ago"),
            ("L'ho comprato un mese ___.", "fa", "fa (ago)", "I bought it a month ago"),
            ("Sono stato a Roma anni ___.", "fa", "fa (ago)", "I was in Rome years ago"),
            ("Ho mangiato dieci minuti ___.", "fa", "fa (ago)", "I ate ten minutes ago"),
        ]
        
        questions = []
        selected = random.sample(templates, min(count, len(templates)))
        
        for sentence, answer, explanation, english in selected:
            questions.append({
                "question": f"Fill in the time preposition: {sentence}\n(English: {english})",
                "answer": answer,
                "explanation": explanation,
                "type": "time_preposition",
                "full_sentence": sentence.replace("___", answer)
            })
        
        return questions
    
    def generate_negation_practice(self, count: int = 10) -> List[Dict]:
        """Practice Italian negations: non...mai, non...più, non...niente/nulla, non...nessuno, etc."""
        
        # Practice templates for different negation patterns
        templates = [
            # NON...MAI (never)
            ("transform", "Vado sempre al cinema.", "Non vado mai al cinema.", "always → never"),
            ("transform", "Maria studia sempre.", "Maria non studia mai.", "always → never"),
            ("transform", "Mangio sempre la pasta.", "Non mangio mai la pasta.", "always → never"),
            ("fill", "Non ___ visto questo film.", "ho mai", "I've never seen this film"),
            ("fill", "Non ___ stato in Italia.", "sono mai", "I've never been to Italy"),
            
            # NON...PIÙ (not anymore, no longer)
            ("transform", "Lavoro ancora qui.", "Non lavoro più qui.", "still → not anymore"),
            ("transform", "Abito ancora a Roma.", "Non abito più a Roma.", "still → not anymore"),
            ("fill", "Non fumo ___.", "più", "I don't smoke anymore"),
            ("fill", "Non studio ___ l'italiano.", "più", "I no longer study Italian"),
            
            # NON...NIENTE/NULLA (nothing)
            ("transform", "Ho visto tutto.", "Non ho visto niente.", "everything → nothing"),
            ("transform", "Capisco tutto.", "Non capisco niente.", "everything → nothing"),
            ("fill", "Non ho ___ da fare.", "niente", "I have nothing to do"),
            ("fill", "Non c'è ___ nel frigo.", "niente", "There's nothing in the fridge"),
            
            # NON...NESSUNO (nobody, no one)
            ("fill", "Non conosco ___.", "nessuno", "I don't know anyone"),
            ("fill", "Non c'è ___ a casa.", "nessuno", "There's no one at home"),
            ("transform", "C'è qualcuno?", "Non c'è nessuno.", "someone → no one"),
            
            # NON...NEANCHE/NEMMENO/NEPPURE (not even)
            ("fill", "Non ho ___ un euro.", "neanche", "I don't even have one euro"),
            ("fill", "Non parlo ___ italiano.", "neanche", "I don't even speak Italian"),
            
            # MIXED DOUBLE NEGATIVES
            ("fill", "Non ho ___ parlato con lei.", "mai", "I've never spoken with her"),
            ("fill", "Non voglio ___ bere.", "più", "I don't want to drink anymore"),
            ("fill", "Non dice ___ a nessuno.", "niente", "He doesn't say anything to anyone"),
            ("transform", "Vado ancora in palestra.", "Non vado più in palestra.", "still → not anymore"),
            ("transform", "Ho fatto tutto.", "Non ho fatto niente.", "everything → nothing"),
        ]
        
        questions = []
        selected = random.sample(templates, min(count, len(templates)))
        
        for q_type, prompt, answer, hint in selected:
            if q_type == "transform":
                question_text = f"Make this sentence negative:\n'{prompt}'"
                explanation = f"Transform: {hint}"
            else:  # fill
                question_text = f"Fill in the negation: {prompt}\n(English: {hint})"
                explanation = f"Pattern: non + verb + {answer}"
            
            questions.append({
                "question": question_text,
                "answer": answer,
                "explanation": explanation,
                "type": "negation"
            })
        
        return questions


    def generate_sentence_translation(self, level: str = "A1", count: int = 10,
                                       direction: str = "it_to_en") -> List[Dict]:
        """Generate sentence translation practice.

        Args:
            level: Language level (A1, A2)
            count: Number of questions
            direction: 'it_to_en' (Italian to English) or 'en_to_it' (English to Italian)
        """

        # Common sentence patterns for each level
        sentences_a1 = [
            ("Mi chiamo Marco.", "My name is Marco.", "introductions"),
            ("Ho ventisette anni.", "I am 27 years old.", "age"),
            ("Sono di Roma.", "I am from Rome.", "origin"),
            ("Abito a Milano.", "I live in Milan.", "location"),
            ("Parlo italiano e inglese.", "I speak Italian and English.", "languages"),
            ("Studio all'università.", "I study at university.", "studies"),
            ("Lavoro in un ufficio.", "I work in an office.", "work"),
            ("Mi piace il caffè.", "I like coffee.", "preferences"),
            ("Non mi piace il tè.", "I don't like tea.", "preferences"),
            ("Vado al cinema.", "I go to the cinema.", "activities"),
            ("Mangio la pasta.", "I eat pasta.", "food"),
            ("Bevo un bicchiere d'acqua.", "I drink a glass of water.", "drinks"),
            ("Leggo un libro.", "I read a book.", "activities"),
            ("Guardo la televisione.", "I watch television.", "activities"),
            ("Ascolto la musica.", "I listen to music.", "activities"),
            ("Cammino nel parco.", "I walk in the park.", "activities"),
            ("Prendo l'autobus.", "I take the bus.", "transport"),
            ("Vado a casa.", "I go home.", "movement"),
            ("Sono stanco.", "I am tired.", "feelings"),
            ("Ho fame.", "I am hungry.", "feelings"),
            ("Ho sete.", "I am thirsty.", "feelings"),
            ("Fa caldo oggi.", "It's hot today.", "weather"),
            ("Fa freddo.", "It's cold.", "weather"),
            ("È una bella giornata.", "It's a beautiful day.", "weather"),
            ("Che ore sono?", "What time is it?", "time"),
            ("Sono le tre.", "It's three o'clock.", "time"),
            ("Buongiorno!", "Good morning!", "greetings"),
            ("Come stai?", "How are you?", "greetings"),
            ("Sto bene, grazie.", "I'm fine, thank you.", "greetings"),
            ("Dove abiti?", "Where do you live?", "questions"),
        ]

        sentences_a2 = [
            ("Ieri sono andato al mare.", "Yesterday I went to the beach.", "past_activities"),
            ("Ho mangiato la pizza.", "I ate pizza.", "past_activities"),
            ("Sono stato a Firenze.", "I was in Florence.", "past_travel"),
            ("Ho visto un film interessante.", "I saw an interesting film.", "past_activities"),
            ("Domani andrò in centro.", "Tomorrow I will go downtown.", "future_plans"),
            ("Il prossimo anno studierò francese.", "Next year I will study French.", "future_plans"),
            ("Quando ero piccolo abitavo a Napoli.", "When I was little I lived in Naples.", "past_habitual"),
            ("Mi sono svegliato alle sette.", "I woke up at seven.", "reflexive_past"),
            ("Mi diverto con i miei amici.", "I have fun with my friends.", "reflexive_present"),
            ("Vado spesso al ristorante.", "I often go to the restaurant.", "frequency"),
            ("Non vado mai in palestra.", "I never go to the gym.", "negation"),
            ("Non lavoro più in quella azienda.", "I don't work at that company anymore.", "negation"),
            ("Studio italiano da due anni.", "I've been studying Italian for two years.", "time_prepositions"),
            ("Ho studiato per tre ore.", "I studied for three hours.", "time_prepositions"),
            ("Sono arrivato a casa alle otto.", "I arrived home at eight.", "time_prepositions"),
            ("L'ho visto tre giorni fa.", "I saw him three days ago.", "time_prepositions"),
            ("Vorrei un caffè, per favore.", "I would like a coffee, please.", "polite_requests"),
            ("Potrei avere il conto?", "Could I have the bill?", "polite_requests"),
            ("Mi piacerebbe visitare Venezia.", "I would like to visit Venice.", "conditional"),
            ("Se avessi tempo, viaggerei di più.", "If I had time, I would travel more.", "conditional"),
            ("Penso che sia una buona idea.", "I think it's a good idea.", "subjunctive"),
            ("Credo che abbia ragione.", "I believe he/she has reason / I believe he/she is right.", "subjunctive"),
            ("Prima di uscire, mi vesto.", "Before going out, I get dressed.", "before_after"),
            ("Dopo aver mangiato, vado a dormire.", "After eating, I go to sleep.", "before_after"),
            ("Mentre studiavo, ascoltavo musica.", "While I was studying, I listened to music.", "simultaneous"),
            ("Quando sono arrivato, pioveva.", "When I arrived, it was raining.", "simultaneous"),
            ("Devo finire questo lavoro.", "I must finish this work.", "obligation"),
            ("Posso aiutarti?", "Can I help you?", "ability"),
            ("Voglio imparare l'italiano.", "I want to learn Italian.", "desire"),
            ("Non capisco questa parola.", "I don't understand this word.", "comprehension"),
        ]

        # Select sentences based on level
        sentence_pool = sentences_a1 if level == "A1" else sentences_a2

        # Randomly select sentences
        selected = random.sample(sentence_pool, min(count, len(sentence_pool)))

        questions = []
        for italian, english, category in selected:
            if direction == "it_to_en":
                question_text = f"Translate to English: {italian}"
                answer = english
            else:
                question_text = f"Translate to Italian: {english}"
                answer = italian

            questions.append({
                "question": question_text,
                "answer": answer,
                "italian": italian,
                "english": english,
                "category": category,
                "type": "sentence_translation"
            })

        return questions

    def generate_regular_passato_prossimo(self, count: int = 10) -> List[Dict]:
        """Generate regular passato prossimo conjugation practice.

        Only tests regular -are, -ere, -ire verbs in passato prossimo.
        Good for A1/A2 levels.
        """
        regular_verbs = [
            ("parlare", "to speak", "avere"),
            ("mangiare", "to eat", "avere"),
            ("studiare", "to study", "avere"),
            ("lavorare", "to work", "avere"),
            ("comprare", "to buy", "avere"),
            ("guardare", "to watch", "avere"),
            ("ascoltare", "to listen", "avere"),
            ("camminare", "to walk", "avere"),
            ("arrivare", "to arrive", "essere"),
            ("andare", "to go", "essere"),  # Irregular but common
            ("vendere", "to sell", "avere"),
            ("credere", "to believe", "avere"),
            ("ricevere", "to receive", "avere"),
            ("dormire", "to sleep", "avere"),
            ("partire", "to leave", "essere"),
            ("finire", "to finish", "avere"),
            ("capire", "to understand", "avere"),
            ("preferire", "to prefer", "avere"),
        ]

        subjects = ["io", "tu", "lui/lei", "noi", "voi", "loro"]

        # Regular past participles
        def get_participle(infinitive):
            if infinitive == "andare":
                return "andato"  # Base form, will be modified for agreement
            if infinitive.endswith("are"):
                return infinitive[:-3] + "ato"
            elif infinitive.endswith("ere"):
                return infinitive[:-3] + "uto"
            elif infinitive == "finire" or infinitive == "capire" or infinitive == "preferire":
                return infinitive[:-3] + "ito"
            elif infinitive.endswith("ire"):
                return infinitive[:-3] + "ito"
            return infinitive

        # Add agreement for essere verbs
        def apply_agreement(participle, aux, subject):
            if aux == "avere":
                return participle  # No agreement with avere
            # Agreement with essere - modify participle ending
            if subject == "io" or subject == "tu":
                return participle + "/a"  # Could be either gender
            elif subject == "lui/lei":
                return participle + "/a"  # Could be either gender
            elif subject == "noi":
                return participle[:-1] + "i/e"  # plural
            elif subject == "voi":
                return participle[:-1] + "i/e"  # plural
            elif subject == "loro":
                return participle[:-1] + "i/e"  # plural
            return participle

        # Conjugate auxiliary
        def conjugate_aux(aux, subject):
            if aux == "avere":
                conj = {"io": "ho", "tu": "hai", "lui/lei": "ha",
                       "noi": "abbiamo", "voi": "avete", "loro": "hanno"}
            else:  # essere
                conj = {"io": "sono", "tu": "sei", "lui/lei": "è",
                       "noi": "siamo", "voi": "siete", "loro": "sono"}
            return conj.get(subject, "")

        questions = []
        import random

        for _ in range(count):
            verb, meaning, aux = random.choice(regular_verbs)
            subject = random.choice(subjects)
            participle = get_participle(verb)
            participle = apply_agreement(participle, aux, subject)

            auxiliary_conjugated = conjugate_aux(aux, subject)
            answer = f"{auxiliary_conjugated} {participle}"

            questions.append({
                "question": f"Conjugate '{verb}' ({meaning}) in passato prossimo for '{subject}'",
                "answer": answer,
                "type": "text_input",
                "hint": f"Use {aux} + past participle"
            })

        return questions

    def generate_imperfect_tense(self, count: int = 10) -> List[Dict]:
        """Generate imperfect tense (imperfetto) conjugation practice.

        Good for A2/B1 levels for describing past habits and ongoing actions.
        """
        regular_verbs = [
            ("parlare", "to speak"),
            ("mangiare", "to eat"),
            ("studiare", "to study"),
            ("lavorare", "to work"),
            ("guardare", "to watch"),
            ("vendere", "to sell"),
            ("credere", "to believe"),
            ("leggere", "to read"),
            ("dormire", "to sleep"),
            ("partire", "to leave"),
            ("finire", "to finish"),
            ("capire", "to understand"),
        ]

        # Common irregular verbs in imperfetto
        irregular_verbs = [
            ("essere", "to be"),
            ("fare", "to do/make"),
            ("dire", "to say"),
            ("bere", "to drink"),
        ]

        all_verbs = regular_verbs + irregular_verbs
        subjects = ["io", "tu", "lui/lei", "noi", "voi", "loro"]

        def conjugate_imperfect(infinitive, subject):
            # Irregular verbs
            if infinitive == "essere":
                conj = {"io": "ero", "tu": "eri", "lui/lei": "era",
                       "noi": "eravamo", "voi": "eravate", "loro": "erano"}
                return conj.get(subject, "")
            elif infinitive == "fare":
                stem = "face"
            elif infinitive == "dire":
                stem = "dice"
            elif infinitive == "bere":
                stem = "beve"
            # Regular verbs
            elif infinitive.endswith("are"):
                stem = infinitive[:-3]
                endings = {"io": "avo", "tu": "avi", "lui/lei": "ava",
                          "noi": "avamo", "voi": "avate", "loro": "avano"}
                return stem + endings.get(subject, "")
            elif infinitive.endswith("ere"):
                stem = infinitive[:-3]
                endings = {"io": "evo", "tu": "evi", "lui/lei": "eva",
                          "noi": "evamo", "voi": "evate", "loro": "evano"}
                return stem + endings.get(subject, "")
            elif infinitive.endswith("ire"):
                stem = infinitive[:-3]
                endings = {"io": "ivo", "tu": "ivi", "lui/lei": "iva",
                          "noi": "ivamo", "voi": "ivate", "loro": "ivano"}
                return stem + endings.get(subject, "")

            # For irregular stems
            if infinitive in ["fare", "dire", "bere"]:
                endings = {"io": "vo", "tu": "vi", "lui/lei": "va",
                          "noi": "vamo", "voi": "vate", "loro": "vano"}
                return stem + endings.get(subject, "")

            return ""

        questions = []
        import random

        for _ in range(count):
            verb, meaning = random.choice(all_verbs)
            subject = random.choice(subjects)
            answer = conjugate_imperfect(verb, subject)

            questions.append({
                "question": f"Conjugate '{verb}' ({meaning}) in imperfetto for '{subject}'",
                "answer": answer,
                "type": "text_input",
                "hint": "Imperfect tense describes past habits and ongoing actions"
            })

        return questions

    def generate_noun_gender_number(self, count: int = 10) -> List[Dict]:
        """Generate noun gender and number identification practice.

        Users must identify if a noun is:
        - Masculine Singular (MS)
        - Feminine Singular (FS)
        - Masculine Plural (MP)
        - Feminine Plural (FP)

        Shows special rules for exceptions (accents, -ma endings, foreign words, etc.)
        Good for A1/A2 levels.
        """
        import random

        # Nouns with their properties and any special rules
        nouns = [
            # Regular masculine singular (-o)
            ("libro", "MS", "libro", "Regular: ends in -o"),
            ("tavolo", "MS", "table", "Regular: ends in -o"),
            ("gatto", "MS", "cat", "Regular: ends in -o"),
            ("amico", "MS", "friend", "Regular: ends in -o"),
            ("ragazzo", "MS", "boy", "Regular: ends in -o"),
            ("anno", "MS", "year", "Regular: ends in -o"),
            ("gelato", "MS", "ice cream", "Regular: ends in -o"),
            ("vino", "MS", "wine", "Regular: ends in -o"),

            # Regular feminine singular (-a)
            ("casa", "FS", "house", "Regular: ends in -a"),
            ("ragazza", "FS", "girl", "Regular: ends in -a"),
            ("pizza", "FS", "pizza", "Regular: ends in -a"),
            ("strada", "FS", "street", "Regular: ends in -a"),
            ("acqua", "FS", "water", "Regular: ends in -a"),
            ("macchina", "FS", "car", "Regular: ends in -a"),
            ("scuola", "FS", "school", "Regular: ends in -a"),
            ("porta", "FS", "door", "Regular: ends in -a"),

            # Regular masculine plural (-i)
            ("libri", "MP", "books", "Regular: plural of -o → -i"),
            ("gatti", "MP", "cats", "Regular: plural of -o → -i"),
            ("amici", "MP", "friends", "Regular: plural of -o → -i"),
            ("ragazzi", "MP", "boys", "Regular: plural of -o → -i"),
            ("anni", "MP", "years", "Regular: plural of -o → -i"),

            # Regular feminine plural (-e)
            ("case", "FP", "houses", "Regular: plural of -a → -e"),
            ("ragazze", "FP", "girls", "Regular: plural of -a → -e"),
            ("pizze", "FP", "pizzas", "Regular: plural of -a → -e"),
            ("strade", "FP", "streets", "Regular: plural of -a → -e"),
            ("porte", "FP", "doors", "Regular: plural of -a → -e"),

            # Masculine -e singular
            ("padre", "MS", "father", "Masculine noun ending in -e"),
            ("mare", "MS", "sea", "Masculine noun ending in -e"),
            ("pane", "MS", "bread", "Masculine noun ending in -e"),
            ("cane", "MS", "dog", "Masculine noun ending in -e"),
            ("pesce", "MS", "fish", "Masculine noun ending in -e"),

            # Feminine -e singular
            ("madre", "FS", "mother", "Feminine noun ending in -e"),
            ("chiave", "FS", "key", "Feminine noun ending in -e"),
            ("notte", "FS", "night", "Feminine noun ending in -e"),
            ("classe", "FS", "class", "Feminine noun ending in -e"),

            # -e plural (both genders → -i)
            ("padri", "MP", "fathers", "Plural of -e → -i (masculine)"),
            ("madri", "FP", "mothers", "Plural of -e → -i (feminine)"),
            ("chiavi", "FP", "keys", "Plural of -e → -i (feminine)"),
            ("cani", "MP", "dogs", "Plural of -e → -i (masculine)"),

            # Special: -ma words (masculine despite -a)
            ("problema", "MS", "problem", "EXCEPTION: -ma ending = masculine (Greek origin)"),
            ("programma", "MS", "program", "EXCEPTION: -ma ending = masculine (Greek origin)"),
            ("sistema", "MS", "system", "EXCEPTION: -ma ending = masculine (Greek origin)"),
            ("tema", "MS", "theme/topic", "EXCEPTION: -ma ending = masculine (Greek origin)"),
            ("cinema", "MS", "cinema", "EXCEPTION: -ma ending = masculine (Greek origin)"),

            # Special: accented words (invariable)
            ("città", "FS", "city", "EXCEPTION: Ends in accent = no plural form (invariable)"),
            ("caffè", "MS", "coffee", "EXCEPTION: Ends in accent = no plural form (invariable)"),
            ("università", "FS", "university", "EXCEPTION: Ends in accent = no plural form (invariable)"),

            # Special: foreign words (invariable)
            ("sport", "MS", "sport", "EXCEPTION: Foreign word = no plural form (invariable)"),
            ("computer", "MS", "computer", "EXCEPTION: Foreign word = no plural form (invariable)"),
            ("film", "MS", "film/movie", "EXCEPTION: Foreign word = no plural form (invariable)"),
            ("bar", "MS", "bar/café", "EXCEPTION: Foreign word = no plural form (invariable)"),

            # Special: -ista words (changes article, not ending)
            ("artista", "MS", "artist (male)", "Can be masculine or feminine (il/la artista)"),
            ("artista", "FS", "artist (female)", "Can be masculine or feminine (il/la artista)"),

            # Special: hand/hands (irregular)
            ("mano", "FS", "hand", "EXCEPTION: Ends in -o but is FEMININE"),
            ("mani", "FP", "hands", "EXCEPTION: Feminine despite -o ending"),
        ]

        questions = []

        # Create the choices
        choices = [
            "Masculine Singular (MS)",
            "Feminine Singular (FS)",
            "Masculine Plural (MP)",
            "Feminine Plural (FP)"
        ]

        for _ in range(count):
            noun_word, gender_number, meaning, rule = random.choice(nouns)

            # Map to full answer
            answer_map = {
                "MS": "Masculine Singular (MS)",
                "FS": "Feminine Singular (FS)",
                "MP": "Masculine Plural (MP)",
                "FP": "Feminine Plural (FP)"
            }

            correct_answer = answer_map[gender_number]

            # Determine if this is an exception
            is_exception = "EXCEPTION" in rule or "Greek" in rule

            hint = f"{meaning} - {rule}" if is_exception else f"{meaning}"

            questions.append({
                "question": f"What is the gender and number of: {noun_word}?",
                "answer": correct_answer,
                "type": "multiple_choice",
                "choices": choices,
                "hint": hint,
                "explanation": rule
            })

        return questions

    def generate_pronouns_practice(self, count: int = 10) -> List[Dict]:
        """Practice direct and indirect object pronouns.

        Direct pronouns: mi, ti, lo/la, ci, vi, li/le (me, you, him/her/it, us, you, them)
        Indirect pronouns: mi, ti, gli/le, ci, vi, gli (to me, to you, to him/her, to us, to you, to them)
        """
        import random

        templates = [
            # Direct object pronouns
            ("Vedo Maria ogni giorno. ___ vedo ogni giorno.", "La", "Direct object pronoun - her", "I see Maria every day. I see HER every day."),
            ("Compro il pane al supermercato. ___ compro al supermercato.", "Lo", "Direct object pronoun - it", "I buy bread at the supermarket. I buy IT there."),
            ("Chiamo i miei amici. ___ chiamo spesso.", "Li", "Direct object pronoun - them (masc.)", "I call my friends. I call THEM often."),
            ("Incontro le ragazze al bar. ___ incontro ogni sabato.", "Le", "Direct object pronoun - them (fem.)", "I meet the girls at the bar. I meet THEM every Saturday."),
            ("Conosco te e tuo fratello. ___ conosco bene.", "Vi", "Direct object pronoun - you (pl.)", "I know you and your brother. I know YOU (plural) well."),
            ("Aspetto mia sorella. ___ aspetto qui.", "La", "Direct object pronoun - her", "I'm waiting for my sister. I'm waiting for HER here."),
            ("Leggo i libri italiani. ___ leggo volentieri.", "Li", "Direct object pronoun - them (masc.)", "I read Italian books. I read THEM willingly."),
            ("Guardo la TV. ___ guardo ogni sera.", "La", "Direct object pronoun - it (fem.)", "I watch TV. I watch IT every evening."),
            ("Mangio le mele. ___ mangio sempre.", "Le", "Direct object pronoun - them (fem.)", "I eat apples. I always eat THEM."),
            ("Porto il computer. ___ porto sempre con me.", "Lo", "Direct object pronoun - it (masc.)", "I carry the computer. I always carry IT with me."),

            # Indirect object pronouns
            ("Parlo a Maria. ___ parlo ogni giorno.", "Le", "Indirect object pronoun - to her", "I speak to Maria. I speak TO HER every day."),
            ("Scrivo a mio padre. ___ scrivo spesso.", "Gli", "Indirect object pronoun - to him", "I write to my father. I write TO HIM often."),
            ("Telefono ai miei amici. ___ telefono la sera.", "Gli", "Indirect object pronoun - to them", "I call my friends. I call THEM in the evening."),
            ("Do il libro a te. ___ do il libro.", "Ti", "Indirect object pronoun - to you", "I give the book to you. I give the book TO YOU."),
            ("Mando un messaggio a voi. ___ mando un messaggio.", "Vi", "Indirect object pronoun - to you (pl.)", "I send a message to you. I send a message TO YOU (plural)."),
            ("Compro un regalo per mia madre. ___ compro un regalo.", "Le", "Indirect object pronoun - to/for her", "I buy a gift for my mother. I buy HER a gift."),
            ("Racconti la storia a me. ___ racconti la storia.", "Mi", "Indirect object pronoun - to me", "You tell the story to me. You tell ME the story."),
            ("Spiego la lezione agli studenti. ___ spiego la lezione.", "Gli", "Indirect object pronoun - to them", "I explain the lesson to the students. I explain the lesson TO THEM."),
            ("Chiedo un favore a te. ___ chiedo un favore.", "Ti", "Indirect object pronoun - to you", "I ask you a favor. I ask YOU a favor."),
            ("Offro un caffè a noi. ___ offre un caffè.", "Ci", "Indirect object pronoun - to us", "He/she offers us a coffee. He/she offers US a coffee."),

            # Mixed practice
            ("Vedo Maria e Marco. ___ vedo domani.", "Li", "Direct pronoun - them (mixed gender uses masc. plural)", "I see Maria and Marco. I see THEM tomorrow."),
            ("Parlo a mia sorella. ___ parlo spesso.", "Le", "Indirect object pronoun - to her", "I speak to my sister. I speak TO HER often."),
            ("Compro le scarpe. ___ compro in Italia.", "Le", "Direct object pronoun - them (fem.)", "I buy shoes. I buy THEM in Italy."),
            ("Do il passaporto all'agente. ___ do il passaporto.", "Gli", "Indirect object pronoun - to him/her", "I give the passport to the agent. I give HIM/HER the passport."),
            ("Aspetto mio padre. ___ aspetto alla stazione.", "Lo", "Direct object pronoun - him", "I'm waiting for my father. I'm waiting for HIM at the station."),
        ]

        # Randomly select templates
        selected = random.sample(templates, min(count, len(templates)))

        questions = []
        for sentence, correct, explanation, english in selected:
            # Generate choices based on the correct answer
            if correct in ["Lo", "La", "Li", "Le"]:
                # Direct pronouns
                all_choices = ["Lo", "La", "Li", "Le", "Mi", "Ti", "Ci", "Vi"]
            else:
                # Indirect pronouns
                all_choices = ["Mi", "Ti", "Gli", "Le", "Ci", "Vi"]

            # Always include the correct answer
            choices = [correct]
            # Add 3 more random choices
            remaining = [c for c in all_choices if c != correct]
            choices.extend(random.sample(remaining, min(3, len(remaining))))
            random.shuffle(choices)

            questions.append({
                "question": sentence,
                "answer": correct,
                "type": "multiple_choice",
                "choices": choices,
                "hint": english,
                "explanation": explanation
            })

        return questions

    def generate_adverbs_practice(self, count: int = 10) -> List[Dict]:
        """Practice Italian adverbs - frequency, manner, time, and place.

        Common adverb types at A1 level:
        - Frequency: sempre, mai, spesso, raramente, qualche volta
        - Manner: bene, male, piano, forte, velocemente, lentamente
        - Time: ora, adesso, oggi, ieri, domani, presto, tardi
        - Place: qui, lì, là, vicino, lontano, sopra, sotto
        """
        import random

        templates = [
            # Frequency adverbs
            ("Vado ___ al cinema il sabato.", "sempre", "Frequency adverb - always", "I always go to the cinema on Saturday."),
            ("Non mangio ___ la carne.", "mai", "Frequency adverb - never", "I never eat meat."),
            ("Vedo ___ Maria al bar.", "spesso", "Frequency adverb - often", "I often see Maria at the bar."),
            ("Vado ___ al ristorante.", "raramente", "Frequency adverb - rarely", "I rarely go to the restaurant."),
            ("Leggo ___ un libro.", "qualche volta", "Frequency adverb - sometimes", "Sometimes I read a book."),
            ("Studio ___ italiano.", "sempre", "Frequency adverb - always", "I always study Italian."),
            ("___ dimentico le chiavi.", "spesso", "Frequency adverb - often", "I often forget the keys."),

            # Manner adverbs
            ("Parlo italiano molto ___.", "bene", "Manner adverb - well", "I speak Italian very well."),
            ("Canto molto ___.", "male", "Manner adverb - badly", "I sing very badly."),
            ("Parla ___!", "piano", "Manner adverb - quietly/slowly", "Speak quietly/slowly!"),
            ("La musica è troppo ___.", "forte", "Manner adverb - loud", "The music is too loud."),
            ("Corro ___.", "velocemente", "Manner adverb - quickly", "I run quickly."),
            ("Cammino ___.", "lentamente", "Manner adverb - slowly", "I walk slowly."),
            ("Lavoro molto ___.", "bene", "Manner adverb - well", "I work very well."),

            # Time adverbs
            ("Vado al supermercato ___.", "adesso", "Time adverb - now", "I'm going to the supermarket now."),
            ("Sono stanco ___.", "oggi", "Time adverb - today", "I'm tired today."),
            ("___ ho visto Maria.", "ieri", "Time adverb - yesterday", "Yesterday I saw Maria."),
            ("Parto ___.", "domani", "Time adverb - tomorrow", "I'm leaving tomorrow."),
            ("Mi sveglio ___.", "presto", "Time adverb - early", "I wake up early."),
            ("Arrivo sempre ___.", "tardi", "Time adverb - late", "I always arrive late."),
            ("Devo andare ___.", "ora", "Time adverb - now", "I have to go now."),

            # Place adverbs
            ("Il libro è ___.", "qui", "Place adverb - here", "The book is here."),
            ("Maria abita ___.", "lì", "Place adverb - there", "Maria lives there."),
            ("La stazione è ___.", "vicino", "Place adverb - near", "The station is near."),
            ("Il mare è ___.", "lontano", "Place adverb - far", "The sea is far."),
            ("Il gatto è ___ il tavolo.", "sopra", "Place adverb - above/on", "The cat is on the table."),
            ("Il cane dorme ___ il letto.", "sotto", "Place adverb - under", "The dog sleeps under the bed."),
            ("Vieni ___!", "qui", "Place adverb - here", "Come here!"),

            # Mixed practice
            ("Studio ___ la sera.", "sempre", "Frequency adverb - always", "I always study in the evening."),
            ("Parlo ___ italiano.", "bene", "Manner adverb - well", "I speak Italian well."),
            ("Vado a casa ___.", "adesso", "Time adverb - now", "I'm going home now."),
            ("L'ufficio è ___ casa mia.", "vicino", "Place adverb - near", "The office is near my house."),
        ]

        # Randomly select templates
        selected = random.sample(templates, min(count, len(templates)))

        questions = []
        for sentence, correct, explanation, english in selected:
            # Generate choices based on the type of adverb
            if correct in ["sempre", "mai", "spesso", "raramente", "qualche volta"]:
                # Frequency adverbs
                all_choices = ["sempre", "mai", "spesso", "raramente", "qualche volta"]
            elif correct in ["bene", "male", "piano", "forte", "velocemente", "lentamente"]:
                # Manner adverbs
                all_choices = ["bene", "male", "piano", "forte", "velocemente", "lentamente"]
            elif correct in ["ora", "adesso", "oggi", "ieri", "domani", "presto", "tardi"]:
                # Time adverbs
                all_choices = ["ora", "adesso", "oggi", "ieri", "domani", "presto", "tardi"]
            else:
                # Place adverbs
                all_choices = ["qui", "lì", "là", "vicino", "lontano", "sopra", "sotto"]

            # Always include the correct answer
            choices = [correct]
            # Add 3 more random choices
            remaining = [c for c in all_choices if c != correct]
            choices.extend(random.sample(remaining, min(3, len(remaining))))
            random.shuffle(choices)

            questions.append({
                "question": sentence,
                "answer": correct,
                "type": "multiple_choice",
                "choices": choices,
                "hint": english,
                "explanation": explanation
            })

        return questions

    def generate_imperative_practice(self, count: int = 10) -> List[Dict]:
        """Practice Italian imperative (command) forms.

        Imperative is used for commands, instructions, and requests.
        Forms: tu (informal you), Lei (formal you), noi (let's), voi (you plural)
        """
        import random

        templates = [
            # Tu form (informal you) - regular verbs
            ("___ la porta! (aprire - tu)", "Apri", "Imperative tu form - open", "Open the door!"),
            ("___ piano! (parlare - tu)", "Parla", "Imperative tu form - speak", "Speak quietly!"),
            ("___ la finestra! (chiudere - tu)", "Chiudi", "Imperative tu form - close", "Close the window!"),
            ("___ qui! (venire - tu)", "Vieni", "Imperative tu form - come", "Come here!"),
            ("___ a casa! (andare - tu)", "Va'", "Imperative tu form - go (irregular)", "Go home!"),
            ("___ il libro! (leggere - tu)", "Leggi", "Imperative tu form - read", "Read the book!"),
            ("___ la verità! (dire - tu)", "Di'", "Imperative tu form - say (irregular)", "Tell the truth!"),
            ("___ pazienza! (avere - tu)", "Abbi", "Imperative tu form - have (irregular)", "Have patience!"),
            ("___ gentile! (essere - tu)", "Sii", "Imperative tu form - be (irregular)", "Be kind!"),
            ("___ il caffè! (fare - tu)", "Fa'", "Imperative tu form - make (irregular)", "Make the coffee!"),

            # Lei form (formal you)
            ("___ pure! (entrare - Lei)", "Entri", "Imperative Lei form - enter", "Please enter!"),
            ("___ qui, prego. (aspettare - Lei)", "Aspetti", "Imperative Lei form - wait", "Wait here, please."),
            ("___ un attimo. (scusare - Lei)", "Scusi", "Imperative Lei form - excuse", "Excuse me a moment."),
            ("___ da questa parte. (venire - Lei)", "Venga", "Imperative Lei form - come", "Come this way."),
            ("___ con calma. (parlare - Lei)", "Parli", "Imperative Lei form - speak", "Speak calmly."),
            ("___ questa medicina. (prendere - Lei)", "Prenda", "Imperative Lei form - take", "Take this medicine."),

            # Noi form (let's)
            ("___ al cinema! (andare - noi)", "Andiamo", "Imperative noi form - let's go", "Let's go to the cinema!"),
            ("___ una pizza! (mangiare - noi)", "Mangiamo", "Imperative noi form - let's eat", "Let's eat a pizza!"),
            ("___ domani! (partire - noi)", "Partiamo", "Imperative noi form - let's leave", "Let's leave tomorrow!"),
            ("___ un caffè! (prendere - noi)", "Prendiamo", "Imperative noi form - let's take", "Let's have a coffee!"),

            # Voi form (you plural)
            ("___ attenti! (stare - voi)", "State", "Imperative voi form - be/stay", "Be careful!"),
            ("___ forte! (parlare - voi)", "Parlate", "Imperative voi form - speak", "Speak loudly!"),
            ("___ i compiti! (fare - voi)", "Fate", "Imperative voi form - do", "Do your homework!"),
            ("___ subito! (venire - voi)", "Venite", "Imperative voi form - come", "Come immediately!"),
            ("___ buoni! (essere - voi)", "Siate", "Imperative voi form - be", "Be good!"),

            # Common expressions
            ("___ attenzione! (fare - tu)", "Fa'", "Imperative - pay attention", "Pay attention!"),
            ("___ silenzio! (fare - voi)", "Fate", "Imperative - be quiet", "Be quiet!"),
            ("___ presto! (venire - tu)", "Vieni", "Imperative - come", "Come quickly!"),
        ]

        # Randomly select templates
        selected = random.sample(templates, min(count, len(templates)))

        questions = []
        for sentence, correct, explanation, english in selected:
            # Generate choices based on similar imperative forms
            if "tu" in sentence:
                all_choices = ["Apri", "Parla", "Chiudi", "Vieni", "Va'", "Leggi", "Di'", "Abbi", "Sii", "Fa'"]
            elif "Lei" in sentence:
                all_choices = ["Entri", "Aspetti", "Scusi", "Venga", "Parli", "Prenda"]
            elif "noi" in sentence:
                all_choices = ["Andiamo", "Mangiamo", "Partiamo", "Prendiamo"]
            else:  # voi
                all_choices = ["State", "Parlate", "Fate", "Venite", "Siate"]

            # Always include the correct answer
            choices = [correct]
            # Add 3 more random choices
            remaining = [c for c in all_choices if c != correct]
            choices.extend(random.sample(remaining, min(3, len(remaining))))
            random.shuffle(choices)

            questions.append({
                "question": sentence,
                "answer": correct,
                "type": "multiple_choice",
                "choices": choices,
                "hint": english,
                "explanation": explanation
            })

        return questions

    def generate_conditional_present(self, count: int = 10) -> List[Dict]:
        """Practice Italian conditional present (condizionale presente).

        The conditional is used for:
        - Polite requests: Vorrei un caffè (I would like a coffee)
        - Hypothetical situations: Sarebbe bello (It would be nice)
        - Advice/suggestions: Dovresti studiare (You should study)

        Formation: infinitive stem + -ei, -esti, -ebbe, -emmo, -este, -ebbero
        """
        import random

        templates = [
            # Regular -are verbs
            ("Io ___ volentieri in Italia. (viaggiare - io)", "viaggerei", "Conditional - I would travel", "I would gladly travel to Italy."),
            ("Tu ___ l'italiano? (parlare - tu)", "parleresti", "Conditional - you would speak", "Would you speak Italian?"),
            ("Lei ___ domani. (arrivare - lei)", "arriverebbe", "Conditional - she would arrive", "She would arrive tomorrow."),
            ("Noi ___ insieme. (cenare - noi)", "ceneremmo", "Conditional - we would have dinner", "We would have dinner together."),

            # Regular -ere verbs
            ("Io ___ un libro. (leggere - io)", "leggerei", "Conditional - I would read", "I would read a book."),
            ("Tu ___ la verità? (credere - tu)", "crederesti", "Conditional - you would believe", "Would you believe the truth?"),
            ("Lui ___ una lettera. (scrivere - lui)", "scriverebbe", "Conditional - he would write", "He would write a letter."),

            # Regular -ire verbs
            ("Io ___ la finestra. (aprire - io)", "aprirei", "Conditional - I would open", "I would open the window."),
            ("Tu ___ alle otto. (partire - tu)", "partiresti", "Conditional - you would leave", "You would leave at eight."),
            ("Lei ___ subito. (capire - lei)", "capirebbe", "Conditional - she would understand", "She would understand immediately."),

            # Irregular: volere (to want)
            ("Io ___ un caffè. (volere - io)", "vorrei", "Conditional irregular - I would like", "I would like a coffee."),
            ("Tu ___ venire? (volere - tu)", "vorresti", "Conditional irregular - you would like", "Would you like to come?"),
            ("Lei ___ aiuto. (volere - lei)", "vorrebbe", "Conditional irregular - she would like", "She would like help."),
            ("Noi ___ partire. (volere - noi)", "vorremmo", "Conditional irregular - we would like", "We would like to leave."),

            # Irregular: essere (to be)
            ("___ bello andare al mare. (essere - lui/lei)", "Sarebbe", "Conditional irregular - it would be", "It would be nice to go to the sea."),
            ("Io ___ felice di aiutarti. (essere - io)", "sarei", "Conditional irregular - I would be", "I would be happy to help you."),
            ("Tu ___ contento? (essere - tu)", "saresti", "Conditional irregular - you would be", "Would you be happy?"),

            # Irregular: avere (to have)
            ("Io ___ bisogno di aiuto. (avere - io)", "avrei", "Conditional irregular - I would have", "I would need help."),
            ("Tu ___ tempo? (avere - tu)", "avresti", "Conditional irregular - you would have", "Would you have time?"),
            ("Lei ___ ragione. (avere - lei)", "avrebbe", "Conditional irregular - she would have/be right", "She would be right."),

            # Irregular: dovere (should/ought to)
            ("Io ___ studiare. (dovere - io)", "dovrei", "Conditional irregular - I should", "I should study."),
            ("Tu ___ riposare. (dovere - tu)", "dovresti", "Conditional irregular - you should", "You should rest."),
            ("Lui ___ lavorare di più. (dovere - lui)", "dovrebbe", "Conditional irregular - he should", "He should work more."),

            # Irregular: potere (could)
            ("Io ___ aiutarti. (potere - io)", "potrei", "Conditional irregular - I could", "I could help you."),
            ("Tu ___ venire domani? (potere - tu)", "potresti", "Conditional irregular - you could", "Could you come tomorrow?"),
            ("Lei ___ telefonare. (potere - lei)", "potrebbe", "Conditional irregular - she could", "She could call."),

            # Irregular: fare (to do/make)
            ("Io ___ un errore. (fare - io)", "farei", "Conditional irregular - I would do/make", "I would make a mistake."),
            ("Tu ___ meglio ad aspettare. (fare - tu)", "faresti", "Conditional irregular - you would do", "You would do better to wait."),
            ("Lei ___ qualsiasi cosa. (fare - lei)", "farebbe", "Conditional irregular - she would do", "She would do anything."),

            # Irregular: andare (to go)
            ("Io ___ al cinema. (andare - io)", "andrei", "Conditional irregular - I would go", "I would go to the cinema."),
            ("Tu ___ con me? (andare - tu)", "andresti", "Conditional irregular - you would go", "Would you go with me?"),
            ("Lui ___ volentieri. (andare - lui)", "andrebbe", "Conditional irregular - he would go", "He would gladly go."),

            # Irregular: venire (to come)
            ("Io ___ domani. (venire - io)", "verrei", "Conditional irregular - I would come", "I would come tomorrow."),
            ("Tu ___ alla festa? (venire - tu)", "verresti", "Conditional irregular - you would come", "Would you come to the party?"),
            ("Lei ___ con noi. (venire - lei)", "verrebbe", "Conditional irregular - she would come", "She would come with us."),
        ]

        # Randomly select templates
        selected = random.sample(templates, min(count, len(templates)))

        questions = []
        for sentence, correct, explanation, english in selected:
            # Generate choices based on conditional conjugations
            if correct in ["vorrei", "vorresti", "vorrebbe", "vorremmo"]:
                all_choices = ["vorrei", "vorresti", "vorrebbe", "vorremmo"]
            elif correct in ["sarei", "saresti", "sarebbe"]:
                all_choices = ["sarei", "saresti", "sarebbe", "Sarebbe"]
            elif correct in ["avrei", "avresti", "avrebbe"]:
                all_choices = ["avrei", "avresti", "avrebbe"]
            elif correct in ["dovrei", "dovresti", "dovrebbe"]:
                all_choices = ["dovrei", "dovresti", "dovrebbe"]
            elif correct in ["potrei", "potresti", "potrebbe"]:
                all_choices = ["potrei", "potresti", "potrebbe"]
            elif correct in ["farei", "faresti", "farebbe"]:
                all_choices = ["farei", "faresti", "farebbe"]
            elif correct in ["andrei", "andresti", "andrebbe"]:
                all_choices = ["andrei", "andresti", "andrebbe"]
            elif correct in ["verrei", "verresti", "verrebbe"]:
                all_choices = ["verrei", "verresti", "verrebbe"]
            else:
                # Regular verbs - mix different verbs to make it challenging
                all_choices = ["viaggerei", "parleresti", "arriverebbe", "leggerei", "crederesti", "scriverebbe",
                              "aprirei", "partiresti", "capirebbe", "ceneremmo"]

            # Always include the correct answer
            choices = [correct]
            # Add 3 more random choices
            remaining = [c for c in all_choices if c != correct]
            choices.extend(random.sample(remaining, min(3, len(remaining))))
            random.shuffle(choices)

            questions.append({
                "question": sentence,
                "answer": correct,
                "type": "multiple_choice",
                "choices": choices,
                "hint": english,
                "explanation": explanation
            })

        return questions

    def generate_present_tense_conjugation(self, count: int = 10) -> List[Dict]:
        """
        Generate present tense conjugation practice for A1 level.
        Tests users on conjugating verbs in the present tense.
        Includes both regular and irregular verbs.
        """
        cursor = self.db.conn.cursor()

        questions = []

        # Get all present tense A1 verbs
        cursor.execute("""
            SELECT DISTINCT infinitive, english, verb_type
            FROM verb_conjugations
            WHERE tense = 'presente' AND level = 'A1'
        """)

        verbs = cursor.fetchall()

        if not verbs:
            return []

        # Generate questions
        for _ in range(count):
            # Pick a random verb
            infinitive, english, verb_type = random.choice(verbs)

            # Pick a random person
            persons = ["io", "tu", "lui_lei", "noi", "voi", "loro"]
            person = random.choice(persons)

            # Get the correct conjugation
            cursor.execute("""
                SELECT conjugated_form
                FROM verb_conjugations
                WHERE infinitive = ? AND tense = 'presente' AND person = ?
            """, (infinitive, person))

            result = cursor.fetchone()
            if not result:
                continue

            correct_form = result[0]

            # Person display names
            person_display = {
                "io": "io",
                "tu": "tu",
                "lui_lei": "lui/lei",
                "noi": "noi",
                "voi": "voi",
                "loro": "loro"
            }

            # Create question
            question_text = f"Conjugate '{infinitive}' ({english}) in the present tense for '{person_display[person]}'"

            # Determine if verb is regular or irregular
            regularity = "irregular" if verb_type == "irregular" else "regular"

            # Create explanation based on verb type
            if verb_type == "irregular":
                explanation = f"'{infinitive}' is an irregular verb. The present tense conjugation for {person_display[person]} is '{correct_form}'."
            elif verb_type == "regular_are":
                explanation = f"'{infinitive}' is a regular -are verb. For {person_display[person]}, remove -are and add the appropriate ending: {correct_form}."
            elif verb_type == "regular_ere":
                explanation = f"'{infinitive}' is a regular -ere verb. For {person_display[person]}, remove -ere and add the appropriate ending: {correct_form}."
            elif verb_type == "regular_ire":
                explanation = f"'{infinitive}' is a regular -ire verb. For {person_display[person]}, remove -ire and add the appropriate ending: {correct_form}."
            elif verb_type == "regular_isc":
                explanation = f"'{infinitive}' is a -ire verb that takes -isc- in some forms. For {person_display[person]}, the conjugation is: {correct_form}."
            else:
                explanation = f"The present tense conjugation of '{infinitive}' for {person_display[person]} is '{correct_form}'."

            # Get other conjugations of the same verb for multiple choice options
            cursor.execute("""
                SELECT conjugated_form
                FROM verb_conjugations
                WHERE infinitive = ? AND tense = 'presente' AND person != ?
                ORDER BY RANDOM()
                LIMIT 3
            """, (infinitive, person))

            other_forms = [row[0] for row in cursor.fetchall()]

            # Build choices
            choices = [correct_form] + other_forms
            random.shuffle(choices)

            # Ensure we have at least 4 choices
            if len(choices) < 4:
                # Add some other verb conjugations
                cursor.execute("""
                    SELECT conjugated_form
                    FROM verb_conjugations
                    WHERE infinitive != ? AND tense = 'presente' AND person = ?
                    ORDER BY RANDOM()
                    LIMIT ?
                """, (infinitive, person, 4 - len(choices)))

                extra_forms = [row[0] for row in cursor.fetchall()]
                choices.extend(extra_forms)
                random.shuffle(choices)

            questions.append({
                "question": question_text,
                "answer": correct_form,
                "type": "multiple_choice",
                "choices": choices[:4],
                "hint": f"{english} - {person_display[person]} ({regularity} verb)",
                "explanation": explanation
            })

        return questions

    def generate_subjunctive_present(self, count: int = 10) -> List[Dict]:
        """
        Generate subjunctive present (congiuntivo presente) practice for A2 level.
        The subjunctive is used to express doubt, possibility, desire, or emotion.
        """

        # Common subjunctive expressions and example sentences
        examples = [
            # With "che" clauses - doubt/uncertainty
            {
                "italian": "Penso che tu _____ ragione.",
                "english": "I think that you are right.",
                "answer": "abbia",
                "infinitive": "avere",
                "person": "tu",
                "trigger": "Penso che (I think that)",
                "explanation": "After 'penso che' (I think that), we use the subjunctive. Avere → abbia (tu form)."
            },
            {
                "italian": "Credo che lei _____ italiana.",
                "english": "I believe that she is Italian.",
                "answer": "sia",
                "infinitive": "essere",
                "person": "lei",
                "trigger": "Credo che (I believe that)",
                "explanation": "After 'credo che' (I believe that), we use the subjunctive. Essere → sia (lei form)."
            },
            {
                "italian": "Dubito che loro _____ la verità.",
                "english": "I doubt that they know the truth.",
                "answer": "sappiano",
                "infinitive": "sapere",
                "person": "loro",
                "trigger": "Dubito che (I doubt that)",
                "explanation": "After 'dubito che' (I doubt that), we use the subjunctive. Sapere → sappiano (loro form)."
            },
            {
                "italian": "Non penso che Marco _____ bene l'italiano.",
                "english": "I don't think that Marco speaks Italian well.",
                "answer": "parli",
                "infinitive": "parlare",
                "person": "lui",
                "trigger": "Non penso che (I don't think that)",
                "explanation": "After 'non penso che' (I don't think that), we use the subjunctive. Parlare → parli (lui form)."
            },
            # Desire/wish
            {
                "italian": "Voglio che tu _____ felice.",
                "english": "I want you to be happy.",
                "answer": "sia",
                "infinitive": "essere",
                "person": "tu",
                "trigger": "Voglio che (I want that)",
                "explanation": "After 'voglio che' (I want that), we use the subjunctive. Essere → sia (tu form)."
            },
            {
                "italian": "Spero che voi _____ presto.",
                "english": "I hope that you arrive soon.",
                "answer": "arriviate",
                "infinitive": "arrivare",
                "person": "voi",
                "trigger": "Spero che (I hope that)",
                "explanation": "After 'spero che' (I hope that), we use the subjunctive. Arrivare → arriviate (voi form)."
            },
            {
                "italian": "Desidero che lui mi _____ aiutare.",
                "english": "I wish that he would help me.",
                "answer": "possa",
                "infinitive": "potere",
                "person": "lui",
                "trigger": "Desidero che (I wish that)",
                "explanation": "After 'desidero che' (I wish that), we use the subjunctive. Potere → possa (lui form)."
            },
            # Emotion
            {
                "italian": "Sono contento che lei _____ qui.",
                "english": "I am happy that she is here.",
                "answer": "sia",
                "infinitive": "essere",
                "person": "lei",
                "trigger": "Sono contento che (I am happy that)",
                "explanation": "After expressions of emotion like 'sono contento che', we use the subjunctive. Essere → sia (lei form)."
            },
            {
                "italian": "Mi dispiace che tu non _____ venire.",
                "english": "I'm sorry that you can't come.",
                "answer": "possa",
                "infinitive": "potere",
                "person": "tu",
                "trigger": "Mi dispiace che (I'm sorry that)",
                "explanation": "After 'mi dispiace che' (I'm sorry that), we use the subjunctive. Potere → possa (tu form)."
            },
            {
                "italian": "Ho paura che loro non _____ in tempo.",
                "english": "I'm afraid that they won't arrive in time.",
                "answer": "arrivino",
                "infinitive": "arrivare",
                "person": "loro",
                "trigger": "Ho paura che (I'm afraid that)",
                "explanation": "After 'ho paura che' (I'm afraid that), we use the subjunctive. Arrivare → arrivino (loro form)."
            },
            # Necessity
            {
                "italian": "È necessario che noi _____ subito.",
                "english": "It's necessary that we leave immediately.",
                "answer": "partiamo",
                "infinitive": "partire",
                "person": "noi",
                "trigger": "È necessario che (It's necessary that)",
                "explanation": "After 'è necessario che' (it's necessary that), we use the subjunctive. Partire → partiamo (noi form)."
            },
            {
                "italian": "Bisogna che tu _____ la verità.",
                "english": "You must tell the truth.",
                "answer": "dica",
                "infinitive": "dire",
                "person": "tu",
                "trigger": "Bisogna che (It's necessary that)",
                "explanation": "After 'bisogna che' (it's necessary that), we use the subjunctive. Dire → dica (tu form)."
            },
            {
                "italian": "È importante che voi _____ attenzione.",
                "english": "It's important that you pay attention.",
                "answer": "facciate",
                "infinitive": "fare",
                "person": "voi",
                "trigger": "È importante che (It's important that)",
                "explanation": "After 'è importante che' (it's important that), we use the subjunctive. Fare → facciate (voi form)."
            },
            # Possibility
            {
                "italian": "È possibile che lui _____ in ritardo.",
                "english": "It's possible that he is late.",
                "answer": "sia",
                "infinitive": "essere",
                "person": "lui",
                "trigger": "È possibile che (It's possible that)",
                "explanation": "After 'è possibile che' (it's possible that), we use the subjunctive. Essere → sia (lui form)."
            },
            {
                "italian": "Può darsi che loro _____ già partiti.",
                "english": "It may be that they have already left.",
                "answer": "siano",
                "infinitive": "essere",
                "person": "loro",
                "trigger": "Può darsi che (It may be that)",
                "explanation": "After 'può darsi che' (it may be that), we use the subjunctive. Essere → siano (loro form)."
            },
            # More examples with common verbs
            {
                "italian": "Penso che Maria _____ molto bene.",
                "english": "I think that Maria cooks very well.",
                "answer": "cucini",
                "infinitive": "cucinare",
                "person": "lei",
                "trigger": "Penso che (I think that)",
                "explanation": "After 'penso che', we use the subjunctive. Cucinare → cucini (lei form)."
            },
            {
                "italian": "Spero che il tempo _____ bello domani.",
                "english": "I hope that the weather is nice tomorrow.",
                "answer": "sia",
                "infinitive": "essere",
                "person": "il tempo",
                "trigger": "Spero che (I hope that)",
                "explanation": "After 'spero che', we use the subjunctive. Essere → sia (third person singular)."
            },
            {
                "italian": "Non credo che lui _____ già finito.",
                "english": "I don't believe that he has already finished.",
                "answer": "abbia",
                "infinitive": "avere",
                "person": "lui",
                "trigger": "Non credo che (I don't believe that)",
                "explanation": "After 'non credo che', we use the subjunctive. Avere → abbia (lui form) + finito."
            },
            {
                "italian": "Voglio che tutti _____ questa lezione.",
                "english": "I want everyone to understand this lesson.",
                "answer": "capiscano",
                "infinitive": "capire",
                "person": "tutti",
                "trigger": "Voglio che (I want that)",
                "explanation": "After 'voglio che', we use the subjunctive. Capire → capiscano (loro form)."
            },
            {
                "italian": "È meglio che noi _____ a casa.",
                "english": "It's better that we stay at home.",
                "answer": "restiamo",
                "infinitive": "restare",
                "person": "noi",
                "trigger": "È meglio che (It's better that)",
                "explanation": "After 'è meglio che' (it's better that), we use the subjunctive. Restare → restiamo (noi form)."
            },
            {
                "italian": "Temo che il treno _____ in ritardo.",
                "english": "I fear that the train is late.",
                "answer": "sia",
                "infinitive": "essere",
                "person": "il treno",
                "trigger": "Temo che (I fear that)",
                "explanation": "After 'temo che' (I fear that), we use the subjunctive. Essere → sia (third person singular)."
            }
        ]

        # Randomly select questions
        selected = random.sample(examples, min(count, len(examples)))
        questions = []

        for item in selected:
            # Create multiple choice options
            correct_answer = item["answer"]

            # Common subjunctive forms for wrong answers
            all_subjunctive_forms = {
                "essere": ["sia", "siano", "siamo", "siate"],
                "avere": ["abbia", "abbiano", "abbiamo", "abbiate"],
                "fare": ["faccia", "facciano", "facciamo", "facciate"],
                "andare": ["vada", "vadano", "andiamo", "andiate"],
                "potere": ["possa", "possano", "possiamo", "possiate"],
                "sapere": ["sappia", "sappiano", "sappiamo", "sappiate"],
                "dire": ["dica", "dicano", "diciamo", "diciate"],
                "venire": ["venga", "vengano", "veniamo", "veniate"],
                "parlare": ["parli", "parlino", "parliamo", "parliate"],
                "arrivare": ["arrivi", "arrivino", "arriviamo", "arriviate"],
                "capire": ["capisca", "capiscano", "capiamo", "capiate"],
                "partire": ["parta", "partano", "partiamo", "partiate"],
                "cucinare": ["cucini", "cucinino", "cuciniamo", "cuciniate"],
                "restare": ["resti", "restino", "restiamo", "restiate"]
            }

            # Get wrong answers from the same verb if possible
            if item["infinitive"] in all_subjunctive_forms:
                possible_wrong = [f for f in all_subjunctive_forms[item["infinitive"]] if f != correct_answer]
            else:
                # Use random subjunctive forms
                possible_wrong = ["sia", "abbia", "faccia", "vada", "possa", "sappia", "parli", "arrivi"]
                possible_wrong = [f for f in possible_wrong if f != correct_answer]

            # Build choices
            wrong_answers = random.sample(possible_wrong, min(3, len(possible_wrong)))
            choices = [correct_answer] + wrong_answers
            random.shuffle(choices)

            questions.append({
                "question": item["italian"],
                "answer": correct_answer,
                "type": "multiple_choice",
                "choices": choices,
                "hint": f"{item['english']} | Trigger: {item['trigger']}",
                "explanation": item["explanation"]
            })

        return questions

    def generate_pronominal_verbs(self, count: int = 10) -> List[Dict]:
        """
        Generate pronominal verbs practice for A2 level.
        Pronominal verbs use particles like ci, ne, si attached to verbs.
        Examples: farcela (to manage), andarsene (to go away), volerci (to take time).
        """

        # Common pronominal verb constructions with examples
        examples = [
            # FARCELA - to manage/make it
            {
                "italian": "Non ce la faccio a finire tutto oggi!",
                "english": "I can't manage to finish everything today!",
                "answer": "farcela",
                "explanation": "'Farcela' means 'to manage/make it'. The pronoun 'ce la' is attached to 'fare'. Example: Ce la faccio! (I can do it!)"
            },
            {
                "italian": "Pensi di ____ a arrivare in tempo?",
                "english": "Do you think you can make it on time?",
                "answer": "farcela",
                "explanation": "'Farcela' = to manage/succeed. The 'ce la' particles combine with the verb fare."
            },
            # ANDARSENE - to go away/leave
            {
                "italian": "Me ne vado subito!",
                "english": "I'm leaving right now!",
                "answer": "andarsene",
                "explanation": "'Andarsene' means 'to go away/leave'. The 'ne' is attached to andare. Example: Te ne vai? (Are you leaving?)"
            },
            {
                "italian": "Dopo la discussione, lui se n'è andato arrabbiato.",
                "english": "After the argument, he left angry.",
                "answer": "andarsene",
                "explanation": "'Andarsene' = to go away/leave. In passato prossimo: me ne sono andato/a, te ne sei andato/a, etc."
            },
            # VOLERCI - to take/require (time/ingredients)
            {
                "italian": "Ci vogliono tre ore per arrivare a Roma.",
                "english": "It takes three hours to get to Rome.",
                "answer": "volerci",
                "explanation": "'Volerci' means 'to take/require' (for time/things needed). Always use 'ci': ci vuole (singular), ci vogliono (plural)."
            },
            {
                "italian": "Quanto tempo ci vuole per imparare l'italiano?",
                "english": "How long does it take to learn Italian?",
                "answer": "volerci",
                "explanation": "'Volerci' = to take (time). 'Ci vuole' for singular, 'ci vogliono' for plural. Example: Ci vuole pazienza (It takes patience)."
            },
            # METTERCI - to take (time, by someone)
            {
                "italian": "Ci metto due ore per arrivare al lavoro.",
                "english": "It takes me two hours to get to work.",
                "answer": "metterci",
                "explanation": "'Metterci' means 'to take (time)' for a specific person. Ci metto, ci metti, ci mette, etc. Different from volerci!"
            },
            {
                "italian": "Quanto tempo ci hai messo per fare questo lavoro?",
                "english": "How long did it take you to do this work?",
                "answer": "metterci",
                "explanation": "'Metterci' = to take (time) with a subject. 'Ci metto 10 minuti' (I take 10 minutes)."
            },
            # CAVARSELA - to manage/get by
            {
                "italian": "Me la cavo abbastanza bene con l'italiano.",
                "english": "I get by pretty well with Italian.",
                "answer": "cavarsela",
                "explanation": "'Cavarsela' means 'to manage/get by/cope'. Uses 'se la': me la cavo, te la cavi, se la cava, etc."
            },
            {
                "italian": "Come te la cavi con il nuovo lavoro?",
                "english": "How are you managing with the new job?",
                "answer": "cavarsela",
                "explanation": "'Cavarsela' = to get by/manage. 'Se la cava bene' = He/she is doing well/managing well."
            },
            # PRENDERSELA - to take it badly/get upset
            {
                "italian": "Non te la prendere! Era solo uno scherzo.",
                "english": "Don't take it badly! It was just a joke.",
                "answer": "prendersela",
                "explanation": "'Prendersela' means 'to take it badly/get upset/offended'. Uses 'se la': me la prendo, te la prendi, etc."
            },
            {
                "italian": "Lei se l'è presa molto quando ha sentito la notizia.",
                "english": "She got very upset when she heard the news.",
                "answer": "prendersela",
                "explanation": "'Prendersela' = to take offense/get upset. 'Prendersela con qualcuno' = to take it out on someone."
            },
            # FREGARSENE - to not care (colloquial)
            {
                "italian": "Me ne frego di quello che dicono!",
                "english": "I don't care what they say!",
                "answer": "fregarsene",
                "explanation": "'Fregarsene' means 'to not care' (informal). Uses 'ne': me ne frego, te ne freghi, se ne frega, etc."
            },
            # SENTIRSELA - to feel up to
            {
                "italian": "Non me la sento di uscire stasera.",
                "english": "I don't feel up to going out tonight.",
                "answer": "sentirsela",
                "explanation": "'Sentirsela' means 'to feel up to doing something'. Often used in negative: Non me la sento = I don't feel like it."
            },
            # ACCORGERSENE - to realize/notice
            {
                "italian": "Ti sei accorto dell'errore?",
                "english": "Did you notice the mistake?",
                "answer": "accorgersene",
                "explanation": "'Accorgersene' means 'to realize/notice'. Reflexive + 'ne': me ne accorgo, te ne accorgi, se ne accorge, etc."
            },
            {
                "italian": "Non me ne sono accorto subito.",
                "english": "I didn't realize it right away.",
                "answer": "accorgersene",
                "explanation": "'Accorgersene' = to notice/realize. Passato prossimo: me ne sono accorto/a, te ne sei accorto/a, etc."
            },
            # ASPETTARSELO - to expect it
            {
                "italian": "Non me l'aspettavo affatto!",
                "english": "I wasn't expecting it at all!",
                "answer": "aspettarselo",
                "explanation": "'Aspettarselo' means 'to expect it'. Uses 'se lo/la': me lo aspetto, te lo aspetti, se lo aspetta, etc."
            },
            # PASSARSELA - to get along/fare
            {
                "italian": "Come te la passi ultimamente?",
                "english": "How are you doing lately?",
                "answer": "passarsela",
                "explanation": "'Passarsela' means 'to get along/fare' (how you're doing). Se la passa bene = he/she is doing well."
            },
            # GODERSELA - to enjoy oneself
            {
                "italian": "Mi sono goduto la vacanza al mare.",
                "english": "I enjoyed my vacation at the beach.",
                "answer": "godersela",
                "explanation": "'Godersela' means 'to enjoy oneself/have a good time'. Uses 'se la': me la godo, te la godi, se la gode, etc."
            },
            # SBRIGARSELA - to hurry up/get it done quickly
            {
                "italian": "Sbrigati, altrimenti facciamo tardi!",
                "english": "Hurry up, otherwise we'll be late!",
                "answer": "sbrigarsi",
                "explanation": "'Sbrigarsi' means 'to hurry up'. Sbrigati! = Hurry up! Can also use 'sbrigarsela' to mean 'get it done quickly'."
            }
        ]

        # Randomly select questions
        selected = random.sample(examples, min(count, len(examples)))
        questions = []

        for item in selected:
            # Common pronominal verbs for choices
            all_verbs = [
                "farcela", "andarsene", "volerci", "metterci", "cavarsela",
                "prendersela", "fregarsene", "sentirsela", "accorgersene",
                "aspettarselo", "passarsela", "godersela", "sbrigarsi"
            ]

            # Build choices - include correct answer and 3 random others
            choices = [item["answer"]]
            wrong_choices = [v for v in all_verbs if v != item["answer"]]
            choices.extend(random.sample(wrong_choices, min(3, len(wrong_choices))))
            random.shuffle(choices)

            questions.append({
                "question": item["italian"],
                "answer": item["answer"],
                "type": "multiple_choice",
                "choices": choices,
                "hint": item["english"],
                "explanation": item["explanation"]
            })

        return questions

    def generate_passive_voice(self, count: int = 10) -> List[Dict]:
        """
        Generate passive voice (forma passiva) practice for B1 level.
        The passive transforms "Subject does action" to "Action is done by subject".
        Italian passive: essere + past participle (agrees with subject)
        """

        # Passive voice examples with transformations
        examples = [
            # Present tense passives
            {
                "italian": "La lettera è scritta da Marco.",
                "english": "The letter is written by Marco.",
                "answer": "è scritta",
                "active": "Marco scrive la lettera",
                "explanation": "Passive present: essere (present) + past participle. 'Scritta' agrees with feminine 'lettera'. Active: Marco scrive la lettera."
            },
            {
                "italian": "I libri sono letti dagli studenti.",
                "english": "The books are read by the students.",
                "answer": "sono letti",
                "active": "Gli studenti leggono i libri",
                "explanation": "Passive present: essere (sono) + past participle. 'Letti' agrees with masculine plural 'libri'. Active: Gli studenti leggono i libri."
            },
            {
                "italian": "La pizza è mangiata dai bambini.",
                "english": "The pizza is eaten by the children.",
                "answer": "è mangiata",
                "active": "I bambini mangiano la pizza",
                "explanation": "Passive: essere + past participle. 'Mangiata' agrees with feminine singular 'pizza'."
            },
            {
                "italian": "Le case sono costruite dai muratori.",
                "english": "The houses are built by the builders.",
                "answer": "sono costruite",
                "active": "I muratori costruiscono le case",
                "explanation": "Passive: 'sono costruite' agrees with feminine plural 'case'."
            },
            # Past tense passives (passato prossimo)
            {
                "italian": "Il film è stato visto da milioni di persone.",
                "english": "The film was seen by millions of people.",
                "answer": "è stato visto",
                "active": "Milioni di persone hanno visto il film",
                "explanation": "Passive past: essere (passato prossimo) + past participle. 'È stato visto' = was seen (masculine singular)."
            },
            {
                "italian": "La casa è stata venduta l'anno scorso.",
                "english": "The house was sold last year.",
                "answer": "è stata venduta",
                "active": "Hanno venduto la casa l'anno scorso",
                "explanation": "Passive past: 'è stata venduta' agrees with feminine 'casa'. Was sold = è stata + past participle."
            },
            {
                "italian": "Le lettere sono state spedite ieri.",
                "english": "The letters were sent yesterday.",
                "answer": "sono state spedite",
                "active": "Hanno spedito le lettere ieri",
                "explanation": "Passive past: 'sono state spedite' agrees with feminine plural 'lettere'."
            },
            {
                "italian": "I documenti sono stati firmati dal direttore.",
                "english": "The documents were signed by the director.",
                "answer": "sono stati firmati",
                "active": "Il direttore ha firmato i documenti",
                "explanation": "Passive past: 'sono stati firmati' agrees with masculine plural 'documenti'."
            },
            # Future tense passives
            {
                "italian": "Il progetto sarà finito entro domani.",
                "english": "The project will be finished by tomorrow.",
                "answer": "sarà finito",
                "active": "Finiranno il progetto entro domani",
                "explanation": "Passive future: essere (future) + past participle. 'Sarà finito' = will be finished."
            },
            {
                "italian": "Le email saranno inviate questa sera.",
                "english": "The emails will be sent this evening.",
                "answer": "saranno inviate",
                "active": "Invieranno le email questa sera",
                "explanation": "Passive future: 'saranno inviate' agrees with feminine plural 'email'."
            },
            # Imperfect passive
            {
                "italian": "Il pane era fatto in casa ogni giorno.",
                "english": "The bread was made at home every day.",
                "answer": "era fatto",
                "active": "Facevano il pane in casa ogni giorno",
                "explanation": "Passive imperfect: essere (imperfect) + past participle. 'Era fatto' = was made (habitual)."
            },
            {
                "italian": "Le strade erano pulite ogni mattina.",
                "english": "The streets were cleaned every morning.",
                "answer": "erano pulite",
                "active": "Pulivano le strade ogni mattina",
                "explanation": "Passive imperfect: 'erano pulite' agrees with feminine plural 'strade'."
            },
            # Venire passive (alternative to essere)
            {
                "italian": "La pizza viene preparata al momento.",
                "english": "The pizza is prepared right away.",
                "answer": "viene preparata",
                "active": "Preparano la pizza al momento",
                "explanation": "Alternative passive with 'venire' instead of 'essere'. 'Viene preparata' = is prepared. Only for present/imperfect, NOT passato prossimo."
            },
            {
                "italian": "I documenti vengono controllati ogni settimana.",
                "english": "The documents are checked every week.",
                "answer": "vengono controllati",
                "active": "Controllano i documenti ogni settimana",
                "explanation": "Passive with 'venire': 'vengono controllati' agrees with masculine plural 'documenti'."
            },
            # Si passivante (passive with si)
            {
                "italian": "In Italia si parla italiano.",
                "english": "In Italy, Italian is spoken.",
                "answer": "si parla",
                "active": "In Italia parlano italiano",
                "explanation": "Si passivante: si + third person verb. 'Si parla' = is spoken. Common for general statements."
            },
            {
                "italian": "In questo ristorante si mangiano piatti tipici.",
                "english": "In this restaurant, typical dishes are eaten.",
                "answer": "si mangiano",
                "active": "In questo ristorante mangiano piatti tipici",
                "explanation": "Si passivante: si + third person plural. 'Si mangiano' agrees with plural 'piatti'."
            },
            {
                "italian": "Qui si vendono libri usati.",
                "english": "Used books are sold here.",
                "answer": "si vendono",
                "active": "Qui vendono libri usati",
                "explanation": "Si passivante: 'si vendono' agrees with plural 'libri'. Very common construction."
            },
            {
                "italian": "In estate si beve molta acqua.",
                "english": "In summer, a lot of water is drunk.",
                "answer": "si beve",
                "active": "In estate bevono molta acqua",
                "explanation": "Si passivante: 'si beve' with singular 'acqua'."
            },
            # Da + agent
            {
                "italian": "La canzone è cantata da Pavarotti.",
                "english": "The song is sung by Pavarotti.",
                "answer": "è cantata",
                "active": "Pavarotti canta la canzone",
                "explanation": "Passive: 'è cantata da Pavarotti'. 'Da' introduces the agent (who does the action)."
            },
            {
                "italian": "Romeo e Giulietta fu scritto da Shakespeare.",
                "english": "Romeo and Juliet was written by Shakespeare.",
                "answer": "fu scritto",
                "active": "Shakespeare scrisse Romeo e Giulietta",
                "explanation": "Passive with passato remoto: 'fu scritto da'. Used in literary/historical contexts."
            }
        ]

        # Randomly select questions
        selected = random.sample(examples, min(count, len(examples)))
        questions = []

        for item in selected:
            # Passive forms for choices
            passive_forms = [
                "è scritto", "è scritta", "sono scritti", "sono scritte",
                "è fatto", "è fatta", "sono fatti", "sono fatte",
                "è stato visto", "è stata vista", "sono stati visti", "sono state viste",
                "viene preparato", "viene preparata", "vengono preparati", "vengono preparate",
                "si parla", "si parlano", "si mangia", "si mangiano",
                "sarà finito", "sarà finita", "saranno finiti", "saranno finite",
                "era fatto", "era fatta", "erano fatti", "erano fatte"
            ]

            # Build choices
            correct_answer = item["answer"]
            choices = [correct_answer]

            # Add similar passive forms
            wrong_choices = [p for p in passive_forms if p != correct_answer]
            choices.extend(random.sample(wrong_choices, min(3, len(wrong_choices))))
            random.shuffle(choices)

            questions.append({
                "question": f"Identify the passive form: {item['italian']}",
                "answer": correct_answer,
                "type": "multiple_choice",
                "choices": choices,
                "hint": f"{item['english']} | Active: {item['active']}",
                "explanation": item["explanation"]
            })

        return questions

    def generate_conditional_past(self, count: int = 10) -> List[Dict]:
        """
        Generate conditional past (condizionale passato) practice for B1 level.
        Used to express what would have happened: avrei fatto = I would have done.
        Structure: avere/essere (conditional) + past participle
        """

        examples = [
            {
                "italian": "Io _____ venuto, ma ero malato.",
                "english": "I would have come, but I was sick.",
                "answer": "sarei",
                "infinitive": "venire",
                "explanation": "Conditional past: essere (conditional) + past participle. 'Sarei venuto' = would have come. Venire uses essere."
            },
            {
                "italian": "Loro _____ mangiato di più, ma erano già pieni.",
                "english": "They would have eaten more, but they were already full.",
                "answer": "avrebbero",
                "infinitive": "mangiare",
                "explanation": "Conditional past: 'avrebbero mangiato' = would have eaten. Regular verbs with avere."
            },
            {
                "italian": "Tu _____ dovuto studiare di più.",
                "english": "You should have studied more.",
                "answer": "avresti",
                "infinitive": "dovere",
                "explanation": "Conditional past with modal verbs: 'avresti dovuto' = should have. Dovere uses avere."
            },
            {
                "italian": "Noi _____ andati al cinema, ma pioveva.",
                "english": "We would have gone to the cinema, but it was raining.",
                "answer": "saremmo",
                "infinitive": "andare",
                "explanation": "Conditional past: 'saremmo andati' = would have gone. Andare uses essere."
            },
            {
                "italian": "Lei _____ partita prima, ma ha perso il treno.",
                "english": "She would have left earlier, but she missed the train.",
                "answer": "sarebbe",
                "infinitive": "partire",
                "explanation": "Conditional past: 'sarebbe partita' = would have left. Partire uses essere."
            },
            {
                "italian": "Voi _____ comprato quella casa?",
                "english": "Would you have bought that house?",
                "answer": "avreste",
                "infinitive": "comprare",
                "explanation": "Conditional past question: 'avreste comprato' = would have bought."
            },
            {
                "italian": "Lui _____ potuto aiutarti, ma non c'era.",
                "english": "He could have helped you, but he wasn't there.",
                "answer": "avrebbe",
                "infinitive": "potere",
                "explanation": "Conditional past with modal: 'avrebbe potuto' = could have. Potere uses avere."
            },
            {
                "italian": "Io non _____ fatto così.",
                "english": "I wouldn't have done that.",
                "answer": "avrei",
                "infinitive": "fare",
                "explanation": "Negative conditional past: 'non avrei fatto' = wouldn't have done."
            },
            {
                "italian": "Tu _____ stata più felice lì.",
                "english": "You would have been happier there.",
                "answer": "saresti",
                "infinitive": "essere",
                "explanation": "Conditional past of essere: 'saresti stata' = would have been (feminine)."
            },
            {
                "italian": "Loro _____ voluto venire con noi.",
                "english": "They would have wanted to come with us.",
                "answer": "avrebbero",
                "infinitive": "volere",
                "explanation": "Conditional past with volere: 'avrebbero voluto' = would have wanted."
            }
        ]

        selected = random.sample(examples, min(count, len(examples)))
        questions = []

        for item in selected:
            conditional_forms = ["avrei", "avresti", "avrebbe", "avremmo", "avreste", "avrebbero",
                                "sarei", "saresti", "sarebbe", "saremmo", "sareste", "sarebbero"]

            choices = [item["answer"]]
            wrong_choices = [f for f in conditional_forms if f != item["answer"]]
            choices.extend(random.sample(wrong_choices, min(3, len(wrong_choices))))
            random.shuffle(choices)

            questions.append({
                "question": item["italian"],
                "answer": item["answer"],
                "type": "multiple_choice",
                "choices": choices,
                "hint": item["english"],
                "explanation": item["explanation"]
            })

        return questions

    def generate_past_perfect(self, count: int = 10) -> List[Dict]:
        """
        Generate past perfect (trapassato prossimo) practice for B1 level.
        Used to express an action that happened before another past action.
        Structure: avere/essere (imperfect) + past participle
        """

        examples = [
            {
                "italian": "Quando sono arrivato, lui era già _____.",
                "english": "When I arrived, he had already left.",
                "answer": "partito",
                "full_form": "era partito",
                "infinitive": "partire",
                "explanation": "Past perfect (trapassato prossimo): imperfect of essere/avere + past participle. 'Era partito' = had left."
            },
            {
                "italian": "Non ho mangiato perché avevo già _____.",
                "english": "I didn't eat because I had already eaten.",
                "answer": "mangiato",
                "full_form": "avevo mangiato",
                "infinitive": "mangiare",
                "explanation": "Past perfect: 'avevo mangiato' = had eaten. Action before another past action."
            },
            {
                "italian": "Lei era stanca perché aveva _____ tutta la notte.",
                "english": "She was tired because she had worked all night.",
                "answer": "lavorato",
                "full_form": "aveva lavorato",
                "infinitive": "lavorare",
                "explanation": "Past perfect: 'aveva lavorato' = had worked. Explains why she was tired."
            },
            {
                "italian": "Eravamo tristi perché il nostro amico se n'era _____.",
                "english": "We were sad because our friend had gone away.",
                "answer": "andato",
                "full_form": "se n'era andato",
                "infinitive": "andarsene",
                "explanation": "Past perfect with pronominal verb: 'se n'era andato' = had gone away."
            },
            {
                "italian": "Quando siamo arrivati, lo spettacolo era già _____.",
                "english": "When we arrived, the show had already started.",
                "answer": "cominciato",
                "full_form": "era cominciato",
                "infinitive": "cominciare",
                "explanation": "Past perfect: 'era cominciato' = had started. The show started before we arrived."
            },
            {
                "italian": "Non sapevo che tu avevi già _____ quel libro.",
                "english": "I didn't know you had already read that book.",
                "answer": "letto",
                "full_form": "avevi letto",
                "infinitive": "leggere",
                "explanation": "Past perfect with irregular past participle: 'avevi letto' = had read."
            },
            {
                "italian": "Loro erano felici perché avevano _____ l'esame.",
                "english": "They were happy because they had passed the exam.",
                "answer": "superato",
                "full_form": "avevano superato",
                "infinitive": "superare",
                "explanation": "Past perfect: 'avevano superato' = had passed. Explains their happiness."
            },
            {
                "italian": "Mi sono reso conto che avevo _____ un errore.",
                "english": "I realized that I had made a mistake.",
                "answer": "fatto",
                "full_form": "avevo fatto",
                "infinitive": "fare",
                "explanation": "Past perfect with irregular verb: 'avevo fatto' = had made."
            },
            {
                "italian": "Quando siamo tornati, i bambini si erano già _____.",
                "english": "When we returned, the children had already gone to bed.",
                "answer": "addormentati",
                "full_form": "si erano addormentati",
                "infinitive": "addormentarsi",
                "explanation": "Past perfect reflexive: 'si erano addormentati' = had fallen asleep."
            },
            {
                "italian": "Non ho comprato il libro perché l'avevo già _____.",
                "english": "I didn't buy the book because I had already bought it.",
                "answer": "comprato",
                "full_form": "avevo comprato",
                "infinitive": "comprare",
                "explanation": "Past perfect: 'avevo comprato' = had bought. Action completed before deciding not to buy."
            }
        ]

        selected = random.sample(examples, min(count, len(examples)))
        questions = []

        for item in selected:
            participles = ["fatto", "detto", "letto", "scritto", "visto", "mangiato", "parlato",
                          "partito", "andato", "venuto", "stato", "avuto", "comprato", "lavorato",
                          "cominciato", "finito", "capito", "superato", "camminato", "addormentati"]

            choices = [item["answer"]]
            wrong_choices = [p for p in participles if p != item["answer"]]
            choices.extend(random.sample(wrong_choices, min(3, len(wrong_choices))))
            random.shuffle(choices)

            questions.append({
                "question": item["italian"],
                "answer": item["answer"],
                "type": "multiple_choice",
                "choices": choices,
                "hint": f"{item['english']} | Full form: {item['full_form']}",
                "explanation": item["explanation"]
            })

        return questions

    def generate_combined_pronouns(self, count: int = 10) -> List[Dict]:
        """
        Generate combined pronouns practice for B1 level.
        When direct and indirect pronouns combine: me lo, te la, glielo, ce li, etc.
        Rules: Indirect + Direct, some forms change (mi/ti/ci/vi → me/te/ce/ve before lo/la/li/le)
        """

        examples = [
            # Me + lo/la/li/le
            {
                "italian": "Puoi prestarmi il libro? Sì, _____ presto.",
                "english": "Can you lend me the book? Yes, I'll lend it to you.",
                "answer": "te lo",
                "breakdown": "te (to you) + lo (it)",
                "explanation": "'Te lo presto' = I lend it to you. Indirect 'ti' becomes 'te' before 'lo'. Order: indirect + direct."
            },
            {
                "italian": "Mi dai la penna? Sì, _____ do subito.",
                "english": "Will you give me the pen? Yes, I'll give it to you right away.",
                "answer": "te la",
                "breakdown": "te (to you) + la (it)",
                "explanation": "'Te la do' = I give it to you. 'Ti' becomes 'te' before 'la'."
            },
            {
                "italian": "Chi ti ha dato le chiavi? _____ ha date Marco.",
                "english": "Who gave you the keys? Marco gave them to me.",
                "answer": "Me le",
                "breakdown": "me (to me) + le (them)",
                "explanation": "'Me le ha date' = gave them to me. 'Mi' becomes 'me' before 'le'."
            },
            # Gli + lo/la/li/le → glielo/gliela/glieli/gliele
            {
                "italian": "Hai spiegato la lezione a Maria? Sì, _____ ho spiegata.",
                "english": "Did you explain the lesson to Maria? Yes, I explained it to her.",
                "answer": "gliela",
                "breakdown": "glie (to her) + la (it)",
                "explanation": "'Gliela ho spiegata' = I explained it to her. 'Gli/le' + 'la' = gliela. One word!"
            },
            {
                "italian": "Hai dato il regalo a tuo fratello? Sì, _____ ho dato ieri.",
                "english": "Did you give the gift to your brother? Yes, I gave it to him yesterday.",
                "answer": "glielo",
                "breakdown": "glie (to him) + lo (it)",
                "explanation": "'Glielo ho dato' = I gave it to him. 'Gli' + 'lo' = glielo (one word)."
            },
            {
                "italian": "Hai mostrato le foto ai tuoi amici? Sì, _____ ho mostrate.",
                "english": "Did you show the photos to your friends? Yes, I showed them to them.",
                "answer": "gliele",
                "breakdown": "glie (to them) + le (them)",
                "explanation": "'Gliele ho mostrate' = I showed them to them. 'Gli' + 'le' = gliele."
            },
            # Ce + lo/la/li/le
            {
                "italian": "Chi vi ha portato i regali? _____ ha portati Babbo Natale.",
                "english": "Who brought you the gifts? Santa Claus brought them to us.",
                "answer": "Ce li",
                "breakdown": "ce (to us) + li (them)",
                "explanation": "'Ce li ha portati' = brought them to us. 'Ci' becomes 'ce' before 'li'."
            },
            {
                "italian": "Vi hanno spiegato la regola? Sì, _____ hanno spiegata.",
                "english": "Did they explain the rule to you? Yes, they explained it to us.",
                "answer": "ce la",
                "breakdown": "ce (to us) + la (it)",
                "explanation": "'Ce la hanno spiegata' = they explained it to us. 'Ci' → 'ce' before 'la'."
            },
            # Ve + lo/la/li/le
            {
                "italian": "Chi vi ha dato i biglietti? _____ ha dati il direttore.",
                "english": "Who gave you the tickets? The director gave them to you.",
                "answer": "Ve li",
                "breakdown": "ve (to you pl) + li (them)",
                "explanation": "'Ve li ha dati' = gave them to you. 'Vi' becomes 've' before 'li'."
            },
            {
                "italian": "Ti hanno portato la torta? Sì, _____ hanno portata.",
                "english": "Did they bring you the cake? Yes, they brought it to me.",
                "answer": "me la",
                "breakdown": "me (to me) + la (it)",
                "explanation": "'Me la hanno portata' = they brought it to me. 'Mi' → 'me' before 'la'."
            },
            # More glielo examples
            {
                "italian": "Hai raccontato la storia ai bambini? Sì, _____ ho raccontata.",
                "english": "Did you tell the story to the children? Yes, I told it to them.",
                "answer": "gliela",
                "breakdown": "glie (to them) + la (it)",
                "explanation": "'Gliela ho raccontata' = I told it to them. Works for both singular and plural."
            },
            {
                "italian": "Puoi prestare i libri a Luca? Sì, _____ posso prestare.",
                "english": "Can you lend the books to Luca? Yes, I can lend them to him.",
                "answer": "glieli",
                "breakdown": "glie (to him) + li (them)",
                "explanation": "'Glieli posso prestare' = I can lend them to him. 'Gli' + 'li' = glieli."
            },
            # Reflexive + lo/la/li/le
            {
                "italian": "Mi metto il cappotto? Sì, _____ metti!",
                "english": "Should I put on my coat? Yes, put it on!",
                "answer": "mettitelo",
                "breakdown": "metti + te (yourself) + lo (it)",
                "explanation": "Reflexive with pronoun: 'mettitelo' = put it on yourself. Te + lo attached to infinitive/imperative."
            },
            {
                "italian": "Dovrei lavarmi le mani? Sì, _____ devi lavare!",
                "english": "Should I wash my hands? Yes, you must wash them!",
                "answer": "te le",
                "breakdown": "te (yourself) + le (them)",
                "explanation": "'Te le devi lavare' = you must wash them (your hands). Reflexive 'ti' → 'te' before 'le'."
            },
            # With imperatives
            {
                "italian": "Devo dare il messaggio a Laura?",
                "english": "Should I give the message to Laura?",
                "answer": "Daglielo",
                "breakdown": "da' (give) + glie (to her) + lo (it)",
                "explanation": "'Daglielo!' = Give it to her! With imperative, pronouns attach: da' + glielo = daglielo."
            },
            # Additional me lo/la/li/le examples
            {
                "italian": "Mi compri il giornale? Sì, _____ compro.",
                "english": "Will you buy me the newspaper? Yes, I'll buy it for you.",
                "answer": "te lo",
                "breakdown": "te (to you) + lo (it)",
                "explanation": "'Te lo compro' = I'll buy it for you."
            },
            {
                "italian": "Mi presti questi libri? Sì, _____ presto volentieri.",
                "english": "Will you lend me these books? Yes, I'll gladly lend them to you.",
                "answer": "te li",
                "breakdown": "te (to you) + li (them)",
                "explanation": "'Te li presto' = I'll lend them to you. 'Ti' → 'te' before 'li'."
            },
            {
                "italian": "Mi porti le valigie? Sì, _____ porto subito.",
                "english": "Will you bring me the suitcases? Yes, I'll bring them to you right away.",
                "answer": "te le",
                "breakdown": "te (to you) + le (them)",
                "explanation": "'Te le porto' = I'll bring them to you."
            },
            {
                "italian": "Chi mi ha mandato questo pacco? _____ ha mandato tua sorella.",
                "english": "Who sent me this package? Your sister sent it to you.",
                "answer": "Te lo",
                "breakdown": "te (to you) + lo (it)",
                "explanation": "'Te lo ha mandato' = sent it to you."
            },
            {
                "italian": "Mi restituisci la macchina? Sì, _____ restituisco domani.",
                "english": "Will you return the car to me? Yes, I'll return it to you tomorrow.",
                "answer": "te la",
                "breakdown": "te (to you) + la (it)",
                "explanation": "'Te la restituisco' = I'll return it to you."
            },
            # Additional glielo/gliela/glieli/gliele examples
            {
                "italian": "Hai portato il documento al direttore? Sì, _____ ho portato stamattina.",
                "english": "Did you bring the document to the director? Yes, I brought it to him this morning.",
                "answer": "glielo",
                "breakdown": "glie (to him) + lo (it)",
                "explanation": "'Glielo ho portato' = I brought it to him."
            },
            {
                "italian": "Hai mandato l'email alla professoressa? Sì, _____ ho mandata ieri.",
                "english": "Did you send the email to the professor? Yes, I sent it to her yesterday.",
                "answer": "gliela",
                "breakdown": "glie (to her) + la (it)",
                "explanation": "'Gliela ho mandata' = I sent it to her."
            },
            {
                "italian": "Hai consegnato i compiti all'insegnante? Sì, _____ ho consegnati.",
                "english": "Did you turn in the homework to the teacher? Yes, I turned it in to him/her.",
                "answer": "glieli",
                "breakdown": "glie (to him/her) + li (them)",
                "explanation": "'Glieli ho consegnati' = I turned them in to him/her."
            },
            {
                "italian": "Hai raccontato le notizie a tua madre? Sì, _____ ho raccontate.",
                "english": "Did you tell the news to your mother? Yes, I told it to her.",
                "answer": "gliele",
                "breakdown": "glie (to her) + le (them)",
                "explanation": "'Gliele ho raccontate' = I told them to her."
            },
            {
                "italian": "Devi spiegare il problema al capo? Sì, _____ devo spiegare.",
                "english": "Do you have to explain the problem to the boss? Yes, I have to explain it to him.",
                "answer": "glielo",
                "breakdown": "glie (to him) + lo (it)",
                "explanation": "'Glielo devo spiegare' = I have to explain it to him."
            },
            {
                "italian": "Vuoi mostrare la foto ai nonni? Sì, _____ voglio mostrare.",
                "english": "Do you want to show the photo to the grandparents? Yes, I want to show it to them.",
                "answer": "gliela",
                "breakdown": "glie (to them) + la (it)",
                "explanation": "'Gliela voglio mostrare' = I want to show it to them."
            },
            {
                "italian": "Hai preparato i panini per i bambini? Sì, _____ ho preparati.",
                "english": "Did you prepare the sandwiches for the children? Yes, I prepared them for them.",
                "answer": "glieli",
                "breakdown": "glie (to them) + li (them)",
                "explanation": "'Glieli ho preparati' = I prepared them for them."
            },
            {
                "italian": "Hai comprato le scarpe a tua figlia? Sì, _____ ho comprate.",
                "english": "Did you buy the shoes for your daughter? Yes, I bought them for her.",
                "answer": "gliele",
                "breakdown": "glie (to her) + le (them)",
                "explanation": "'Gliele ho comprate' = I bought them for her."
            },
            # Additional ce lo/la/li/le examples
            {
                "italian": "Chi vi ha dato questo consiglio? _____ ha dato il professore.",
                "english": "Who gave you this advice? The professor gave it to us.",
                "answer": "Ce lo",
                "breakdown": "ce (to us) + lo (it)",
                "explanation": "'Ce lo ha dato' = gave it to us."
            },
            {
                "italian": "Vi hanno prestato la macchina? Sì, _____ hanno prestata.",
                "english": "Did they lend you the car? Yes, they lent it to us.",
                "answer": "ce la",
                "breakdown": "ce (to us) + la (it)",
                "explanation": "'Ce la hanno prestata' = they lent it to us."
            },
            {
                "italian": "Vi hanno restituito i documenti? Sì, _____ hanno restituiti.",
                "english": "Did they return the documents to you? Yes, they returned them to us.",
                "answer": "ce li",
                "breakdown": "ce (to us) + li (them)",
                "explanation": "'Ce li hanno restituiti' = they returned them to us."
            },
            {
                "italian": "Vi hanno mandato le istruzioni? Sì, _____ hanno mandate ieri.",
                "english": "Did they send you the instructions? Yes, they sent them to us yesterday.",
                "answer": "ce le",
                "breakdown": "ce (to us) + le (them)",
                "explanation": "'Ce le hanno mandate' = they sent them to us."
            },
            # Additional ve lo/la/li/le examples
            {
                "italian": "Chi vi ha consigliato questo ristorante? _____ ha consigliato Marco.",
                "english": "Who recommended this restaurant to you? Marco recommended it to you.",
                "answer": "Ve lo",
                "breakdown": "ve (to you pl) + lo (it)",
                "explanation": "'Ve lo ha consigliato' = recommended it to you."
            },
            {
                "italian": "Vi hanno mostrato la strada? Sì, _____ hanno mostrata.",
                "english": "Did they show you the way? Yes, they showed it to us.",
                "answer": "ve la",
                "breakdown": "ve (to you pl) + la (it)",
                "explanation": "'Ve la hanno mostrata' = they showed it to you."
            },
            {
                "italian": "Vi hanno portato i fiori? Sì, _____ hanno portati.",
                "english": "Did they bring you the flowers? Yes, they brought them to you.",
                "answer": "ve li",
                "breakdown": "ve (to you pl) + li (them)",
                "explanation": "'Ve li hanno portati' = they brought them to you."
            },
            {
                "italian": "Vi hanno spedito le cartoline? Sì, _____ hanno spedite.",
                "english": "Did they send you the postcards? Yes, they sent them to you.",
                "answer": "ve le",
                "breakdown": "ve (to you pl) + le (them)",
                "explanation": "'Ve le hanno spedite' = they sent them to you."
            },
            # More mixed examples
            {
                "italian": "Puoi prestarmi la tua penna? Sì, _____ presto.",
                "english": "Can you lend me your pen? Yes, I'll lend it to you.",
                "answer": "te la",
                "breakdown": "te (to you) + la (it)",
                "explanation": "'Te la presto' = I'll lend it to you."
            },
            {
                "italian": "Mi spieghi questa regola? Sì, _____ spiego subito.",
                "english": "Will you explain this rule to me? Yes, I'll explain it to you right away.",
                "answer": "te la",
                "breakdown": "te (to you) + la (it)",
                "explanation": "'Te la spiego' = I'll explain it to you."
            },
            {
                "italian": "Chi ti ha insegnato queste canzoni? _____ ha insegnate mia nonna.",
                "english": "Who taught you these songs? My grandmother taught them to me.",
                "answer": "Me le",
                "breakdown": "me (to me) + le (them)",
                "explanation": "'Me le ha insegnate' = taught them to me."
            },
            {
                "italian": "Hai presentato il nuovo collega ai tuoi amici? Sì, _____ ho presentato.",
                "english": "Did you introduce the new colleague to your friends? Yes, I introduced him to them.",
                "answer": "glielo",
                "breakdown": "glie (to them) + lo (him)",
                "explanation": "'Glielo ho presentato' = I introduced him to them."
            },
            {
                "italian": "Posso chiederti un favore? Sì, _____ puoi chiedere.",
                "english": "Can I ask you a favor? Yes, you can ask it of me.",
                "answer": "me lo",
                "breakdown": "me (to me) + lo (it)",
                "explanation": "'Me lo puoi chiedere' = you can ask it of me."
            },
            {
                "italian": "Devo portare questi documenti al direttore? Sì, _____ devi portare.",
                "english": "Do I have to bring these documents to the director? Yes, you have to bring them to him.",
                "answer": "glieli",
                "breakdown": "glie (to him) + li (them)",
                "explanation": "'Glieli devi portare' = you have to bring them to him."
            },
            {
                "italian": "Vuoi dire la verità ai tuoi genitori? Sì, _____ voglio dire.",
                "english": "Do you want to tell the truth to your parents? Yes, I want to tell it to them.",
                "answer": "gliela",
                "breakdown": "glie (to them) + la (it)",
                "explanation": "'Gliela voglio dire' = I want to tell it to them."
            },
            {
                "italian": "Mi fai vedere le tue foto? Sì, _____ faccio vedere.",
                "english": "Will you show me your photos? Yes, I'll show them to you.",
                "answer": "te le",
                "breakdown": "te (to you) + le (them)",
                "explanation": "'Te le faccio vedere' = I'll show them to you."
            },
            # With imperatives - more examples
            {
                "italian": "Devo mandare la lettera a Paolo? Sì, _____ !",
                "english": "Should I send the letter to Paolo? Yes, send it to him!",
                "answer": "Mandagliela",
                "breakdown": "manda + glie (to him) + la (it)",
                "explanation": "'Mandagliela!' = Send it to him! Imperative with attached pronouns."
            },
            {
                "italian": "Devo comprare il regalo per Maria? Sì, _____ !",
                "english": "Should I buy the gift for Maria? Yes, buy it for her!",
                "answer": "Compraglielo",
                "breakdown": "compra + glie (to her) + lo (it)",
                "explanation": "'Compraglielo!' = Buy it for her!"
            },
            {
                "italian": "Devo dire queste cose ai miei amici? Sì, _____ !",
                "english": "Should I tell these things to my friends? Yes, tell them to them!",
                "answer": "Digliele",
                "breakdown": "di' + glie (to them) + le (them)",
                "explanation": "'Digliele!' = Tell them to them! With imperative 'di' + glielo."
            },
            {
                "italian": "Devo portare i documenti al professore? Sì, _____ !",
                "english": "Should I bring the documents to the professor? Yes, bring them to him!",
                "answer": "Portaglieli",
                "breakdown": "porta + glie (to him) + li (them)",
                "explanation": "'Portaglieli!' = Bring them to him!"
            },
            {
                "italian": "Devo mostrare la mia tesi alla professoressa? Sì, _____ !",
                "english": "Should I show my thesis to the professor? Yes, show it to her!",
                "answer": "Mostragliela",
                "breakdown": "mostra + glie (to her) + la (it)",
                "explanation": "'Mostragliela!' = Show it to her!"
            },
            # Negative imperatives
            {
                "italian": "Devo dire il segreto a Marco? No, non _____ !",
                "english": "Should I tell the secret to Marco? No, don't tell it to him!",
                "answer": "diglielo",
                "breakdown": "non di' + glie + lo",
                "explanation": "'Non diglielo!' = Don't tell it to him! Negative imperative with pronouns."
            },
            {
                "italian": "Devo dare le chiavi a Luca? No, non _____ !",
                "english": "Should I give the keys to Luca? No, don't give them to him!",
                "answer": "dargliele",
                "breakdown": "non dare + glie + le",
                "explanation": "'Non dargliele!' = Don't give them to him!"
            },
            # More everyday examples
            {
                "italian": "Hai lasciato il messaggio a Carla? Sì, _____ ho lasciato.",
                "english": "Did you leave the message for Carla? Yes, I left it for her.",
                "answer": "glielo",
                "breakdown": "glie (to her) + lo (it)",
                "explanation": "'Glielo ho lasciato' = I left it for her."
            },
            {
                "italian": "Ci hanno dato le informazioni? Sì, _____ hanno date.",
                "english": "Did they give us the information? Yes, they gave it to us.",
                "answer": "ce le",
                "breakdown": "ce (to us) + le (them)",
                "explanation": "'Ce le hanno date' = they gave them to us."
            },
            {
                "italian": "Ti hanno chiesto il numero di telefono? Sì, _____ hanno chiesto.",
                "english": "Did they ask you for your phone number? Yes, they asked me for it.",
                "answer": "me lo",
                "breakdown": "me (to me) + lo (it)",
                "explanation": "'Me lo hanno chiesto' = they asked me for it."
            },
            {
                "italian": "Vi hanno offerto il caffè? Sì, _____ hanno offerto.",
                "english": "Did they offer you coffee? Yes, they offered it to us.",
                "answer": "ce lo",
                "breakdown": "ce (to us) + lo (it)",
                "explanation": "'Ce lo hanno offerto' = they offered it to us."
            },
            {
                "italian": "Mi porti i giornali? Sì, _____ porto.",
                "english": "Will you bring me the newspapers? Yes, I'll bring them to you.",
                "answer": "te li",
                "breakdown": "te (to you) + li (them)",
                "explanation": "'Te li porto' = I'll bring them to you."
            },
            {
                "italian": "Hai scritto la lettera ai tuoi zii? Sì, _____ ho scritta.",
                "english": "Did you write the letter to your uncles? Yes, I wrote it to them.",
                "answer": "gliela",
                "breakdown": "glie (to them) + la (it)",
                "explanation": "'Gliela ho scritta' = I wrote it to them."
            },
            {
                "italian": "Mi hai preparato la colazione? Sì, _____ ho preparata.",
                "english": "Did you prepare breakfast for me? Yes, I prepared it for you.",
                "answer": "te la",
                "breakdown": "te (to you) + la (it)",
                "explanation": "'Te la ho preparata' = I prepared it for you."
            },
            {
                "italian": "Chi vi ha insegnato l'italiano? _____ ha insegnato la professoressa Rossi.",
                "english": "Who taught you Italian? Professor Rossi taught it to us.",
                "answer": "Ce lo",
                "breakdown": "ce (to us) + lo (it)",
                "explanation": "'Ce lo ha insegnato' = taught it to us."
            },
            {
                "italian": "Devo ripetere le istruzioni ai ragazzi? Sì, _____ devi ripetere.",
                "english": "Do I have to repeat the instructions to the kids? Yes, you have to repeat them to them.",
                "answer": "gliele",
                "breakdown": "glie (to them) + le (them)",
                "explanation": "'Gliele devi ripetere' = you have to repeat them to them."
            }
        ]

        selected = random.sample(examples, min(count, len(examples)))
        questions = []

        for item in selected:
            # Combined pronoun forms for choices
            combined = ["me lo", "te la", "glielo", "gliela", "glieli", "gliele",
                       "ce li", "ce la", "ve li", "ve la", "me la", "te lo",
                       "Me le", "Ce la", "Ve li", "mettitelo", "te le", "Daglielo"]

            choices = [item["answer"]]
            wrong_choices = [c for c in combined if c.lower() != item["answer"].lower()]
            choices.extend(random.sample(wrong_choices, min(3, len(wrong_choices))))
            random.shuffle(choices)

            questions.append({
                "question": item["italian"],
                "answer": item["answer"],
                "type": "multiple_choice",
                "choices": choices,
                "hint": f"{item['english']} | {item['breakdown']}",
                "explanation": item["explanation"]
            })

        return questions

    def generate_subjunctive_past(self, count: int = 10) -> List[Dict]:
        """
        Generate subjunctive past (congiuntivo passato) practice for B1 level.
        Structure: avere/essere (present subjunctive) + past participle
        Used after same triggers as present subjunctive, but for past actions.
        """

        examples = [
            {
                "italian": "Penso che lui _____ già partito.",
                "english": "I think that he has already left.",
                "answer": "sia",
                "full": "sia partito",
                "explanation": "Subjunctive past: essere (present subjunctive) + past participle. 'Sia partito' = has left. Partire uses essere."
            },
            {
                "italian": "Credo che loro _____ mangiato troppo.",
                "english": "I believe that they have eaten too much.",
                "answer": "abbiano",
                "full": "abbiano mangiato",
                "explanation": "Subjunctive past: avere (present subjunctive) + past participle. 'Abbiano mangiato' = have eaten."
            },
            {
                "italian": "Spero che tu _____ capito la lezione.",
                "english": "I hope that you understood the lesson.",
                "answer": "abbia",
                "full": "abbia capito",
                "explanation": "Subjunctive past: 'abbia capito' = understood/have understood. Used after 'spero che'."
            },
            {
                "italian": "Dubito che voi _____ finito il lavoro.",
                "english": "I doubt that you have finished the work.",
                "answer": "abbiate",
                "full": "abbiate finito",
                "explanation": "Subjunctive past: 'abbiate finito' = have finished (voi form)."
            },
            {
                "italian": "È possibile che lei _____ uscita.",
                "english": "It's possible that she went out.",
                "answer": "sia",
                "full": "sia uscita",
                "explanation": "Subjunctive past: 'sia uscita' = went out/has gone out. Uscire uses essere."
            },
            {
                "italian": "Non credo che noi _____ visto quel film.",
                "english": "I don't think that we saw that film.",
                "answer": "abbiamo",
                "full": "abbiamo visto",
                "explanation": "Subjunctive past: 'abbiamo visto' = saw/have seen (noi form)."
            },
            {
                "italian": "Spero che Maria _____ arrivata bene.",
                "english": "I hope that Maria arrived safely.",
                "answer": "sia",
                "full": "sia arrivata",
                "explanation": "Subjunctive past: 'sia arrivata' = arrived/has arrived (feminine)."
            },
            {
                "italian": "Temo che loro non _____ venuti.",
                "english": "I fear that they didn't come.",
                "answer": "siano",
                "full": "siano venuti",
                "explanation": "Subjunctive past negative: 'non siano venuti' = didn't come. Venire uses essere."
            },
            {
                "italian": "Penso che _____ stato un errore.",
                "english": "I think that it was a mistake.",
                "answer": "sia",
                "full": "sia stato",
                "explanation": "Subjunctive past of essere: 'sia stato' = was/has been."
            },
            {
                "italian": "È strano che tu non _____ ricevuto la lettera.",
                "english": "It's strange that you didn't receive the letter.",
                "answer": "abbia",
                "full": "abbia ricevuto",
                "explanation": "Subjunctive past: 'non abbia ricevuto' = didn't receive."
            }
        ]

        selected = random.sample(examples, min(count, len(examples)))
        questions = []

        for item in selected:
            forms = ["sia", "abbia", "siano", "abbiano", "abbiamo", "abbiate", "siamo", "siate"]

            choices = [item["answer"]]
            wrong_choices = [f for f in forms if f != item["answer"]]
            choices.extend(random.sample(wrong_choices, min(3, len(wrong_choices))))
            random.shuffle(choices)

            questions.append({
                "question": item["italian"],
                "answer": item["answer"],
                "type": "multiple_choice",
                "choices": choices,
                "hint": f"{item['english']} | Full: {item['full']}",
                "explanation": item["explanation"]
            })

        return questions

    def generate_subjunctive_imperfect(self, count: int = 10) -> List[Dict]:
        """
        Generate subjunctive imperfect (congiuntivo imperfetto) for B1 level.
        Used in hypothetical or contrary-to-fact situations.
        Endings: -ssi, -ssi, -sse, -ssimo, -ste, -ssero
        """

        examples = [
            {
                "italian": "Se io _____ ricco, comprerei una casa.",
                "english": "If I were rich, I would buy a house.",
                "answer": "fossi",
                "infinitive": "essere",
                "explanation": "Subjunctive imperfect in 'if' clauses: 'se fossi' = if I were. Essere → fossi."
            },
            {
                "italian": "Vorrei che tu _____ più gentile.",
                "english": "I would like you to be nicer.",
                "answer": "fossi",
                "infinitive": "essere",
                "explanation": "After 'vorrei che' (I would like that), use subjunctive imperfect: 'fossi' = were (tu)."
            },
            {
                "italian": "Se loro _____ tempo, verrebbero con noi.",
                "english": "If they had time, they would come with us.",
                "answer": "avessero",
                "infinitive": "avere",
                "explanation": "Subjunctive imperfect: 'se avessero' = if they had. Avere → avessero."
            },
            {
                "italian": "Credevo che lei _____ italiana.",
                "english": "I thought that she was Italian.",
                "answer": "fosse",
                "infinitive": "essere",
                "explanation": "Subjunctive imperfect after past tense: 'fosse' = was/were (lei). Essere → fosse."
            },
            {
                "italian": "Se noi _____ più soldi, viaggeremmo di più.",
                "english": "If we had more money, we would travel more.",
                "answer": "avessimo",
                "infinitive": "avere",
                "explanation": "Subjunctive imperfect: 'se avessimo' = if we had. Avere → avessimo."
            },
            {
                "italian": "Vorrei che voi _____ più spesso.",
                "english": "I would like you to come more often.",
                "answer": "veniste",
                "infinitive": "venire",
                "explanation": "Subjunctive imperfect: 'veniste' = came/would come (voi). Venire → veniste."
            },
            {
                "italian": "Se tu _____ italiano, capiresti tutto.",
                "english": "If you spoke Italian, you would understand everything.",
                "answer": "parlassi",
                "infinitive": "parlare",
                "explanation": "Subjunctive imperfect: 'se parlassi' = if you spoke. Parlare → parlassi."
            },
            {
                "italian": "Pensavo che loro _____ in vacanza.",
                "english": "I thought that they were on vacation.",
                "answer": "fossero",
                "infinitive": "essere",
                "explanation": "Subjunctive imperfect: 'fossero' = were (loro). After pensavo che."
            },
            {
                "italian": "Se lei _____ la verità, sarebbe meglio.",
                "english": "If she told the truth, it would be better.",
                "answer": "dicesse",
                "infinitive": "dire",
                "explanation": "Subjunctive imperfect: 'se dicesse' = if she told. Dire → dicesse."
            },
            {
                "italian": "Speravo che voi _____ venire alla festa.",
                "english": "I hoped that you could come to the party.",
                "answer": "poteste",
                "infinitive": "potere",
                "explanation": "Subjunctive imperfect: 'poteste' = could (voi). Potere → poteste."
            }
        ]

        selected = random.sample(examples, min(count, len(examples)))
        questions = []

        for item in selected:
            forms = ["fossi", "fosse", "fossero", "fossimo", "avessi", "avesse", "avessero",
                    "avessimo", "parlassi", "parlasse", "veniste", "dicesse", "poteste"]

            choices = [item["answer"]]
            wrong_choices = [f for f in forms if f != item["answer"]]
            choices.extend(random.sample(wrong_choices, min(3, len(wrong_choices))))
            random.shuffle(choices)

            questions.append({
                "question": item["italian"],
                "answer": item["answer"],
                "type": "multiple_choice",
                "choices": choices,
                "hint": item["english"],
                "explanation": item["explanation"]
            })

        return questions

    def generate_subjunctive_past_perfect(self, count: int = 10) -> List[Dict]:
        """
        Generate subjunctive past perfect (congiuntivo trapassato) for B1 level.
        Structure: avere/essere (subjunctive imperfect) + past participle
        Used for hypothetical past situations or reported thoughts about past.
        """

        examples = [
            {
                "italian": "Se io _____ saputo, sarei venuto.",
                "english": "If I had known, I would have come.",
                "answer": "avessi",
                "full": "avessi saputo",
                "explanation": "Subjunctive past perfect in 'if' clauses: avere/essere (imperfect subjunctive) + participle. 'Avessi saputo' = had known."
            },
            {
                "italian": "Pensavo che loro _____ già partiti.",
                "english": "I thought that they had already left.",
                "answer": "fossero",
                "full": "fossero partiti",
                "explanation": "Subjunctive past perfect: 'fossero partiti' = had left. After pensavo che (past tense)."
            },
            {
                "italian": "Se tu _____ studiato, avresti passato l'esame.",
                "english": "If you had studied, you would have passed the exam.",
                "answer": "avessi",
                "full": "avessi studiato",
                "explanation": "Subjunctive past perfect: 'se avessi studiato' = if you had studied."
            },
            {
                "italian": "Credevo che lei _____ già arrivata.",
                "english": "I believed that she had already arrived.",
                "answer": "fosse",
                "full": "fosse arrivata",
                "explanation": "Subjunctive past perfect: 'fosse arrivata' = had arrived (feminine)."
            },
            {
                "italian": "Se noi _____ andati, ci saremmo divertiti.",
                "english": "If we had gone, we would have had fun.",
                "answer": "fossimo",
                "full": "fossimo andati",
                "explanation": "Subjunctive past perfect: 'se fossimo andati' = if we had gone."
            },
            {
                "italian": "Speravo che voi _____ finito il lavoro.",
                "english": "I hoped that you had finished the work.",
                "answer": "aveste",
                "full": "aveste finito",
                "explanation": "Subjunctive past perfect: 'aveste finito' = had finished (voi)."
            },
            {
                "italian": "Se lui _____ venuto, sarebbe stato bello.",
                "english": "If he had come, it would have been nice.",
                "answer": "fosse",
                "full": "fosse venuto",
                "explanation": "Subjunctive past perfect: 'se fosse venuto' = if he had come."
            },
            {
                "italian": "Pensavo che tu _____ capito tutto.",
                "english": "I thought that you had understood everything.",
                "answer": "avessi",
                "full": "avessi capito",
                "explanation": "Subjunctive past perfect: 'avessi capito' = had understood."
            },
            {
                "italian": "Se loro _____ stati qui, li avreste visti.",
                "english": "If they had been here, you would have seen them.",
                "answer": "fossero",
                "full": "fossero stati",
                "explanation": "Subjunctive past perfect: 'se fossero stati' = if they had been."
            },
            {
                "italian": "Dubitavo che lei _____ mangiato.",
                "english": "I doubted that she had eaten.",
                "answer": "avesse",
                "full": "avesse mangiato",
                "explanation": "Subjunctive past perfect: 'avesse mangiato' = had eaten (lei)."
            }
        ]

        selected = random.sample(examples, min(count, len(examples)))
        questions = []

        for item in selected:
            forms = ["avessi", "avesse", "avessero", "avessimo", "aveste",
                    "fossi", "fosse", "fossero", "fossimo", "foste"]

            choices = [item["answer"]]
            wrong_choices = [f for f in forms if f != item["answer"]]
            choices.extend(random.sample(wrong_choices, min(3, len(wrong_choices))))
            random.shuffle(choices)

            questions.append({
                "question": item["italian"],
                "answer": item["answer"],
                "type": "multiple_choice",
                "choices": choices,
                "hint": f"{item['english']} | Full: {item['full']}",
                "explanation": item["explanation"]
            })

        return questions

    def generate_passato_remoto(self, count: int = 10) -> List[Dict]:
        """
        Generate passato remoto practice for B2 level.
        Historical/literary past tense, rarely used in conversation.
        Common in written Italian, literature, and formal contexts.
        """

        examples = [
            {
                "italian": "Dante _____ la Divina Commedia nel 1300.",
                "english": "Dante wrote the Divine Comedy in 1300.",
                "answer": "scrisse",
                "infinitive": "scrivere",
                "explanation": "Passato remoto: 'scrisse' = wrote. Used for distant historical events. Scrivere is irregular."
            },
            {
                "italian": "Cristoforo Colombo _____ in America nel 1492.",
                "english": "Christopher Columbus arrived in America in 1492.",
                "answer": "arrivò",
                "infinitive": "arrivare",
                "explanation": "Passato remoto: 'arrivò' = arrived. Regular -are verb ending: -ò (lui/lei)."
            },
            {
                "italian": "I Romani _____ un grande impero.",
                "english": "The Romans built a great empire.",
                "answer": "costruirono",
                "infinitive": "costruire",
                "explanation": "Passato remoto: 'costruirono' = built (they). Regular -ire verb: -irono (loro)."
            },
            {
                "italian": "Leonardo da Vinci _____ nel 1519.",
                "english": "Leonardo da Vinci died in 1519.",
                "answer": "morì",
                "infinitive": "morire",
                "explanation": "Passato remoto: 'morì' = died. Used for biographical/historical facts."
            },
            {
                "italian": "I soldati _____ coraggiosamente.",
                "english": "The soldiers fought courageously.",
                "answer": "combatterono",
                "infinitive": "combattere",
                "explanation": "Passato remoto: 'combatterono' = fought. Regular -ere verb: -erono (loro)."
            },
            {
                "italian": "Giuseppe Verdi _____ molte opere famose.",
                "english": "Giuseppe Verdi composed many famous operas.",
                "answer": "compose",
                "infinitive": "comporre",
                "explanation": "Passato remoto irregular: 'compose' = composed. Comporre has irregular passato remoto."
            },
            {
                "italian": "Il re _____ la guerra.",
                "english": "The king declared war.",
                "answer": "dichiarò",
                "infinitive": "dichiarare",
                "explanation": "Passato remoto: 'dichiarò' = declared. Regular -are verb."
            },
            {
                "italian": "Gli esploratori _____ nuove terre.",
                "english": "The explorers discovered new lands.",
                "answer": "scoprirono",
                "infinitive": "scoprire",
                "explanation": "Passato remoto: 'scoprirono' = discovered (they)."
            },
            {
                "italian": "Giulio Cesare _____ 'Veni, vidi, vici'.",
                "english": "Julius Caesar said 'I came, I saw, I conquered'.",
                "answer": "disse",
                "infinitive": "dire",
                "explanation": "Passato remoto irregular: 'disse' = said. Dire has irregular forms."
            },
            {
                "italian": "La regina _____ per molti anni.",
                "english": "The queen reigned for many years.",
                "answer": "regnò",
                "infinitive": "regnare",
                "explanation": "Passato remoto: 'regnò' = reigned. Regular -are verb."
            }
        ]

        selected = random.sample(examples, min(count, len(examples)))
        questions = []

        for item in selected:
            # Passato remoto forms for choices
            forms = ["scrisse", "arrivò", "costruirono", "morì", "combatterono",
                    "compose", "dichiarò", "scoprirono", "disse", "regnò",
                    "fu", "fece", "vide", "venne", "nacque"]

            choices = [item["answer"]]
            wrong_choices = [f for f in forms if f != item["answer"]]
            choices.extend(random.sample(wrong_choices, min(3, len(wrong_choices))))
            random.shuffle(choices)

            questions.append({
                "question": item["italian"],
                "answer": item["answer"],
                "type": "multiple_choice",
                "choices": choices,
                "hint": f"{item['english']} | {item['infinitive']}",
                "explanation": item["explanation"]
            })

        return questions

    def generate_relative_pronouns(self, count: int = 10) -> List[Dict]:
        """
        Generate relative pronouns practice for B2 level.
        che, cui, il quale/la quale/i quali/le quali
        """

        examples = [
            {
                "italian": "La ragazza _____ ho incontrato è molto gentile.",
                "english": "The girl that I met is very kind.",
                "answer": "che",
                "explanation": "'Che' is the most common relative pronoun (that/who/which). Used for subjects and direct objects."
            },
            {
                "italian": "Il libro di _____ ti ho parlato è interessante.",
                "english": "The book that I told you about is interesting.",
                "answer": "cui",
                "explanation": "'Di cui' = about which/whom. 'Cui' is used after prepositions (di, a, con, per, etc.)."
            },
            {
                "italian": "La persona a _____ ho scritto non ha risposto.",
                "english": "The person to whom I wrote didn't respond.",
                "answer": "cui",
                "explanation": "'A cui' = to whom/which. Always use 'cui' after prepositions."
            },
            {
                "italian": "Il film _____ abbiamo visto era bellissimo.",
                "english": "The film that we saw was beautiful.",
                "answer": "che",
                "explanation": "'Che' for direct objects. The film (that) we saw."
            },
            {
                "italian": "La casa nella _____ abito è antica.",
                "english": "The house in which I live is old.",
                "answer": "quale",
                "explanation": "'Nella quale' = in which. Can use 'quale' after prepositions for emphasis. Also: 'in cui' works."
            },
            {
                "italian": "Gli amici con _____ esco sono simpatici.",
                "english": "The friends with whom I go out are nice.",
                "answer": "cui",
                "explanation": "'Con cui' = with whom. 'Cui' after all prepositions."
            },
            {
                "italian": "_____ studia molto, impara di più.",
                "english": "Those who study a lot, learn more.",
                "answer": "Chi",
                "explanation": "'Chi' = he/she who, those who. Refers to people in general statements."
            },
            {
                "italian": "Il ragazzo _____ padre è medico studia medicina.",
                "english": "The boy whose father is a doctor studies medicine.",
                "answer": "il cui",
                "explanation": "'Il cui' = whose (masculine). Agreement: il cui padre, la cui madre, i cui genitori, le cui sorelle."
            },
            {
                "italian": "Prendi tutto _____ vuoi.",
                "english": "Take everything that you want.",
                "answer": "quello che",
                "explanation": "'Quello che' or 'ciò che' = what/that which. For abstract things."
            },
            {
                "italian": "La città per _____ passo ogni giorno è Roma.",
                "english": "The city through which I pass every day is Rome.",
                "answer": "cui",
                "explanation": "'Per cui' = through which/for which. Cui after prepositions."
            }
        ]

        selected = random.sample(examples, min(count, len(examples)))
        questions = []

        for item in selected:
            choices_pool = ["che", "cui", "quale", "Chi", "il cui", "quello che", "la quale", "i quali"]

            choices = [item["answer"]]
            wrong_choices = [c for c in choices_pool if c != item["answer"]]
            choices.extend(random.sample(wrong_choices, min(3, len(wrong_choices))))
            random.shuffle(choices)

            questions.append({
                "question": item["italian"],
                "answer": item["answer"],
                "type": "multiple_choice",
                "choices": choices,
                "hint": item["english"],
                "explanation": item["explanation"]
            })

        return questions

    def generate_impersonal_si(self, count: int = 10) -> List[Dict]:
        """
        Generate impersonal si practice for B2 level.
        Si + verb for general statements: si dice = one says/it is said
        Different from si passivante.
        """

        examples = [
            {
                "italian": "In Italia _____ parla italiano.",
                "english": "In Italy, one speaks Italian / Italian is spoken.",
                "answer": "si",
                "explanation": "Impersonal 'si' + third person singular verb. 'Si parla' = one speaks/people speak."
            },
            {
                "italian": "_____ dice che Roma è bellissima.",
                "english": "They say that Rome is beautiful.",
                "answer": "Si",
                "explanation": "'Si dice' = it is said/people say/they say. Common impersonal construction."
            },
            {
                "italian": "Come _____ fa a cucinare la pasta?",
                "english": "How does one cook pasta?",
                "answer": "si",
                "explanation": "'Come si fa' = how does one do/make. Impersonal instruction question."
            },
            {
                "italian": "Non _____ può fumare qui.",
                "english": "One cannot smoke here.",
                "answer": "si",
                "explanation": "'Non si può' = one cannot/you cannot. Impersonal si with modal verbs."
            },
            {
                "italian": "_____ mangia bene in questo ristorante.",
                "english": "One eats well in this restaurant.",
                "answer": "Si",
                "explanation": "'Si mangia' = one eats/people eat. General statement."
            },
            {
                "italian": "_____ deve sempre essere cortesi.",
                "english": "One must always be polite.",
                "answer": "Si",
                "explanation": "'Si deve' = one must. With dovere, essere becomes plural: 'essere cortesi'."
            },
            {
                "italian": "_____ sa che Dante era italiano.",
                "english": "Everyone knows that Dante was Italian.",
                "answer": "Si",
                "explanation": "'Si sa' = everyone knows/it is known. Common expression."
            },
            {
                "italian": "_____ vive meglio in campagna.",
                "english": "One lives better in the countryside.",
                "answer": "Si",
                "explanation": "'Si vive' = one lives. Impersonal statement about general experience."
            },
            {
                "italian": "Come _____ scrive questa parola?",
                "english": "How does one write this word?",
                "answer": "si",
                "explanation": "'Come si scrive' = how is it written/how do you write. Common question."
            },
            {
                "italian": "_____ pensa che sia vero.",
                "english": "One thinks that it's true.",
                "answer": "Si",
                "explanation": "'Si pensa' = one thinks/it is thought. Often followed by subjunctive."
            }
        ]

        selected = random.sample(examples, min(count, len(examples)))
        questions = []

        for item in selected:
            choices = [item["answer"], "ci", "ne", "lo", "la"]
            random.shuffle(choices)

            questions.append({
                "question": item["italian"],
                "answer": item["answer"],
                "type": "multiple_choice",
                "choices": choices,
                "hint": item["english"],
                "explanation": item["explanation"]
            })

        return questions

    def generate_unreal_past(self, count: int = 10) -> List[Dict]:
        """
        Generate unreal past conditionals for B2 level.
        Third conditional: If X had happened, Y would have happened.
        Structure: Se + subjunctive past perfect, conditional past
        """

        examples = [
            {
                "italian": "Se _____ studiato, avresti passato l'esame.",
                "english": "If you had studied, you would have passed the exam.",
                "answer": "avessi",
                "full": "avessi studiato",
                "explanation": "Unreal past: Se + subjunctive past perfect + conditional past. 'Se avessi studiato' = if you had studied (but you didn't)."
            },
            {
                "italian": "Se _____ stato lì, ti avrei aiutato.",
                "english": "If I had been there, I would have helped you.",
                "answer": "fossi",
                "full": "fossi stato",
                "explanation": "Unreal past: 'Se fossi stato' = if I had been. Hypothetical past situation that didn't happen."
            },
            {
                "italian": "Se lei _____ venuta, si sarebbe divertita.",
                "english": "If she had come, she would have had fun.",
                "answer": "fosse",
                "full": "fosse venuta",
                "explanation": "Unreal past: 'Se fosse venuta' = if she had come (but she didn't come)."
            },
            {
                "italian": "Se noi _____ saputo, avremmo fatto diversamente.",
                "english": "If we had known, we would have done differently.",
                "answer": "avessimo",
                "full": "avessimo saputo",
                "explanation": "Unreal past: 'Se avessimo saputo' = if we had known. Contrary to fact in the past."
            },
            {
                "italian": "Se voi _____ arrivati prima, avreste visto tutto.",
                "english": "If you had arrived earlier, you would have seen everything.",
                "answer": "foste",
                "full": "foste arrivati",
                "explanation": "Unreal past: 'Se foste arrivati' = if you had arrived (voi form)."
            },
            {
                "italian": "Se loro _____ detto la verità, tutto sarebbe diverso.",
                "english": "If they had told the truth, everything would be different.",
                "answer": "avessero",
                "full": "avessero detto",
                "explanation": "Unreal past: 'Se avessero detto' = if they had told. Result affects present: 'sarebbe diverso'."
            },
            {
                "italian": "Se tu _____ andato, ti saresti annoiato.",
                "english": "If you had gone, you would have been bored.",
                "answer": "fossi",
                "full": "fossi andato",
                "explanation": "Unreal past: 'Se fossi andato' = if you had gone (but you didn't)."
            },
            {
                "italian": "Se io _____ visto il film, te lo avrei detto.",
                "english": "If I had seen the film, I would have told you.",
                "answer": "avessi",
                "full": "avessi visto",
                "explanation": "Unreal past: 'Se avessi visto' = if I had seen (but I didn't see it)."
            },
            {
                "italian": "Se lei _____ partita prima, sarebbe arrivata in tempo.",
                "english": "If she had left earlier, she would have arrived on time.",
                "answer": "fosse",
                "full": "fosse partita",
                "explanation": "Unreal past: 'Se fosse partita' = if she had left (feminine)."
            },
            {
                "italian": "Se noi _____ comprato quella casa, saremmo felici.",
                "english": "If we had bought that house, we would be happy.",
                "answer": "avessimo",
                "full": "avessimo comprato",
                "explanation": "Unreal past with present result: past action affects present state."
            }
        ]

        selected = random.sample(examples, min(count, len(examples)))
        questions = []

        for item in selected:
            forms = ["avessi", "avesse", "avessero", "avessimo", "aveste",
                    "fossi", "fosse", "fossero", "fossimo", "foste"]

            choices = [item["answer"]]
            wrong_choices = [f for f in forms if f != item["answer"]]
            choices.extend(random.sample(wrong_choices, min(3, len(wrong_choices))))
            random.shuffle(choices)

            questions.append({
                "question": item["italian"],
                "answer": item["answer"],
                "type": "multiple_choice",
                "choices": choices,
                "hint": f"{item['english']} | Full: {item['full']}",
                "explanation": item["explanation"]
            })

        return questions

    def generate_comprehensive_subjunctives(self, count: int = 10) -> List[Dict]:
        """
        Generate comprehensive subjunctive review for B2 level.
        Mixed practice of all four subjunctive tenses.
        Tests ability to choose correct tense based on context.
        """

        examples = [
            # Present subjunctive
            {
                "italian": "Penso che lui _____ italiano.",
                "english": "I think that he is Italian.",
                "answer": "sia",
                "tense": "present",
                "explanation": "Present subjunctive after 'penso che' for present/general fact. 'Sia' = is (subjunctive)."
            },
            {
                "italian": "Spero che tu _____ bene.",
                "english": "I hope that you're well.",
                "answer": "stia",
                "tense": "present",
                "explanation": "Present subjunctive: 'spero che tu stia' = I hope you are. Stare → stia."
            },
            # Past subjunctive
            {
                "italian": "Credo che loro _____ già partiti.",
                "english": "I believe that they have already left.",
                "answer": "siano",
                "tense": "past",
                "explanation": "Past subjunctive (congiuntivo passato): 'siano partiti' = have left. Present trigger + past action."
            },
            {
                "italian": "Dubito che lei _____ capito tutto.",
                "english": "I doubt that she understood everything.",
                "answer": "abbia",
                "tense": "past",
                "explanation": "Past subjunctive: 'abbia capito' = understood/has understood. Completed action."
            },
            # Imperfect subjunctive
            {
                "italian": "Vorrei che tu _____ con me.",
                "english": "I would like you to come with me.",
                "answer": "venissi",
                "tense": "imperfect",
                "explanation": "Imperfect subjunctive after 'vorrei che' (conditional). Venire → venissi."
            },
            {
                "italian": "Se io _____ ricco, viaggerei molto.",
                "english": "If I were rich, I would travel a lot.",
                "answer": "fossi",
                "tense": "imperfect",
                "explanation": "Imperfect subjunctive in hypothetical 'if' clause. 'Se fossi' = if I were."
            },
            {
                "italian": "Pensavo che lei _____ qui.",
                "english": "I thought that she was here.",
                "answer": "fosse",
                "tense": "imperfect",
                "explanation": "Imperfect subjunctive after past tense main verb (pensavo). 'Fosse' = was."
            },
            # Past perfect subjunctive
            {
                "italian": "Credevo che tu _____ già mangiato.",
                "english": "I believed that you had already eaten.",
                "answer": "avessi",
                "tense": "past perfect",
                "explanation": "Past perfect subjunctive: 'avessi mangiato' = had eaten. Past main verb + earlier past action."
            },
            {
                "italian": "Se noi _____ saputo, saremmo venuti.",
                "english": "If we had known, we would have come.",
                "answer": "avessimo",
                "tense": "past perfect",
                "explanation": "Past perfect subjunctive in unreal past: 'se avessimo saputo' = if we had known."
            },
            {
                "italian": "Speravo che voi _____ arrivati in tempo.",
                "english": "I hoped that you had arrived on time.",
                "answer": "foste",
                "tense": "past perfect",
                "explanation": "Past perfect subjunctive: 'foste arrivati' = had arrived (voi)."
            },
            # More mixed examples
            {
                "italian": "È possibile che _____ domani.",
                "english": "It's possible that it will rain tomorrow.",
                "answer": "piova",
                "tense": "present",
                "explanation": "Present subjunctive for future possibility. Piovere → piova."
            },
            {
                "italian": "Non credo che _____ la verità ieri.",
                "english": "I don't think they told the truth yesterday.",
                "answer": "abbiano detto",
                "tense": "past",
                "explanation": "Past subjunctive: 'abbiano detto' = told (completed past action)."
            }
        ]

        selected = random.sample(examples, min(count, len(examples)))
        questions = []

        for item in selected:
            # Mix of subjunctive forms across all tenses
            all_forms = ["sia", "abbia", "siano", "abbiano", "stia",
                        "fossi", "avessi", "fosse", "avesse", "venissi",
                        "avessimo", "fossero", "avessero", "foste",
                        "piova", "abbiano detto"]

            choices = [item["answer"]]
            wrong_choices = [f for f in all_forms if f != item["answer"]]
            choices.extend(random.sample(wrong_choices, min(3, len(wrong_choices))))
            random.shuffle(choices)

            questions.append({
                "question": item["italian"],
                "answer": item["answer"],
                "type": "multiple_choice",
                "choices": choices,
                "hint": f"{item['english']} | Tense: {item['tense']} subjunctive",
                "explanation": item["explanation"]
            })

        return questions


if __name__ == "__main__":
    # Test the practice generator
    print("Testing Practice Generator...")
    print()
    
    with ItalianDatabase() as db:
        generator = PracticeGenerator(db)
        
        # Test verb conjugation drill
        print("=== Verb Conjugation Drill ===")
        questions = generator.generate_verb_conjugation_drill("A1", 3)
        for i, q in enumerate(questions, 1):
            print(f"{i}. {q['question']}")
            print(f"   Answer: {q['answer']}")
            print()
        
        # Test vocabulary quiz
        print("=== Vocabulary Quiz ===")
        questions = generator.generate_vocabulary_quiz("A1", 3, "it_to_en")
        for i, q in enumerate(questions, 1):
            print(f"{i}. {q['question']}")
            print(f"   Answer: {q['answer']}")
            print()
