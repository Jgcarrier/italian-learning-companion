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
    
    def generate_verb_conjugation_drill(self, level: str = "A1", count: int = 10) -> List[Dict]:
        """Generate verb conjugation practice questions."""
        cursor = self.db.conn.cursor()
        
        # Get random verbs from the specified level
        cursor.execute("""
            SELECT DISTINCT infinitive, english, verb_type, tense
            FROM verb_conjugations
            WHERE level = ?
            ORDER BY RANDOM()
            LIMIT ?
        """, (level, count))
        
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
            ("Credo che abbia ragione.", "I believe he/she is right.", "subjunctive"),
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
        def get_participle(infinitive, aux):
            if infinitive == "andare":
                return "andato/a"
            if infinitive.endswith("are"):
                return infinitive[:-3] + "ato"
            elif infinitive.endswith("ere"):
                return infinitive[:-3] + "uto"
            elif infinitive == "finire" or infinitive == "capire" or infinitive == "preferire":
                return infinitive[:-3] + "ito"
            elif infinitive.endswith("ire"):
                return infinitive[:-3] + "ito"
            return infinitive

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
            participle = get_participle(verb, aux)

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
