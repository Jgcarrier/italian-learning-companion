"""
Data Import Script
Populates the database with A1 (completed) and A2 (current) curriculum data.
"""

from database import ItalianDatabase

def import_a1_verbs(db: ItalianDatabase):
    """Import core A1 verb conjugations."""
    print("Importing A1 verbs...")
    
    # Regular -ARE verbs (Parlare)
    parlare_presente = [
        ("io", "parlo"), ("tu", "parli"), ("lui_lei", "parla"),
        ("noi", "parliamo"), ("voi", "parlate"), ("loro", "parlano")
    ]
    for person, form in parlare_presente:
        db.add_verb_conjugation("parlare", "to speak", "regular_are", "presente", person, form, "A1")
    
    # Regular -ERE verbs (Vedere)
    vedere_presente = [
        ("io", "vedo"), ("tu", "vedi"), ("lui_lei", "vede"),
        ("noi", "vediamo"), ("voi", "vedete"), ("loro", "vedono")
    ]
    for person, form in vedere_presente:
        db.add_verb_conjugation("vedere", "to see", "regular_ere", "presente", person, form, "A1")
    
    # Regular -IRE verbs (Dormire)
    dormire_presente = [
        ("io", "dormo"), ("tu", "dormi"), ("lui_lei", "dorme"),
        ("noi", "dormiamo"), ("voi", "dormite"), ("loro", "dormono")
    ]
    for person, form in dormire_presente:
        db.add_verb_conjugation("dormire", "to sleep", "regular_ire", "presente", person, form, "A1")
    
    # Regular -ISC verbs (Capire)
    capire_presente = [
        ("io", "capisco"), ("tu", "capisci"), ("lui_lei", "capisce"),
        ("noi", "capiamo"), ("voi", "capite"), ("loro", "capiscono")
    ]
    for person, form in capire_presente:
        db.add_verb_conjugation("capire", "to understand", "regular_isc", "presente", person, form, "A1")
    
    # Irregular verbs - Essere
    essere_presente = [
        ("io", "sono"), ("tu", "sei"), ("lui_lei", "è"),
        ("noi", "siamo"), ("voi", "siete"), ("loro", "sono")
    ]
    for person, form in essere_presente:
        db.add_verb_conjugation("essere", "to be", "irregular", "presente", person, form, "A1")
    
    # Irregular verbs - Avere
    avere_presente = [
        ("io", "ho"), ("tu", "hai"), ("lui_lei", "ha"),
        ("noi", "abbiamo"), ("voi", "avete"), ("loro", "hanno")
    ]
    for person, form in avere_presente:
        db.add_verb_conjugation("avere", "to have", "irregular", "presente", person, form, "A1")
    
    # Irregular verbs - Fare
    fare_presente = [
        ("io", "faccio"), ("tu", "fai"), ("lui_lei", "fa"),
        ("noi", "facciamo"), ("voi", "fate"), ("loro", "fanno")
    ]
    for person, form in fare_presente:
        db.add_verb_conjugation("fare", "to do/make", "irregular", "presente", person, form, "A1")
    
    # Irregular verbs - Andare
    andare_presente = [
        ("io", "vado"), ("tu", "vai"), ("lui_lei", "va"),
        ("noi", "andiamo"), ("voi", "andate"), ("loro", "vanno")
    ]
    for person, form in andare_presente:
        db.add_verb_conjugation("andare", "to go", "irregular", "presente", person, form, "A1")
    
    # Passato Prossimo - common verbs
    # With AVERE
    db.add_verb_conjugation("parlare", "to speak", "regular_are", "passato_prossimo", "io", "parlato", "A1", "avere")
    db.add_verb_conjugation("dormire", "to sleep", "regular_ire", "passato_prossimo", "io", "dormito", "A1", "avere")
    db.add_verb_conjugation("vedere", "to see", "regular_ere", "passato_prossimo", "io", "visto", "A1", "avere")
    db.add_verb_conjugation("fare", "to do/make", "irregular", "passato_prossimo", "io", "fatto", "A1", "avere")
    
    # With ESSERE
    db.add_verb_conjugation("essere", "to be", "irregular", "passato_prossimo", "io", "stato", "A1", "essere")
    db.add_verb_conjugation("andare", "to go", "irregular", "passato_prossimo", "io", "andato", "A1", "essere")
    
    print(f"✓ Imported A1 verbs")

