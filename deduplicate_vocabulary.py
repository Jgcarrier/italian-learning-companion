#!/usr/bin/env python3
"""
Deduplicate CEFR vocabulary files so each level only contains NEW words.

CEFR vocabulary is cumulative (B1 includes all A1+A2 words), but for learning
purposes each level should only test NEW words at that level.

This script:
1. Keeps A1 vocabulary as-is (foundation)
2. Removes A1 words from A2, keeping only new A2 words
3. Removes A1+A2 words from B1, keeping only new B1 words
4. Removes A1+A2+B1 words from B2, keeping only new B2 words
"""

import json
from pathlib import Path
import shutil
from datetime import datetime

def load_vocab_file(filepath):
    """Load vocabulary from a JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_vocab_file(filepath, vocab_list):
    """Save vocabulary to a JSON file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(vocab_list, f, ensure_ascii=False, indent=2)

def get_word_set(vocab_list):
    """Extract set of words (lowercased, stripped) from vocabulary list."""
    return {entry['italian'].lower().strip() for entry in vocab_list}

def deduplicate_vocabulary():
    """Deduplicate vocabulary files."""

    data_dir = Path(__file__).parent / "data" / "cefr_vocabulary"

    # Create backup directory
    backup_dir = data_dir / "backups"
    backup_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_subdir = backup_dir / f"backup_{timestamp}"
    backup_subdir.mkdir(exist_ok=True)

    print("=" * 80)
    print("VOCABULARY DEDUPLICATION")
    print("=" * 80)
    print()

    # Backup original files
    print("Creating backups...")
    for level in ['a1', 'a2', 'b1', 'b2']:
        original = data_dir / f"cefr_{level}_vocabulary.json"
        if original.exists():
            backup = backup_subdir / f"cefr_{level}_vocabulary.json"
            shutil.copy2(original, backup)
            print(f"  ✓ Backed up {original.name}")
    print()

    # Load all vocabulary files
    vocab_a1 = load_vocab_file(data_dir / "cefr_a1_vocabulary.json")
    vocab_a2 = load_vocab_file(data_dir / "cefr_a2_vocabulary.json")
    vocab_b1 = load_vocab_file(data_dir / "cefr_b1_vocabulary.json")
    vocab_b2 = load_vocab_file(data_dir / "cefr_b2_vocabulary.json")

    print("Original vocabulary counts:")
    print(f"  A1: {len(vocab_a1)} words")
    print(f"  A2: {len(vocab_a2)} words")
    print(f"  B1: {len(vocab_b1)} words")
    print(f"  B2: {len(vocab_b2)} words")
    print()

    # Get word sets for each level
    words_a1 = get_word_set(vocab_a1)
    words_a2 = get_word_set(vocab_a2)
    words_b1 = get_word_set(vocab_b1)
    words_b2 = get_word_set(vocab_b2)

    # A1 stays the same (foundation level)
    new_vocab_a1 = vocab_a1

    # A2: Remove words that are in A1
    new_vocab_a2 = [entry for entry in vocab_a2
                    if entry['italian'].lower().strip() not in words_a1]

    # B1: Remove words that are in A1 or A2
    lower_words_b1 = words_a1 | words_a2
    new_vocab_b1 = [entry for entry in vocab_b1
                    if entry['italian'].lower().strip() not in lower_words_b1]

    # B2: Remove words that are in A1, A2, or B1
    lower_words_b2 = words_a1 | words_a2 | words_b1
    new_vocab_b2 = [entry for entry in vocab_b2
                    if entry['italian'].lower().strip() not in lower_words_b2]

    print("Deduplication results:")
    print(f"  A1: {len(new_vocab_a1)} words (unchanged, foundation level)")
    print(f"  A2: {len(new_vocab_a2)} words (removed {len(vocab_a2) - len(new_vocab_a2)} duplicates)")
    print(f"  B1: {len(new_vocab_b1)} words (removed {len(vocab_b1) - len(new_vocab_b1)} duplicates)")
    print(f"  B2: {len(new_vocab_b2)} words (removed {len(vocab_b2) - len(new_vocab_b2)} duplicates)")
    print()

    # Save deduplicated files
    print("Saving deduplicated vocabulary files...")
    save_vocab_file(data_dir / "cefr_a1_vocabulary.json", new_vocab_a1)
    save_vocab_file(data_dir / "cefr_a2_vocabulary.json", new_vocab_a2)
    save_vocab_file(data_dir / "cefr_b1_vocabulary.json", new_vocab_b1)
    save_vocab_file(data_dir / "cefr_b2_vocabulary.json", new_vocab_b2)
    print("  ✓ All files saved")
    print()

    # Statistics
    total_before = len(vocab_a1) + len(vocab_a2) + len(vocab_b1) + len(vocab_b2)
    total_after = len(new_vocab_a1) + len(new_vocab_a2) + len(new_vocab_b1) + len(new_vocab_b2)
    total_removed = total_before - total_after

    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total words before: {total_before}")
    print(f"Total words after: {total_after}")
    print(f"Duplicates removed: {total_removed}")
    print(f"Reduction: {(total_removed / total_before * 100):.1f}%")
    print()
    print(f"Backups saved to: {backup_subdir}")
    print()
    print("✓ Deduplication complete!")
    print()

    # Verification
    print("=" * 80)
    print("VERIFICATION (checking for remaining overlaps)")
    print("=" * 80)

    new_words_a1 = get_word_set(new_vocab_a1)
    new_words_a2 = get_word_set(new_vocab_a2)
    new_words_b1 = get_word_set(new_vocab_b1)
    new_words_b2 = get_word_set(new_vocab_b2)

    # Check for any overlaps
    overlap_a1_a2 = new_words_a1 & new_words_a2
    overlap_a1_b1 = new_words_a1 & new_words_b1
    overlap_a1_b2 = new_words_a1 & new_words_b2
    overlap_a2_b1 = new_words_a2 & new_words_b1
    overlap_a2_b2 = new_words_a2 & new_words_b2
    overlap_b1_b2 = new_words_b1 & new_words_b2

    total_overlaps = (len(overlap_a1_a2) + len(overlap_a1_b1) + len(overlap_a1_b2) +
                     len(overlap_a2_b1) + len(overlap_a2_b2) + len(overlap_b1_b2))

    if total_overlaps == 0:
        print("✓ No overlaps found! Each level has unique vocabulary.")
    else:
        print(f"⚠ Warning: Found {total_overlaps} overlaps:")
        if overlap_a1_a2:
            print(f"  A1 ∩ A2: {len(overlap_a1_a2)} words")
        if overlap_a1_b1:
            print(f"  A1 ∩ B1: {len(overlap_a1_b1)} words")
        if overlap_a1_b2:
            print(f"  A1 ∩ B2: {len(overlap_a1_b2)} words")
        if overlap_a2_b1:
            print(f"  A2 ∩ B1: {len(overlap_a2_b1)} words")
        if overlap_a2_b2:
            print(f"  A2 ∩ B2: {len(overlap_a2_b2)} words")
        if overlap_b1_b2:
            print(f"  B1 ∩ B2: {len(overlap_b1_b2)} words")
    print()

if __name__ == "__main__":
    deduplicate_vocabulary()
