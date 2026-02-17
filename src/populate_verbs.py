"""
Populate verb_conjugations table with comprehensive Italian verb data.
"""

import sqlite3
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from database import ItalianDatabase

def populate_verb_conjugations(db_path='../data/curriculum.db'):
    """Populate the verb_conjugations table with common Italian verbs."""

    db = ItalianDatabase(db_path)
    cursor = db.conn.cursor()

    # Clear existing verb conjugations (for fresh start)
    print("Clearing existing verb conjugations...")
    cursor.execute("DELETE FROM verb_conjugations")

    # Define common verbs with their conjugations
    # Format: (infinitive, english, verb_type, level)
    verbs_data = [
        # A1 Level - Essential verbs (20 verbs)
        ("essere", "to be", "irregular", "A1"),
        ("avere", "to have", "irregular", "A1"),
        ("fare", "to do/make", "irregular", "A1"),
        ("andare", "to go", "irregular", "A1"),
        ("venire", "to come", "irregular", "A1"),
        ("stare", "to stay/be", "irregular", "A1"),
        ("dire", "to say", "irregular", "A1"),
        ("dare", "to give", "irregular", "A1"),
        ("parlare", "to speak", "regular_are", "A1"),
        ("mangiare", "to eat", "regular_are", "A1"),
        ("studiare", "to study", "regular_are", "A1"),
        ("lavorare", "to work", "regular_are", "A1"),
        ("abitare", "to live", "regular_are", "A1"),
        ("chiamare", "to call", "regular_are", "A1"),
        ("comprare", "to buy", "regular_are", "A1"),
        ("prendere", "to take", "regular_ere", "A1"),
        ("vedere", "to see", "irregular", "A1"),
        ("sapere", "to know", "irregular", "A1"),
        ("potere", "to be able", "irregular", "A1"),
        ("volere", "to want", "irregular", "A1"),

        # A2 Level - Common verbs (30 verbs)
        ("dovere", "to have to", "irregular", "A2"),
        ("uscire", "to go out", "irregular", "A2"),
        ("capire", "to understand", "regular_ire", "A2"),
        ("finire", "to finish", "regular_ire", "A2"),
        ("aprire", "to open", "regular_ire", "A2"),
        ("partire", "to leave", "regular_ire", "A2"),
        ("dormire", "to sleep", "regular_ire", "A2"),
        ("sentire", "to hear/feel", "regular_ire", "A2"),
        ("arrivare", "to arrive", "regular_are", "A2"),
        ("tornare", "to return", "regular_are", "A2"),
        ("guardare", "to watch", "regular_are", "A2"),
        ("ascoltare", "to listen", "regular_are", "A2"),
        ("aspettare", "to wait", "regular_are", "A2"),
        ("pensare", "to think", "regular_are", "A2"),
        ("trovare", "to find", "regular_are", "A2"),
        ("cercare", "to look for", "regular_are", "A2"),
        ("giocare", "to play", "regular_are", "A2"),
        ("lasciare", "to leave", "regular_are", "A2"),
        ("portare", "to bring", "regular_are", "A2"),
        ("ricevere", "to receive", "regular_ere", "A2"),
        ("credere", "to believe", "regular_ere", "A2"),
        ("vendere", "to sell", "regular_ere", "A2"),
        ("leggere", "to read", "irregular", "A2"),
        ("scrivere", "to write", "irregular", "A2"),
        ("bere", "to drink", "irregular", "A2"),
        ("conoscere", "to know", "irregular", "A2"),
        ("mettere", "to put", "irregular", "A2"),
        ("rimanere", "to remain", "irregular", "A2"),
        ("salire", "to go up", "irregular", "A2"),
        ("tenere", "to hold", "irregular", "A2"),

        # B1 Level - Intermediate verbs (25 verbs)
        ("spegnere", "to turn off", "irregular", "B1"),
        ("scegliere", "to choose", "irregular", "B1"),
        ("chiedere", "to ask", "irregular", "B1"),
        ("chiudere", "to close", "irregular", "B1"),
        ("decidere", "to decide", "irregular", "B1"),
        ("perdere", "to lose", "irregular", "B1"),
        ("rispondere", "to answer", "irregular", "B1"),
        ("spendere", "to spend", "irregular", "B1"),
        ("vivere", "to live", "irregular", "B1"),
        ("correre", "to run", "irregular", "B1"),
        ("crescere", "to grow", "irregular", "B1"),
        ("piangere", "to cry", "irregular", "B1"),
        ("ridere", "to laugh", "irregular", "B1"),
        ("vincere", "to win", "irregular", "B1"),
        ("camminare", "to walk", "regular_are", "B1"),
        ("dimenticare", "to forget", "regular_are", "B1"),
        ("spiegare", "to explain", "regular_are", "B1"),
        ("mostrare", "to show", "regular_are", "B1"),
        ("pagare", "to pay", "regular_are", "B1"),
        ("preparare", "to prepare", "regular_are", "B1"),
        ("ricordare", "to remember", "regular_are", "B1"),
        ("sembrare", "to seem", "regular_are", "B1"),
        ("sperare", "to hope", "regular_are", "B1"),
        ("aiutare", "to help", "regular_are", "B1"),
        ("invitare", "to invite", "regular_are", "B1"),

        # B2 Level - Advanced verbs (25 verbs)
        ("apparire", "to appear", "irregular", "B2"),
        ("cogliere", "to pick/catch", "irregular", "B2"),
        ("comporre", "to compose", "irregular", "B2"),
        ("condurre", "to lead", "irregular", "B2"),
        ("cuocere", "to cook", "irregular", "B2"),
        ("dipingere", "to paint", "irregular", "B2"),
        ("esprimere", "to express", "irregular", "B2"),
        ("muovere", "to move", "irregular", "B2"),
        ("nascere", "to be born", "irregular", "B2"),
        ("offrire", "to offer", "irregular", "B2"),
        ("porre", "to place", "irregular", "B2"),
        ("raccogliere", "to gather", "irregular", "B2"),
        ("rompere", "to break", "irregular", "B2"),
        ("sciogliere", "to dissolve", "irregular", "B2"),
        ("togliere", "to remove", "irregular", "B2"),
        ("trarre", "to draw", "irregular", "B2"),
        ("accorgersi", "to notice", "irregular", "B2"),
        ("comportare", "to involve", "regular_are", "B2"),
        ("considerare", "to consider", "regular_are", "B2"),
        ("dimostrare", "to demonstrate", "regular_are", "B2"),
        ("riguardare", "to concern", "regular_are", "B2"),
        ("rappresentare", "to represent", "regular_are", "B2"),
        ("verificare", "to verify", "regular_are", "B2"),
        ("contribuire", "to contribute", "regular_ire", "B2"),
        ("sostituire", "to substitute", "regular_ire", "B2"),
    ]

    print(f"Adding {len(verbs_data)} verbs to database...")

    # Conjugation data for each tense
    conjugations_inserted = 0

    for infinitive, english, verb_type, level in verbs_data:
        # Present tense (presente)
        presente = get_presente(infinitive, verb_type)
        for person, form in presente.items():
            cursor.execute("""
                INSERT INTO verb_conjugations
                (infinitive, english, verb_type, tense, person, conjugated_form, level)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (infinitive, english, verb_type, "presente", person, form, level))
            conjugations_inserted += 1

        # Past participle for passato prossimo
        past_participle = get_past_participle(infinitive, verb_type)
        auxiliary = get_auxiliary(infinitive)
        for person in ["io", "tu", "lui_lei", "noi", "voi", "loro"]:
            cursor.execute("""
                INSERT INTO verb_conjugations
                (infinitive, english, verb_type, tense, person, conjugated_form, auxiliary, level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (infinitive, english, verb_type, "passato_prossimo", person, past_participle, auxiliary, level))
            conjugations_inserted += 1

        # Future tense (futuro)
        futuro = get_futuro(infinitive, verb_type)
        for person, form in futuro.items():
            cursor.execute("""
                INSERT INTO verb_conjugations
                (infinitive, english, verb_type, tense, person, conjugated_form, level)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (infinitive, english, verb_type, "futuro", person, form, level))
            conjugations_inserted += 1

        # Imperfect (imperfetto)
        imperfetto = get_imperfetto(infinitive, verb_type)
        for person, form in imperfetto.items():
            cursor.execute("""
                INSERT INTO verb_conjugations
                (infinitive, english, verb_type, tense, person, conjugated_form, level)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (infinitive, english, verb_type, "imperfetto", person, form, level))
            conjugations_inserted += 1

        # Conditional present (condizionale)
        condizionale = get_condizionale(infinitive, verb_type)
        for person, form in condizionale.items():
            cursor.execute("""
                INSERT INTO verb_conjugations
                (infinitive, english, verb_type, tense, person, conjugated_form, level)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (infinitive, english, verb_type, "condizionale", person, form, level))
            conjugations_inserted += 1

        # Subjunctive present (congiuntivo_presente)
        congiuntivo_presente = get_congiuntivo_presente(infinitive, verb_type)
        for person, form in congiuntivo_presente.items():
            cursor.execute("""
                INSERT INTO verb_conjugations
                (infinitive, english, verb_type, tense, person, conjugated_form, level)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (infinitive, english, verb_type, "congiuntivo_presente", person, form, level))
            conjugations_inserted += 1

        # Subjunctive imperfect (congiuntivo_imperfetto)
        congiuntivo_imperfetto = get_congiuntivo_imperfetto(infinitive, verb_type)
        for person, form in congiuntivo_imperfetto.items():
            cursor.execute("""
                INSERT INTO verb_conjugations
                (infinitive, english, verb_type, tense, person, conjugated_form, level)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (infinitive, english, verb_type, "congiuntivo_imperfetto", person, form, level))
            conjugations_inserted += 1

    db.conn.commit()
    print(f"✓ Successfully inserted {conjugations_inserted} conjugations for {len(verbs_data)} verbs")
    print(f"✓ Average of {conjugations_inserted // len(verbs_data)} conjugations per verb")

    # Verify
    cursor.execute("SELECT COUNT(*) FROM verb_conjugations")
    total = cursor.fetchone()[0]
    print(f"✓ Total conjugations in database: {total}")

    db.close()
    return conjugations_inserted


def get_presente(infinitive, verb_type):
    """Get present tense conjugations."""
    # This is a simplified version - in production you'd have complete irregular verb tables
    conjugations = {}

    if infinitive == "essere":
        return {"io": "sono", "tu": "sei", "lui_lei": "è", "noi": "siamo", "voi": "siete", "loro": "sono"}
    elif infinitive == "avere":
        return {"io": "ho", "tu": "hai", "lui_lei": "ha", "noi": "abbiamo", "voi": "avete", "loro": "hanno"}
    elif infinitive == "fare":
        return {"io": "faccio", "tu": "fai", "lui_lei": "fa", "noi": "facciamo", "voi": "fate", "loro": "fanno"}
    elif infinitive == "andare":
        return {"io": "vado", "tu": "vai", "lui_lei": "va", "noi": "andiamo", "voi": "andate", "loro": "vanno"}
    elif infinitive == "venire":
        return {"io": "vengo", "tu": "vieni", "lui_lei": "viene", "noi": "veniamo", "voi": "venite", "loro": "vengono"}
    elif infinitive == "stare":
        return {"io": "sto", "tu": "stai", "lui_lei": "sta", "noi": "stiamo", "voi": "state", "loro": "stanno"}
    elif infinitive == "dire":
        return {"io": "dico", "tu": "dici", "lui_lei": "dice", "noi": "diciamo", "voi": "dite", "loro": "dicono"}
    elif infinitive == "dare":
        return {"io": "do", "tu": "dai", "lui_lei": "dà", "noi": "diamo", "voi": "date", "loro": "danno"}
    elif infinitive == "potere":
        return {"io": "posso", "tu": "puoi", "lui_lei": "può", "noi": "possiamo", "voi": "potete", "loro": "possono"}
    elif infinitive == "volere":
        return {"io": "voglio", "tu": "vuoi", "lui_lei": "vuole", "noi": "vogliamo", "voi": "volete", "loro": "vogliono"}
    elif infinitive == "dovere":
        return {"io": "devo", "tu": "devi", "lui_lei": "deve", "noi": "dobbiamo", "voi": "dovete", "loro": "devono"}
    elif infinitive == "sapere":
        return {"io": "so", "tu": "sai", "lui_lei": "sa", "noi": "sappiamo", "voi": "sapete", "loro": "sanno"}
    elif infinitive == "uscire":
        return {"io": "esco", "tu": "esci", "lui_lei": "esce", "noi": "usciamo", "voi": "uscite", "loro": "escono"}
    elif infinitive == "bere":
        return {"io": "bevo", "tu": "bevi", "lui_lei": "beve", "noi": "beviamo", "voi": "bevete", "loro": "bevono"}
    elif verb_type == "regular_are":
        stem = infinitive[:-3]

        # Handle verbs ending in -iare (mangiare, studiare, etc.)
        # Drop the final i from stem before adding endings that start with i
        if infinitive.endswith("iare"):
            base = stem[:-1]  # Remove the i: "mangi" → "mang"
            return {
                "io": base + "io",         # mangio
                "tu": base + "i",          # mangi (not mangii)
                "lui_lei": base + "ia",    # mangia
                "noi": base + "iamo",      # mangiamo
                "voi": base + "iate",      # mangiate
                "loro": base + "iano"      # mangiano
            }
        # Handle verbs ending in -care/-gare (cercare, pagare, etc.)
        # Add h before i/e to preserve hard sound
        elif infinitive.endswith("care") or infinitive.endswith("gare"):
            return {
                "io": stem + "o",
                "tu": stem + "hi",          # cerchi, paghi
                "lui_lei": stem + "a",
                "noi": stem + "hiamo",      # cerchiamo, paghiamo
                "voi": stem + "ate",
                "loro": stem + "ano"
            }
        # Regular -are verbs
        else:
            return {
                "io": stem + "o",
                "tu": stem + "i",
                "lui_lei": stem + "a",
                "noi": stem + "iamo",
                "voi": stem + "ate",
                "loro": stem + "ano"
            }
    elif verb_type == "regular_ere":
        stem = infinitive[:-3]
        return {
            "io": stem + "o",
            "tu": stem + "i",
            "lui_lei": stem + "e",
            "noi": stem + "iamo",
            "voi": stem + "ete",
            "loro": stem + "ono"
        }
    elif verb_type == "regular_ire":
        stem = infinitive[:-3]
        if infinitive in ["capire", "finire", "preferire", "pulire", "spedire", "costruire", "contribuire"]:
            # -isc verbs
            return {
                "io": stem + "isco",
                "tu": stem + "isci",
                "lui_lei": stem + "isce",
                "noi": stem + "iamo",
                "voi": stem + "ite",
                "loro": stem + "iscono"
            }
        else:
            return {
                "io": stem + "o",
                "tu": stem + "i",
                "lui_lei": stem + "e",
                "noi": stem + "iamo",
                "voi": stem + "ite",
                "loro": stem + "ono"
            }
    else:
        # Default for unknown irregulars
        stem = infinitive[:-3]
        return {
            "io": stem + "o",
            "tu": stem + "i",
            "lui_lei": stem + "e",
            "noi": stem + "iamo",
            "voi": stem + "ete",
            "loro": stem + "ono"
        }


def get_past_participle(infinitive, verb_type):
    """Get past participle."""
    irregular_participles = {
        "essere": "stato",
        "avere": "avuto",
        "fare": "fatto",
        "dire": "detto",
        "leggere": "letto",
        "scrivere": "scritto",
        "vedere": "visto",
        "prendere": "preso",
        "mettere": "messo",
        "aprire": "aperto",
        "chiedere": "chiesto",
        "chiudere": "chiuso",
        "decidere": "deciso",
        "perdere": "perso",
        "rispondere": "risposto",
        "spendere": "speso",
        "venire": "venuto",
        "vivere": "vissuto",
        "correre": "corso",
        "bere": "bevuto",
        "conoscere": "conosciuto",
        "rimanere": "rimasto",
        "scegliere": "scelto",
        "spegnere": "spento",
        "vincere": "vinto",
        "nascere": "nato",
        "offrire": "offerto",
        "rompere": "rotto",
    }

    if infinitive in irregular_participles:
        return irregular_participles[infinitive]
    elif verb_type == "regular_are":
        return infinitive[:-3] + "ato"
    elif verb_type == "regular_ere":
        return infinitive[:-3] + "uto"
    elif verb_type == "regular_ire":
        return infinitive[:-3] + "ito"
    else:
        return infinitive[:-3] + "uto"


def get_auxiliary(infinitive):
    """Determine if verb uses avere or essere."""
    essere_verbs = {
        "essere", "andare", "venire", "arrivare", "partire", "uscire",
        "tornare", "rimanere", "salire", "nascere", "morire", "stare",
        "diventare", "sembrare", "apparire", "crescere", "cadere"
    }
    return "essere" if infinitive in essere_verbs else "avere"


def get_futuro(infinitive, verb_type):
    """Get future tense."""
    if infinitive == "essere":
        return {"io": "sarò", "tu": "sarai", "lui_lei": "sarà", "noi": "saremo", "voi": "sarete", "loro": "saranno"}
    elif infinitive == "avere":
        return {"io": "avrò", "tu": "avrai", "lui_lei": "avrà", "noi": "avremo", "voi": "avrete", "loro": "avranno"}
    elif infinitive == "fare":
        return {"io": "farò", "tu": "farai", "lui_lei": "farà", "noi": "faremo", "voi": "farete", "loro": "faranno"}
    elif infinitive == "andare":
        return {"io": "andrò", "tu": "andrai", "lui_lei": "andrà", "noi": "andremo", "voi": "andrete", "loro": "andranno"}
    elif infinitive == "venire":
        return {"io": "verrò", "tu": "verrai", "lui_lei": "verrà", "noi": "verremo", "voi": "verrete", "loro": "verranno"}
    elif infinitive == "dare":
        return {"io": "darò", "tu": "darai", "lui_lei": "darà", "noi": "daremo", "voi": "darete", "loro": "daranno"}
    elif infinitive == "stare":
        return {"io": "starò", "tu": "starai", "lui_lei": "starà", "noi": "staremo", "voi": "starete", "loro": "staranno"}
    elif verb_type == "regular_are":
        stem = infinitive[:-3]

        # Handle verbs ending in -care/-gare - add h before e
        if infinitive.endswith("care") or infinitive.endswith("gare"):
            return {
                "io": stem + "herò",         # cercherò, pagherò
                "tu": stem + "herai",
                "lui_lei": stem + "herà",
                "noi": stem + "heremo",
                "voi": stem + "herete",
                "loro": stem + "heranno"
            }
        # -iare verbs and regular -are verbs
        else:
            return {
                "io": stem + "erò",
                "tu": stem + "erai",
                "lui_lei": stem + "erà",
                "noi": stem + "eremo",
                "voi": stem + "erete",
                "loro": stem + "eranno"
            }
    elif verb_type in ["regular_ere", "regular_ire"]:
        stem = infinitive[:-1]  # Remove just the 'e' or 'e'
        return {
            "io": stem + "rò",
            "tu": stem + "rai",
            "lui_lei": stem + "rà",
            "noi": stem + "remo",
            "voi": stem + "rete",
            "loro": stem + "ranno"
        }
    else:
        stem = infinitive[:-1]
        return {
            "io": stem + "rò",
            "tu": stem + "rai",
            "lui_lei": stem + "rà",
            "noi": stem + "remo",
            "voi": stem + "rete",
            "loro": stem + "ranno"
        }


def get_imperfetto(infinitive, verb_type):
    """Get imperfect tense."""
    if infinitive == "essere":
        return {"io": "ero", "tu": "eri", "lui_lei": "era", "noi": "eravamo", "voi": "eravate", "loro": "erano"}
    elif infinitive == "fare":
        return {"io": "facevo", "tu": "facevi", "lui_lei": "faceva", "noi": "facevamo", "voi": "facevate", "loro": "facevano"}
    elif infinitive == "dire":
        return {"io": "dicevo", "tu": "dicevi", "lui_lei": "diceva", "noi": "dicevamo", "voi": "dicevate", "loro": "dicevano"}
    elif infinitive == "bere":
        return {"io": "bevevo", "tu": "bevevi", "lui_lei": "beveva", "noi": "bevevamo", "voi": "bevevate", "loro": "bevevano"}
    elif infinitive == "andare":
        # Andare is irregular in presente, but regular in imperfetto
        return {"io": "andavo", "tu": "andavi", "lui_lei": "andava", "noi": "andavamo", "voi": "andavate", "loro": "andavano"}
    elif verb_type == "regular_are":
        stem = infinitive[:-3]
        return {
            "io": stem + "avo",
            "tu": stem + "avi",
            "lui_lei": stem + "ava",
            "noi": stem + "avamo",
            "voi": stem + "avate",
            "loro": stem + "avano"
        }
    elif verb_type in ["regular_ere", "regular_ire"]:
        stem = infinitive[:-3]
        return {
            "io": stem + "evo",
            "tu": stem + "evi",
            "lui_lei": stem + "eva",
            "noi": stem + "evamo",
            "voi": stem + "evate",
            "loro": stem + "evano"
        }
    else:
        stem = infinitive[:-3]
        return {
            "io": stem + "evo",
            "tu": stem + "evi",
            "lui_lei": stem + "eva",
            "noi": stem + "evamo",
            "voi": stem + "evate",
            "loro": stem + "evano"
        }


def get_condizionale(infinitive, verb_type):
    """Get conditional present."""
    if infinitive == "essere":
        return {"io": "sarei", "tu": "saresti", "lui_lei": "sarebbe", "noi": "saremmo", "voi": "sareste", "loro": "sarebbero"}
    elif infinitive == "avere":
        return {"io": "avrei", "tu": "avresti", "lui_lei": "avrebbe", "noi": "avremmo", "voi": "avreste", "loro": "avrebbero"}
    elif infinitive == "fare":
        return {"io": "farei", "tu": "faresti", "lui_lei": "farebbe", "noi": "faremmo", "voi": "fareste", "loro": "farebbero"}
    elif infinitive == "andare":
        return {"io": "andrei", "tu": "andresti", "lui_lei": "andrebbe", "noi": "andremmo", "voi": "andreste", "loro": "andrebbero"}
    elif infinitive == "venire":
        return {"io": "verrei", "tu": "verresti", "lui_lei": "verrebbe", "noi": "verremmo", "voi": "verreste", "loro": "verrebbero"}
    elif verb_type == "regular_are":
        stem = infinitive[:-3]

        # Handle verbs ending in -care/-gare - add h before e
        if infinitive.endswith("care") or infinitive.endswith("gare"):
            return {
                "io": stem + "herei",        # cercherei, pagherei
                "tu": stem + "heresti",
                "lui_lei": stem + "herebbe",
                "noi": stem + "heremmo",
                "voi": stem + "hereste",
                "loro": stem + "herebbero"  # cercherebbero, pagherebbero
            }
        # -iare verbs and regular -are verbs
        else:
            return {
                "io": stem + "erei",
                "tu": stem + "eresti",
                "lui_lei": stem + "erebbe",
                "noi": stem + "eremmo",
                "voi": stem + "ereste",
                "loro": stem + "erebbero"
            }
    elif verb_type in ["regular_ere", "regular_ire"]:
        stem = infinitive[:-1]
        return {
            "io": stem + "rei",
            "tu": stem + "resti",
            "lui_lei": stem + "rebbe",
            "noi": stem + "remmo",
            "voi": stem + "reste",
            "loro": stem + "rebbero"
        }
    else:
        stem = infinitive[:-1]
        return {
            "io": stem + "rei",
            "tu": stem + "resti",
            "lui_lei": stem + "rebbe",
            "noi": stem + "remmo",
            "voi": stem + "reste",
            "loro": stem + "rebbero"
        }


def get_congiuntivo_presente(infinitive, verb_type):
    """Get subjunctive present tense."""
    if infinitive == "essere":
        return {"io": "sia", "tu": "sia", "lui_lei": "sia", "noi": "siamo", "voi": "siate", "loro": "siano"}
    elif infinitive == "avere":
        return {"io": "abbia", "tu": "abbia", "lui_lei": "abbia", "noi": "abbiamo", "voi": "abbiate", "loro": "abbiano"}
    elif infinitive == "fare":
        return {"io": "faccia", "tu": "faccia", "lui_lei": "faccia", "noi": "facciamo", "voi": "facciate", "loro": "facciano"}
    elif infinitive == "andare":
        return {"io": "vada", "tu": "vada", "lui_lei": "vada", "noi": "andiamo", "voi": "andiate", "loro": "vadano"}
    elif infinitive == "dare":
        return {"io": "dia", "tu": "dia", "lui_lei": "dia", "noi": "diamo", "voi": "diate", "loro": "diano"}
    elif infinitive == "stare":
        return {"io": "stia", "tu": "stia", "lui_lei": "stia", "noi": "stiamo", "voi": "stiate", "loro": "stiano"}
    elif infinitive == "dire":
        return {"io": "dica", "tu": "dica", "lui_lei": "dica", "noi": "diciamo", "voi": "diciate", "loro": "dicano"}
    elif infinitive == "venire":
        return {"io": "venga", "tu": "venga", "lui_lei": "venga", "noi": "veniamo", "voi": "veniate", "loro": "vengano"}
    elif infinitive == "potere":
        return {"io": "possa", "tu": "possa", "lui_lei": "possa", "noi": "possiamo", "voi": "possiate", "loro": "possano"}
    elif infinitive == "volere":
        return {"io": "voglia", "tu": "voglia", "lui_lei": "voglia", "noi": "vogliamo", "voi": "vogliate", "loro": "vogliano"}
    elif infinitive == "dovere":
        return {"io": "deva", "tu": "deva", "lui_lei": "deva", "noi": "dobbiamo", "voi": "dobbiate", "loro": "devano"}
    elif infinitive == "sapere":
        return {"io": "sappia", "tu": "sappia", "lui_lei": "sappia", "noi": "sappiamo", "voi": "sappiate", "loro": "sappiano"}
    elif infinitive == "uscire":
        return {"io": "esca", "tu": "esca", "lui_lei": "esca", "noi": "usciamo", "voi": "usciate", "loro": "escano"}
    elif infinitive == "salire":
        return {"io": "salga", "tu": "salga", "lui_lei": "salga", "noi": "saliamo", "voi": "saliate", "loro": "salgano"}
    elif infinitive == "rimanere":
        return {"io": "rimanga", "tu": "rimanga", "lui_lei": "rimanga", "noi": "rimaniamo", "voi": "rimaniate", "loro": "rimangano"}
    elif infinitive == "tenere":
        return {"io": "tenga", "tu": "tenga", "lui_lei": "tenga", "noi": "teniamo", "voi": "teniate", "loro": "tengano"}
    elif infinitive == "bere":
        return {"io": "beva", "tu": "beva", "lui_lei": "beva", "noi": "beviamo", "voi": "beviate", "loro": "bevano"}
    elif verb_type == "regular_are":
        stem = infinitive[:-3]

        # Handle verbs ending in -iare - drop the i before adding i endings
        if infinitive.endswith("iare"):
            base = stem[:-1]  # Remove the i: "mangi" → "mang"
            return {
                "io": base + "i",           # mangi (not mangii)
                "tu": base + "i",
                "lui_lei": base + "i",
                "noi": base + "iamo",
                "voi": base + "iate",
                "loro": base + "ino"
            }
        # Handle verbs ending in -care/-gare - add h before i
        elif infinitive.endswith("care") or infinitive.endswith("gare"):
            return {
                "io": stem + "hi",           # cerchi, paghi
                "tu": stem + "hi",
                "lui_lei": stem + "hi",
                "noi": stem + "hiamo",
                "voi": stem + "hiate",
                "loro": stem + "hino"
            }
        # Regular -are verbs
        else:
            return {
                "io": stem + "i",
                "tu": stem + "i",
                "lui_lei": stem + "i",
                "noi": stem + "iamo",
                "voi": stem + "iate",
                "loro": stem + "ino"
            }
    elif verb_type == "regular_ere":
        stem = infinitive[:-3]
        return {
            "io": stem + "a",
            "tu": stem + "a",
            "lui_lei": stem + "a",
            "noi": stem + "iamo",
            "voi": stem + "iate",
            "loro": stem + "ano"
        }
    elif verb_type == "regular_ire":
        stem = infinitive[:-3]
        if infinitive in ["capire", "finire", "preferire", "pulire", "spedire", "costruire", "contribuire"]:
            # -isc verbs
            return {
                "io": stem + "isca",
                "tu": stem + "isca",
                "lui_lei": stem + "isca",
                "noi": stem + "iamo",
                "voi": stem + "iate",
                "loro": stem + "iscano"
            }
        else:
            return {
                "io": stem + "a",
                "tu": stem + "a",
                "lui_lei": stem + "a",
                "noi": stem + "iamo",
                "voi": stem + "iate",
                "loro": stem + "ano"
            }
    else:
        # Default for unknown irregulars
        stem = infinitive[:-3]
        return {
            "io": stem + "a",
            "tu": stem + "a",
            "lui_lei": stem + "a",
            "noi": stem + "iamo",
            "voi": stem + "iate",
            "loro": stem + "ano"
        }


def get_congiuntivo_imperfetto(infinitive, verb_type):
    """Get subjunctive imperfect tense."""
    if infinitive == "essere":
        return {"io": "fossi", "tu": "fossi", "lui_lei": "fosse", "noi": "fossimo", "voi": "foste", "loro": "fossero"}
    elif infinitive == "dare":
        return {"io": "dessi", "tu": "dessi", "lui_lei": "desse", "noi": "dessimo", "voi": "deste", "loro": "dessero"}
    elif infinitive == "stare":
        return {"io": "stessi", "tu": "stessi", "lui_lei": "stesse", "noi": "stessimo", "voi": "steste", "loro": "stessero"}
    elif infinitive == "fare":
        return {"io": "facessi", "tu": "facessi", "lui_lei": "facesse", "noi": "facessimo", "voi": "faceste", "loro": "facessero"}
    elif infinitive == "dire":
        return {"io": "dicessi", "tu": "dicessi", "lui_lei": "dicesse", "noi": "dicessimo", "voi": "diceste", "loro": "dicessero"}
    elif infinitive == "bere":
        return {"io": "bevessi", "tu": "bevessi", "lui_lei": "bevesse", "noi": "bevessimo", "voi": "beveste", "loro": "bevessero"}
    elif verb_type == "regular_are":
        stem = infinitive[:-3]
        return {
            "io": stem + "assi",
            "tu": stem + "assi",
            "lui_lei": stem + "asse",
            "noi": stem + "assimo",
            "voi": stem + "aste",
            "loro": stem + "assero"
        }
    elif verb_type in ["regular_ere", "regular_ire"]:
        stem = infinitive[:-3]
        return {
            "io": stem + "essi",
            "tu": stem + "essi",
            "lui_lei": stem + "esse",
            "noi": stem + "essimo",
            "voi": stem + "este",
            "loro": stem + "essero"
        }
    else:
        # Default for irregulars
        stem = infinitive[:-3]
        return {
            "io": stem + "essi",
            "tu": stem + "essi",
            "lui_lei": stem + "esse",
            "noi": stem + "essimo",
            "voi": stem + "este",
            "loro": stem + "essero"
        }


if __name__ == "__main__":
    print("=" * 80)
    print("POPULATING VERB CONJUGATIONS DATABASE")
    print("=" * 80)
    print()

    total = populate_verb_conjugations()

    print()
    print("=" * 80)
    print(f"✓ DATABASE POPULATION COMPLETE - {total} conjugations added!")
    print("=" * 80)