def import_a1_vocabulary(db: ItalianDatabase):
    """Import essential A1 vocabulary."""
    print("Importing A1 vocabulary...")
    
    # Food vocabulary
    food_items = [
        ("caffè", "coffee", "noun", "masculine", "caffè", "food"),
        ("acqua", "water", "noun", "feminine", "acque", "food"),
        ("pane", "bread", "noun", "masculine", "pani", "food"),
        ("pasta", "pasta", "noun", "feminine", "paste", "food"),
        ("carne", "meat", "noun", "feminine", "carni", "food"),
        ("pesce", "fish", "noun", "masculine", "pesci", "food"),
        ("vino", "wine", "noun", "masculine", "vini", "food"),
        ("birra", "beer", "noun", "feminine", "birre", "food"),
        ("formaggio", "cheese", "noun", "masculine", "formaggi", "food"),
        ("prosciutto", "ham", "noun", "masculine", "prosciutti", "food"),
        ("latte", "milk", "noun", "masculine", "latte", "food"),
        ("burro", "butter", "noun", "masculine", "burri", "food"),
        ("uovo", "egg", "noun", "masculine", "uova", "food"),
        ("pomodoro", "tomato", "noun", "masculine", "pomodori", "food"),
        ("insalata", "salad/lettuce", "noun", "feminine", "insalate", "food"),
        ("frutta", "fruit", "noun", "feminine", "frutta", "food"),
        ("verdura", "vegetables", "noun", "feminine", "verdure", "food"),
        ("dolce", "dessert/sweet", "noun", "masculine", "dolci", "food"),
        ("zucchero", "sugar", "noun", "masculine", "zuccheri", "food"),
        ("sale", "salt", "noun", "masculine", "sale", "food"),
        ("olio", "oil", "noun", "masculine", "oli", "food"),
        ("riso", "rice", "noun", "masculine", "risi", "food"),
    ]
    
    for italian, english, word_type, gender, plural, category in food_items:
        db.add_vocabulary(italian, english, word_type, "A1", gender, plural, category)
    
    # Time vocabulary
    time_items = [
        ("giorno", "day", "noun", "masculine", "giorni", "time"),
        ("settimana", "week", "noun", "feminine", "settimane", "time"),
        ("mese", "month", "noun", "masculine", "mesi", "time"),
        ("anno", "year", "noun", "masculine", "anni", "time"),
        ("oggi", "today", "adverb", None, None, "time"),
        ("domani", "tomorrow", "adverb", None, None, "time"),
        ("ieri", "yesterday", "adverb", None, None, "time"),
        ("ora", "hour/now", "noun", "feminine", "ore", "time"),
        ("mattina", "morning", "noun", "feminine", "mattine", "time"),
        ("pomeriggio", "afternoon", "noun", "masculine", "pomeriggi", "time"),
        ("sera", "evening", "noun", "feminine", "sere", "time"),
        ("notte", "night", "noun", "feminine", "notti", "time"),
        ("presto", "early/soon", "adverb", None, None, "time"),
        ("tardi", "late", "adverb", None, None, "time"),
    ]
    
    for item in time_items:
        italian, english, word_type, gender, plural, category = item
        db.add_vocabulary(italian, english, word_type, "A1", gender, plural, category)
    
    # Days of the week
    days = [
        ("lunedì", "Monday"), ("martedì", "Tuesday"), ("mercoledì", "Wednesday"),
        ("giovedì", "Thursday"), ("venerdì", "Friday"), ("sabato", "Saturday"),
        ("domenica", "Sunday")
    ]
    for italian, english in days:
        db.add_vocabulary(italian, english, "noun", "A1", "masculine", italian, "time")
    
    # Months
    months = [
        ("gennaio", "January"), ("febbraio", "February"), ("marzo", "March"),
        ("aprile", "April"), ("maggio", "May"), ("giugno", "June"),
        ("luglio", "July"), ("agosto", "August"), ("settembre", "September"),
        ("ottobre", "October"), ("novembre", "November"), ("dicembre", "December")
    ]
    for italian, english in months:
        db.add_vocabulary(italian, english, "noun", "A1", "masculine", italian, "time")
    
    # Family
    family = [
        ("madre", "mother", "feminine", "madri"),
        ("padre", "father", "masculine", "padri"),
        ("fratello", "brother", "masculine", "fratelli"),
        ("sorella", "sister", "feminine", "sorelle"),
        ("nonno", "grandfather", "masculine", "nonni"),
        ("nonna", "grandmother", "feminine", "nonne"),
        ("figlio", "son", "masculine", "figli"),
        ("figlia", "daughter", "feminine", "figlie"),
        ("zio", "uncle", "masculine", "zii"),
        ("zia", "aunt", "feminine", "zie"),
        ("cugino", "cousin (m)", "masculine", "cugini"),
        ("cugina", "cousin (f)", "feminine", "cugine"),
        ("marito", "husband", "masculine", "mariti"),
        ("moglie", "wife", "feminine", "mogli"),
    ]
    for italian, english, gender, plural in family:
        db.add_vocabulary(italian, english, "noun", "A1", gender, plural, "family")
    
    # Common adjectives
    adjectives = [
        ("buono", "good", "masculine", "buoni"),
        ("cattivo", "bad", "masculine", "cattivi"),
        ("grande", "big/great", "both", "grandi"),
        ("piccolo", "small", "masculine", "piccoli"),
        ("bello", "beautiful", "masculine", "belli"),
        ("brutto", "ugly", "masculine", "brutti"),
        ("nuovo", "new", "masculine", "nuovi"),
        ("vecchio", "old", "masculine", "vecchi"),
        ("giovane", "young", "both", "giovani"),
        ("caldo", "hot/warm", "masculine", "caldi"),
        ("freddo", "cold", "masculine", "freddi"),
        ("lungo", "long", "masculine", "lunghi"),
        ("corto", "short", "masculine", "corti"),
        ("alto", "tall/high", "masculine", "alti"),
        ("basso", "short/low", "masculine", "bassi"),
        ("facile", "easy", "both", "facili"),
        ("difficile", "difficult", "both", "difficili"),
    ]
    for italian, english, gender, plural in adjectives:
        db.add_vocabulary(italian, english, "adjective", "A1", gender, plural, "adjectives")
    
    # Common verbs (infinitives)
    verbs = [
        ("mangiare", "to eat"), ("bere", "to drink"), ("dormire", "to sleep"),
        ("lavorare", "to work"), ("studiare", "to study"), ("parlare", "to speak"),
        ("capire", "to understand"), ("leggere", "to read"), ("scrivere", "to write"),
        ("ascoltare", "to listen"), ("guardare", "to watch"), ("vedere", "to see"),
        ("sentire", "to hear/feel"), ("andare", "to go"), ("venire", "to come"),
        ("partire", "to leave"), ("arrivare", "to arrive"), ("tornare", "to return"),
        ("uscire", "to go out"), ("entrare", "to enter"), ("abitare", "to live"),
    ]
    for italian, english in verbs:
        db.add_vocabulary(italian, english, "verb", "A1", None, None, "verbs")
    
    # Places
    places = [
        ("casa", "house/home", "feminine", "case"),
        ("città", "city", "feminine", "città"),
        ("paese", "village/country", "masculine", "paesi"),
        ("strada", "street/road", "feminine", "strade"),
        ("piazza", "square/plaza", "feminine", "piazze"),
        ("stazione", "station", "feminine", "stazioni"),
        ("aeroporto", "airport", "masculine", "aeroporti"),
        ("albergo", "hotel", "masculine", "alberghi"),
        ("ristorante", "restaurant", "masculine", "ristoranti"),
        ("bar", "bar/café", "masculine", "bar"),
        ("negozio", "shop", "masculine", "negozi"),
        ("mercato", "market", "masculine", "mercati"),
        ("scuola", "school", "feminine", "scuole"),
        ("università", "university", "feminine", "università"),
        ("ospedale", "hospital", "masculine", "ospedali"),
        ("chiesa", "church", "feminine", "chiese"),
        ("museo", "museum", "masculine", "musei"),
        ("cinema", "cinema", "masculine", "cinema"),
        ("teatro", "theater", "masculine", "teatri"),
        ("parco", "park", "masculine", "parchi"),
        ("mare", "sea", "masculine", "mari"),
        ("montagna", "mountain", "feminine", "montagne"),
        ("spiaggia", "beach", "feminine", "spiagge"),
    ]
    for italian, english, gender, plural in places:
        db.add_vocabulary(italian, english, "noun", "A1", gender, plural, "places")
    
    # Common phrases and expressions
    phrases = [
        ("grazie", "thank you"), ("prego", "you're welcome"), ("scusi", "excuse me (formal)"),
        ("per favore", "please"), ("va bene", "okay/all right"), ("certo", "certainly"),
        ("forse", "maybe/perhaps"), ("sempre", "always"), ("mai", "never"),
        ("molto", "very/much"), ("poco", "little/few"), ("troppo", "too much"),
        ("ancora", "still/yet/again"), ("già", "already"), ("subito", "immediately"),
    ]
    for italian, english in phrases:
        db.add_vocabulary(italian, english, "phrase", "A1", None, None, "expressions")
    
    print(f"✓ Imported A1 vocabulary")

