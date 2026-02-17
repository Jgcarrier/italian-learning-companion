#!/usr/bin/env python3
"""
Analyze vocabulary overlaps between CEFR levels.
Identify words that appear at multiple levels.
"""

import json
from pathlib import Path
from collections import defaultdict

def load_vocab_file(filepath):
    """Load vocabulary from a JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_overlaps():
    """Analyze vocabulary overlaps across all CEFR levels."""

    # Load all vocabulary files
    data_dir = Path(__file__).parent / "data" / "cefr_vocabulary"
    levels = ['a1', 'a2', 'b1', 'b2']

    vocab_by_level = {}
    word_to_levels = defaultdict(list)

    for level in levels:
        filepath = data_dir / f"cefr_{level}_vocabulary.json"
        if filepath.exists():
            vocab = load_vocab_file(filepath)
            vocab_by_level[level.upper()] = vocab

            # Track which levels each word appears in
            for entry in vocab:
                word = entry['italian'].lower().strip()
                word_to_levels[word].append(level.upper())
        else:
            print(f"Warning: {filepath} not found")

    # Print statistics
    print("=" * 80)
    print("VOCABULARY OVERLAP ANALYSIS")
    print("=" * 80)
    print()

    for level in ['A1', 'A2', 'B1', 'B2']:
        if level in vocab_by_level:
            print(f"{level}: {len(vocab_by_level[level])} words")
    print()

    # Find duplicates
    duplicates = {word: levels for word, levels in word_to_levels.items()
                  if len(set(levels)) > 1}

    print(f"Total unique words across all levels: {len(word_to_levels)}")
    print(f"Words appearing at multiple levels: {len(duplicates)}")
    print()

    # Categorize overlaps by problematic severity
    print("=" * 80)
    print("PROBLEMATIC OVERLAPS (words in higher levels that duplicate lower levels)")
    print("=" * 80)
    print()

    # B1 words that duplicate A1/A2
    b1_duplicates = []
    for word, levels in duplicates.items():
        levels_set = set(levels)
        if 'B1' in levels_set and ('A1' in levels_set or 'A2' in levels_set):
            b1_duplicates.append((word, sorted(levels)))

    print(f"B1 words that also appear in A1/A2: {len(b1_duplicates)}")
    if b1_duplicates:
        print("\nSample (first 50):")
        for word, levels in sorted(b1_duplicates)[:50]:
            print(f"  {word:30} → {', '.join(levels)}")
    print()

    # B2 words that duplicate A1/A2/B1
    b2_duplicates = []
    for word, levels in duplicates.items():
        levels_set = set(levels)
        if 'B2' in levels_set and ('A1' in levels_set or 'A2' in levels_set or 'B1' in levels_set):
            b2_duplicates.append((word, sorted(levels)))

    print(f"B2 words that also appear in A1/A2/B1: {len(b2_duplicates)}")
    if b2_duplicates:
        print("\nSample (first 50):")
        for word, levels in sorted(b2_duplicates)[:50]:
            print(f"  {word:30} → {', '.join(levels)}")
    print()

    # Full duplicate report
    print("=" * 80)
    print("ALL DUPLICATES BY CATEGORY")
    print("=" * 80)
    print()

    # Group by level combinations
    overlap_patterns = defaultdict(list)
    for word, levels in duplicates.items():
        pattern = tuple(sorted(set(levels)))
        overlap_patterns[pattern].append(word)

    for pattern in sorted(overlap_patterns.keys()):
        words = sorted(overlap_patterns[pattern])
        print(f"\n{' + '.join(pattern)} ({len(words)} words):")
        # Show first 20 of each pattern
        for word in words[:20]:
            print(f"  {word}")
        if len(words) > 20:
            print(f"  ... and {len(words) - 20} more")

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"B1 duplicates to remove: {len(b1_duplicates)}")
    print(f"B2 duplicates to remove: {len(b2_duplicates)}")
    print()

    # Save detailed report
    report_file = Path(__file__).parent / "vocabulary_overlap_report.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("VOCABULARY OVERLAP DETAILED REPORT\n")
        f.write("=" * 80 + "\n\n")

        f.write("B1 DUPLICATES (should be removed from B1):\n")
        f.write("-" * 80 + "\n")
        for word, levels in sorted(b1_duplicates):
            f.write(f"{word:30} → {', '.join(levels)}\n")

        f.write("\n\nB2 DUPLICATES (should be removed from B2):\n")
        f.write("-" * 80 + "\n")
        for word, levels in sorted(b2_duplicates):
            f.write(f"{word:30} → {', '.join(levels)}\n")

    print(f"Detailed report saved to: {report_file}")

if __name__ == "__main__":
    analyze_overlaps()
