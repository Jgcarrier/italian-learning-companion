"""
Diagnostic script to check database contents
"""

from database import ItalianDatabase

print("=" * 60)
print("DATABASE DIAGNOSTIC")
print("=" * 60)

with ItalianDatabase() as db:
    cursor = db.conn.cursor()
    
    # Check vocabulary count
    cursor.execute("SELECT COUNT(*) FROM vocabulary")
    vocab_count = cursor.fetchone()[0]
    print(f"\n✓ Total vocabulary words: {vocab_count}")
    
    if vocab_count > 0:
        # Show some examples
        cursor.execute("SELECT italian, english, category FROM vocabulary LIMIT 5")
        print("\nExample vocabulary:")
        for italian, english, category in cursor.fetchall():
            print(f"  - {italian} = {english} ({category})")
    else:
        print("\n❌ NO VOCABULARY IN DATABASE!")
        print("   Run: python3 import_data.py")
    
    # Check topics count
    cursor.execute("SELECT COUNT(*) FROM topics")
    topics_count = cursor.fetchone()[0]
    print(f"\n✓ Total topics: {topics_count}")
    
    if topics_count > 0:
        # Show A1 vs A2
        cursor.execute("SELECT level, COUNT(*) FROM topics GROUP BY level")
        print("\nTopics by level:")
        for level, count in cursor.fetchall():
            print(f"  - {level}: {count} topics")
    else:
        print("\n❌ NO TOPICS IN DATABASE!")
        print("   Run: python3 import_data.py")
    
    # Check verb conjugations
    cursor.execute("SELECT COUNT(*) FROM verb_conjugations")
    verb_count = cursor.fetchone()[0]
    print(f"\n✓ Total verb conjugations: {verb_count}")

print("\n" + "=" * 60)
print("If any counts are 0, run: python3 import_data.py")
print("=" * 60)