def import_a1_topics(db: ItalianDatabase):
    """Import A1 grammar topics you've completed."""
    print("Importing A1 topics...")
    
    topics = [
        ("Present tense regular -ARE verbs", "verbs", "A1", "Regular verb conjugation ending in -are", "Nuovo Espresso 1, Lezione 2", True),
        ("Present tense regular -ERE verbs", "verbs", "A1", "Regular verb conjugation ending in -ere", "Nuovo Espresso 1, Lezione 3", True),
        ("Present tense regular -IRE verbs", "verbs", "A1", "Regular verb conjugation ending in -ire", "Nuovo Espresso 1, Lezione 4", True),
        ("Present tense -ISC verbs", "verbs", "A1", "Regular verbs with -isc- infix (capire type)", "Nuovo Espresso 1, Lezione 4", True),
        ("Irregular verb: essere", "verbs", "A1", "To be - sono, sei, è, siamo, siete, sono", "Nuovo Espresso 1, Lezione 1", True),
        ("Irregular verb: avere", "verbs", "A1", "To have - ho, hai, ha, abbiamo, avete, hanno", "Nuovo Espresso 1, Lezione 1", True),
        ("Irregular verb: fare", "verbs", "A1", "To do/make - faccio, fai, fa, facciamo, fate, fanno", "Nuovo Espresso 1, Lezione 2", True),
        ("Irregular verb: andare", "verbs", "A1", "To go - vado, vai, va, andiamo, andate, vanno", "Nuovo Espresso 1, Lezione 4", True),
        ("Passato prossimo with avere", "verbs", "A1", "Past tense with auxiliary avere", "Nuovo Espresso 1, Lezione 7", True),
        ("Passato prossimo with essere", "verbs", "A1", "Past tense with auxiliary essere", "Nuovo Espresso 1, Lezione 7", True),
        
        ("Definite articles", "articles", "A1", "il, lo, la, i, gli, le", "Nuovo Espresso 1, Lezione 1-2", True),
        ("Indefinite articles", "articles", "A1", "un, uno, una, un'", "Nuovo Espresso 1, Lezione 2", True),
        ("Partitive articles", "articles", "A1", "del, dello, della, dei, degli, delle (some)", "Nuovo Espresso 1, Lezione 6", True),
        
        ("Subject pronouns", "pronouns", "A1", "io, tu, lui/lei, noi, voi, loro", "Nuovo Espresso 1, Lezione 1", True),
        ("Direct object pronouns", "pronouns", "A1", "mi, ti, lo/la, ci, vi, li/le", "Nuovo Espresso 1, Lezione 8", True),
        ("Reflexive pronouns", "pronouns", "A1", "mi, ti, si, ci, vi, si", "Nuovo Espresso 1, Lezione 9", True),
        ("Possessive adjectives", "pronouns", "A1", "mio, tuo, suo, nostro, vostro, loro", "Nuovo Espresso 1, Lezione 10", True),
        
        ("Simple prepositions", "prepositions", "A1", "di, a, da, in, con, su, per, tra/fra", "Nuovo Espresso 1, Lezione 5", True),
        ("Articulated prepositions", "prepositions", "A1", "Preposition + article combinations (del, alla, etc.)", "Nuovo Espresso 1, Lezione 5", True),
        
        ("Noun gender and number", "nouns", "A1", "Masculine/feminine, singular/plural formation", "Nuovo Espresso 1, Lezione 2-3", True),
        ("Adjective agreement", "adjectives", "A1", "Adjectives agree with noun in gender and number", "Nuovo Espresso 1, Lezione 5", True),
    ]
    
    for name, category, level, description, lesson_ref, completed in topics:
        db.add_topic(name, category, level, description, lesson_ref, completed)
    
    print(f"✓ Imported {len(topics)} A1 topics")

