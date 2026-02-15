"""
Italian Learning Companion - Main Application
A terminal-based interface for practicing Italian.
"""

import time
from datetime import datetime
from database import ItalianDatabase
from practice_generator import PracticeGenerator

def remove_accents(text: str) -> str:
    """Remove Italian accents from text for flexible answer checking.
    
    Converts: à→a, è→e, é→e, ì→i, ò→o, ù→u
    """
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

class ItalianLearningApp:
    def __init__(self):
        self.db = ItalianDatabase()
        self.generator = PracticeGenerator(self.db)
    
    def clear_screen(self):
        """Clear the terminal screen."""
        print("\n" * 50)  # Simple clear for cross-platform compatibility
    
    def show_main_menu(self):
        """Display the main menu."""
        print("\n" + "=" * 60)
        print("🇮🇹  ITALIAN LEARNING COMPANION  🇮🇹")
        print("=" * 60)
        print("\nMain Menu:")
        print("  1. Verb Practice (Submenu)")
        print("  2. Vocabulary Quiz")
        print("  3. Grammar Practice (Submenu)")
        print("  4. Multiple Choice")
        print("  5. Focus on Weak Areas")
        print("  6. View Progress Stats")
        print("  7. Topic List")
        print("  0. Exit")
        print()
    
    def run_practice_session(self, questions: list, session_type: str):
        """Run a practice session with the given questions."""
        if not questions:
            print("❌ No questions available for this practice type.")
            input("\nPress Enter to continue...")
            return
        
        print(f"\n{'=' * 60}")
        print(f"Starting {session_type}")
        print(f"{'=' * 60}")
        print(f"You have {len(questions)} questions.\n")
        
        correct = 0
        start_time = time.time()
        results = []
        
        for i, q in enumerate(questions, 1):
            print(f"\nQuestion {i}/{len(questions)}:")
            print(f"  {q['question']}")
            
            # Show choices for multiple choice
            if q['type'] == 'multiple_choice':
                for idx, choice in enumerate(q['choices'], 1):
                    print(f"    {idx}. {choice}")
                user_answer = input("\nYour answer (1-4): ").strip()
                try:
                    choice_idx = int(user_answer) - 1
                    user_answer = q['choices'][choice_idx]
                except (ValueError, IndexError):
                    user_answer = ""
            else:
                user_answer = input("\nYour answer: ").strip()
            
            # Check answer with and without accents for flexibility
            user_answer_normalized = remove_accents(user_answer.lower())
            correct_answer_normalized = remove_accents(q['answer'].lower())
            is_correct = user_answer_normalized == correct_answer_normalized
            
            if is_correct:
                print("✅ Correct!")
                # Show proper spelling if user didn't use accents
                if user_answer.lower() != q['answer'].lower():
                    print(f"   (Proper spelling: {q['answer']})")
                correct += 1
            else:
                print(f"❌ Wrong. The correct answer is: {q['answer']}")
            
            results.append({
                'question': q['question'],
                'user_answer': user_answer,
                'correct_answer': q['answer'],
                'is_correct': is_correct
            })
            
            time.sleep(1)  # Brief pause between questions
        
        # Calculate results
        end_time = time.time()
        time_spent = int(end_time - start_time)
        accuracy = (correct / len(questions)) * 100
        
        # Show summary
        print(f"\n{'=' * 60}")
        print("📊 SESSION SUMMARY")
        print(f"{'=' * 60}")
        print(f"  Score: {correct}/{len(questions)} ({accuracy:.1f}%)")
        print(f"  Time: {time_spent // 60}m {time_spent % 60}s")
        
        if accuracy >= 90:
            print("  Grade: 🌟 Excellent!")
        elif accuracy >= 75:
            print("  Grade: 👍 Good job!")
        elif accuracy >= 60:
            print("  Grade: 📚 Keep practicing!")
        else:
            print("  Grade: 💪 More practice needed!")
        
        # Save session to database
        session_id = self.db.record_practice_session(
            session_type=session_type,
            total_questions=len(questions),
            correct_answers=correct,
            time_spent=time_spent
        )
        
        print(f"\n✅ Session saved to database (ID: {session_id})")
        input("\nPress Enter to continue...")
    
    def verb_conjugation_practice(self):
        """Verb practice submenu."""
        while True:
            print("\n" + "=" * 60)
            print("VERB PRACTICE")
            print("=" * 60)
            print("\n  1. General Conjugation Practice (A1/A2)")
            print("  2. Irregular Passato Prossimo")
            print("  3. Choose Avere vs Essere (Passato Prossimo)")
            print("  4. Futuro Semplice")
            print("  5. Reflexive Verbs")
            print("  0. Back to Main Menu")
            
            choice = input("\nChoice: ").strip()
            
            if choice == "0":
                return
            elif choice == "1":
                # Original general practice
                print("\nChoose level:")
                print("  1. A1 (completed)")
                print("  2. A2 (current)")
                level_choice = input("Choice: ").strip()
                level = "A1" if level_choice == "1" else "A2"
                count = int(input("How many questions? (default 10): ").strip() or "10")
                questions = self.generator.generate_verb_conjugation_drill(level, count)
                self.run_practice_session(questions, f"Verb Conjugation ({level})")
            elif choice == "2":
                count = int(input("How many questions? (default 10): ").strip() or "10")
                questions = self.generator.generate_irregular_passato_prossimo(count)
                self.run_practice_session(questions, "Irregular Passato Prossimo")
            elif choice == "3":
                count = int(input("How many questions? (default 10): ").strip() or "10")
                questions = self.generator.generate_auxiliary_choice(count)
                self.run_auxiliary_choice_session(questions)
            elif choice == "4":
                count = int(input("How many questions? (default 10): ").strip() or "10")
                questions = self.generator.generate_futuro_semplice(count)
                self.run_practice_session(questions, "Futuro Semplice")
            elif choice == "5":
                count = int(input("How many questions? (default 10): ").strip() or "10")
                questions = self.generator.generate_reflexive_verbs(count)
                self.run_practice_session(questions, "Reflexive Verbs")
            else:
                print("\n❌ Invalid choice.")
                time.sleep(1)
    
    def grammar_practice(self):
        """Grammar practice submenu."""
        while True:
            print("\n" + "=" * 60)
            print("GRAMMAR PRACTICE")
            print("=" * 60)
            print("\n  1. Articulated Prepositions (del, alla, nel, etc.)")
            print("  2. Time Prepositions (per, da, a, fa)")
            print("  3. Negations (non...mai, non...più, etc.)")
            print("  4. Fill in the Blank (Mixed)")
            print("  0. Back to Main Menu")
            
            choice = input("\nChoice: ").strip()
            
            if choice == "0":
                return
            elif choice == "1":
                count = int(input("How many questions? (default 10): ").strip() or "10")
                questions = self.generator.generate_articulated_prepositions(count)
                self.run_practice_session(questions, "Articulated Prepositions")
            elif choice == "2":
                count = int(input("How many questions? (default 10): ").strip() or "10")
                questions = self.generator.generate_time_prepositions(count)
                self.run_time_prepositions_session(questions)
            elif choice == "3":
                count = int(input("How many questions? (default 10): ").strip() or "10")
                questions = self.generator.generate_negation_practice(count)
                self.run_negation_session(questions)
            elif choice == "4":
                count = int(input("How many questions? (default 10): ").strip() or "10")
                questions = self.generator.generate_fill_in_blank("A1", count)
                self.run_practice_session(questions, "Fill in the Blank")
            else:
                print("\n❌ Invalid choice.")
                time.sleep(1)
    
    def run_auxiliary_choice_session(self, questions: list):
        """Special session for auxiliary choice - shows explanation."""
        if not questions:
            print("❌ No questions available.")
            input("\nPress Enter to continue...")
            return
        
        print(f"\n{'=' * 60}")
        print("AUXILIARY CHOICE PRACTICE")
        print(f"{'=' * 60}")
        print(f"You have {len(questions)} questions.")
        print("Choose: avere or essere\n")
        
        correct = 0
        start_time = time.time()
        
        for i, q in enumerate(questions, 1):
            print(f"\nQuestion {i}/{len(questions)}:")
            print(f"  {q['question']}")
            print("    1. avere")
            print("    2. essere")
            
            user_choice = input("\nYour answer (1 or 2): ").strip()
            user_answer = "avere" if user_choice == "1" else "essere" if user_choice == "2" else ""
            
            is_correct = user_answer == q['answer']
            
            if is_correct:
                print("✅ Correct!")
                correct += 1
            else:
                print(f"❌ Wrong. The correct answer is: {q['answer']}")
            
            print(f"   Why? {q['reason']}")
            time.sleep(2)
        
        # Summary
        end_time = time.time()
        time_spent = int(end_time - start_time)
        accuracy = (correct / len(questions)) * 100
        
        print(f"\n{'=' * 60}")
        print("📊 SESSION SUMMARY")
        print(f"{'=' * 60}")
        print(f"  Score: {correct}/{len(questions)} ({accuracy:.1f}%)")
        print(f"  Time: {time_spent // 60}m {time_spent % 60}s")
        
        if accuracy >= 90:
            print("  Grade: 🌟 Excellent!")
        elif accuracy >= 75:
            print("  Grade: 👍 Good job!")
        elif accuracy >= 60:
            print("  Grade: 📚 Keep practicing!")
        else:
            print("  Grade: 💪 More practice needed!")
        
        session_id = self.db.record_practice_session(
            session_type="Auxiliary Choice",
            total_questions=len(questions),
            correct_answers=correct,
            time_spent=time_spent
        )
        
        print(f"\n✅ Session saved (ID: {session_id})")
        input("\nPress Enter to continue...")
    
    def run_time_prepositions_session(self, questions: list):
        """Special session for time prepositions - shows explanation."""
        if not questions:
            print("❌ No questions available.")
            input("\nPress Enter to continue...")
            return
        
        print(f"\n{'=' * 60}")
        print("TIME PREPOSITIONS PRACTICE")
        print(f"{'=' * 60}")
        print(f"You have {len(questions)} questions.")
        print("Choose: per, da, a, or fa\n")
        print("Quick guide:")
        print("  per = for (finished duration)")
        print("  da = since/for (continuing)")
        print("  a = at (point in time/age)")
        print("  fa = ago")
        print()
        
        correct = 0
        start_time = time.time()
        
        for i, q in enumerate(questions, 1):
            print(f"\nQuestion {i}/{len(questions)}:")
            print(f"  {q['question']}")
            
            user_answer = input("\nYour answer: ").strip().lower()
            
            # Check with accent flexibility
            user_answer_normalized = remove_accents(user_answer)
            correct_answer_normalized = remove_accents(q['answer'].lower())
            is_correct = user_answer_normalized == correct_answer_normalized
            
            if is_correct:
                print("✅ Correct!")
                if user_answer.lower() != q['answer'].lower():
                    print(f"   (Proper spelling: {q['answer']})")
                correct += 1
            else:
                print(f"❌ Wrong. The correct answer is: {q['answer']}")
            
            print(f"   Why? {q['explanation']}")
            time.sleep(2)
        
        # Summary
        end_time = time.time()
        time_spent = int(end_time - start_time)
        accuracy = (correct / len(questions)) * 100
        
        print(f"\n{'=' * 60}")
        print("📊 SESSION SUMMARY")
        print(f"{'=' * 60}")
        print(f"  Score: {correct}/{len(questions)} ({accuracy:.1f}%)")
        print(f"  Time: {time_spent // 60}m {time_spent % 60}s")
        
        if accuracy >= 90:
            print("  Grade: 🌟 Excellent!")
        elif accuracy >= 75:
            print("  Grade: 👍 Good job!")
        elif accuracy >= 60:
            print("  Grade: 📚 Keep practicing!")
        else:
            print("  Grade: 💪 More practice needed!")
        
        session_id = self.db.record_practice_session(
            session_type="Time Prepositions",
            total_questions=len(questions),
            correct_answers=correct,
            time_spent=time_spent
        )
        
        print(f"\n✅ Session saved (ID: {session_id})")
        input("\nPress Enter to continue...")
    
    def run_negation_session(self, questions: list):
        """Special session for negations - shows explanation."""
        if not questions:
            print("❌ No questions available.")
            input("\nPress Enter to continue...")
            return
        
        print(f"\n{'=' * 60}")
        print("NEGATION PRACTICE")
        print(f"{'=' * 60}")
        print(f"You have {len(questions)} questions.")
        print()
        print("Quick guide - Double negatives in Italian:")
        print("  non...mai = never")
        print("  non...più = not anymore")
        print("  non...niente/nulla = nothing")
        print("  non...nessuno = no one")
        print("  non...neanche = not even")
        print()
        
        correct = 0
        start_time = time.time()
        
        for i, q in enumerate(questions, 1):
            print(f"\nQuestion {i}/{len(questions)}:")
            print(f"  {q['question']}")
            
            user_answer = input("\nYour answer: ").strip()
            
            # Check with accent flexibility
            user_answer_normalized = remove_accents(user_answer.lower())
            correct_answer_normalized = remove_accents(q['answer'].lower())
            is_correct = user_answer_normalized == correct_answer_normalized
            
            if is_correct:
                print("✅ Correct!")
                if user_answer.lower() != q['answer'].lower():
                    print(f"   (Proper spelling: {q['answer']})")
                correct += 1
            else:
                print(f"❌ Wrong. The correct answer is: {q['answer']}")
            
            print(f"   💡 {q['explanation']}")
            time.sleep(2)
        
        # Summary
        end_time = time.time()
        time_spent = int(end_time - start_time)
        accuracy = (correct / len(questions)) * 100
        
        print(f"\n{'=' * 60}")
        print("📊 SESSION SUMMARY")
        print(f"{'=' * 60}")
        print(f"  Score: {correct}/{len(questions)} ({accuracy:.1f}%)")
        print(f"  Time: {time_spent // 60}m {time_spent % 60}s")
        
        if accuracy >= 90:
            print("  Grade: 🌟 Excellent!")
        elif accuracy >= 75:
            print("  Grade: 👍 Good job!")
        elif accuracy >= 60:
            print("  Grade: 📚 Keep practicing!")
        else:
            print("  Grade: 💪 More practice needed!")
        
        session_id = self.db.record_practice_session(
            session_type="Negations",
            total_questions=len(questions),
            correct_answers=correct,
            time_spent=time_spent
        )
        
        print(f"\n✅ Session saved (ID: {session_id})")
        input("\nPress Enter to continue...")
    
    def vocabulary_quiz(self):
        """Start vocabulary quiz."""
        print("\n" + "=" * 60)
        print("VOCABULARY QUIZ")
        print("=" * 60)
        print("\nChoose direction:")
        print("  1. Italian → English")
        print("  2. English → Italian")
        print("  0. Back")
        
        choice = input("\nChoice: ").strip()
        
        if choice == "0":
            return
        
        direction = "it_to_en" if choice == "1" else "en_to_it"
        count = int(input("How many questions? (default 10): ").strip() or "10")
        
        questions = self.generator.generate_vocabulary_quiz("A1", count, direction)
        self.run_practice_session(questions, "Vocabulary Quiz")
    
    def view_stats(self):
        """Show performance statistics."""
        print("\n" + "=" * 60)
        print("📈 YOUR PROGRESS")
        print("=" * 60)
        
        # Get stats for different time periods
        periods = [7, 30, 90]
        
        for days in periods:
            stats = self.db.get_performance_stats(days)
            print(f"\n{days} days:")
            print(f"  Sessions: {stats['total_sessions'] or 0}")
            print(f"  Questions: {stats['total_questions'] or 0}")
            print(f"  Accuracy: {stats['avg_accuracy']:.1f}%" if stats['avg_accuracy'] else "  Accuracy: N/A")
        
        # Show weak areas
        print("\n" + "-" * 60)
        print("Weak Areas (need practice):")
        weak = self.db.get_weak_areas(5)
        if weak:
            for area in weak:
                if area['topic_name']:
                    print(f"  • {area['topic_name']} ({area['error_count']} errors)")
                elif area['vocab_word']:
                    print(f"  • {area['vocab_word']} ({area['error_count']} errors)")
        else:
            print("  No weak areas yet - keep practicing!")
        
        input("\nPress Enter to continue...")
    
    def view_topics(self):
        """Show all topics by level."""
        print("\n" + "=" * 60)
        print("📚 TOPICS")
        print("=" * 60)
        
        for level in ["A1", "A2"]:
            topics = self.db.get_topics_by_level(level)
            print(f"\n{level} Topics ({len(topics)}):")
            
            for topic in topics:
                status = "✅" if topic['completed'] else "🔄"
                print(f"  {status} {topic['name']}")
                print(f"     Category: {topic['category']}")
                if topic['description']:
                    print(f"     {topic['description']}")
        
        input("\nPress Enter to continue...")
    
    def run(self):
        """Main application loop."""
        while True:
            self.clear_screen()
            self.show_main_menu()
            choice = input("Choose an option: ").strip()
            
            if choice == "0":
                print("\nGrazie! Arrivederci! 👋")
                break
            elif choice == "1":
                self.verb_conjugation_practice()  # Now opens submenu
            elif choice == "2":
                self.vocabulary_quiz()
            elif choice == "3":
                self.grammar_practice()  # Now opens submenu
            elif choice == "4":
                questions = self.generator.generate_multiple_choice("A1", 10)
                self.run_practice_session(questions, "Multiple Choice")
            elif choice == "5":
                print("\n⚠️  Weak areas practice coming soon!")
                input("\nPress Enter to continue...")
            elif choice == "6":
                self.view_stats()
            elif choice == "7":
                self.view_topics()
            else:
                print("\n❌ Invalid choice. Please try again.")
                time.sleep(1)
        
        # Cleanup
        self.db.close()


def main():
    """Entry point for the application."""
    app = ItalianLearningApp()
    app.run()


if __name__ == "__main__":
    main()