def import_a2_topics(db: ItalianDatabase):
    """Import A2 topics you're currently learning."""
    print("Importing A2 topics...")
    
    topics = [
        ("Imperfetto tense", "verbs", "A2", "Imperfect tense for habitual past actions", "Nuovo Espresso 2, Lezione 2", False),
        ("Passato prossimo vs Imperfetto", "verbs", "A2", "When to use each past tense", "Nuovo Espresso 2, Lezione 2", False),
        ("Futuro semplice", "verbs", "A2", "Simple future tense", "Nuovo Espresso 2, Lezione 8", False),
        ("Condizionale presente", "verbs", "A2", "Present conditional for polite requests and hypotheticals", "Nuovo Espresso 2, Lezione 3", False),
        ("Imperativo (tu)", "verbs", "A2", "Informal commands", "Nuovo Espresso 2, Lezione 1", False),
        ("Imperativo (Lei/voi)", "verbs", "A2", "Formal and plural commands", "Nuovo Espresso 2, Lezione 7", False),
        
        ("Pronomi combinati", "pronouns", "A2", "Combined pronouns (me lo, te la, etc.)", "Nuovo Espresso 2, Lezione 6", False),
        ("Pronomi relativi (che/cui)", "pronouns", "A2", "Relative pronouns - that, which, who", "Nuovo Espresso 2, Lezione 4", False),
        
        ("Comparativi", "comparatives", "A2", "More than, less than, as...as", "Nuovo Espresso 2, Lezione 1", False),
        ("Superlativi relativi", "comparatives", "A2", "The most, the least", "Nuovo Espresso 2, Lezione 10", False),
        
        ("Gerundio (stare + gerund)", "verbs", "A2", "Progressive form - stare + -ando/-endo", "Nuovo Espresso 2, Lezione 4", False),
    ]
    
    for name, category, level, description, lesson_ref, completed in topics:
        db.add_topic(name, category, level, description, lesson_ref, completed)
    
    print(f"✓ Imported {len(topics)} A2 topics (current learning)")

def main():
    """Main import function."""
    print("=" * 60)
    print("Italian Learning Companion - Data Import")
    print("=" * 60)
    print()
    
    with ItalianDatabase() as db:
        import_a1_topics(db)
        import_a1_verbs(db)
        import_a1_vocabulary(db)
        import_a2_topics(db)
    
    print()
    print("=" * 60)
    print("✓ All data imported successfully!")
    print("=" * 60)
    print()
    print("You now have:")
    print("  • A1 completed curriculum (verbs, vocabulary, grammar topics)")
    print("  • A2 current topics (ready for practice)")
    print("  • Database ready for tracking your progress")
    print()
    print("Next steps:")
    print("  1. Run 'python src/main.py' to start practicing")
    print("  2. The system will focus on A2 topics you're learning")
    print("  3. It will track weak areas automatically")

if __name__ == "__main__":
    main()
