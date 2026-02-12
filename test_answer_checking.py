#!/usr/bin/env python3
"""
Test the improved answer checking logic
"""

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


def check_answer(user_answer: str, correct_answer: str) -> tuple[bool, str]:
    """
    Check if user answer matches the correct answer with flexible matching.

    Returns:
        (is_correct, display_answer) - bool indicating correctness, and the answer to display

    Handles:
    - Accent-forgiving matching
    - Multiple acceptable answers separated by "/" (e.g., "small/low")
    - Optional "to" for verb infinitives (e.g., "to speak" or "speak")
    - Extra whitespace
    """
    user_normalized = remove_accents(user_answer.strip().lower())

    # Split correct answer by "/" to get all acceptable answers
    acceptable_answers = [remove_accents(ans.strip().lower()) for ans in correct_answer.split('/')]

    # For each acceptable answer, also check variants
    all_acceptable = []
    for ans in acceptable_answers:
        all_acceptable.append(ans)

        # If answer starts with "to ", also accept without "to"
        if ans.startswith('to '):
            all_acceptable.append(ans[3:])  # Remove "to "
        # If answer doesn't start with "to ", also accept with "to "
        else:
            # Check if this looks like a verb (heuristic: single word, not a noun with article)
            if ' ' not in ans and not ans.startswith(('il ', 'la ', 'i ', 'gli ', 'le ', "l'")):
                all_acceptable.append(f'to {ans}')

    # Check if user answer matches any acceptable variant
    is_correct = user_normalized in all_acceptable

    # For display, use the first option if multiple
    display_answer = correct_answer.split('/')[0] if '/' in correct_answer else correct_answer

    return is_correct, display_answer


# Test cases
test_cases = [
    # (user_answer, correct_answer, should_be_correct, description)
    ("small", "small/low", True, "Multiple options - first option"),
    ("low", "small/low", True, "Multiple options - second option"),
    ("tiny", "small/low", False, "Multiple options - wrong answer"),

    ("speak", "to speak", True, "Verb without 'to' when answer has 'to'"),
    ("to speak", "to speak", True, "Verb with 'to' when answer has 'to'"),
    ("speak", "speak", True, "Verb without 'to' when answer has no 'to'"),
    ("to speak", "speak", True, "Verb with 'to' when answer has no 'to'"),

    ("caffe", "caffè", True, "Accent removal - caffe vs caffè"),
    ("citta", "città", True, "Accent removal - citta vs città"),
    ("perche", "perché", True, "Accent removal - perche vs perché"),

    ("month", "month", True, "Exact match"),
    ("Month", "month", True, "Case insensitive"),
    ("  month  ", "month", True, "Extra whitespace"),

    ("il libro", "il libro", True, "Noun with article - exact match"),
    ("to il libro", "il libro", False, "Noun with article - shouldn't accept 'to'"),

    ("eat", "to eat/to consume", True, "Multiple verbs - first without 'to'"),
    ("consume", "to eat/to consume", True, "Multiple verbs - second without 'to'"),
    ("to eat", "to eat/to consume", True, "Multiple verbs - first with 'to'"),
    ("to consume", "to eat/to consume", True, "Multiple verbs - second with 'to'"),
]

print("Testing Answer Checking Logic")
print("=" * 70)

passed = 0
failed = 0

for user_ans, correct_ans, expected, description in test_cases:
    is_correct, display = check_answer(user_ans, correct_ans)
    status = "✅ PASS" if is_correct == expected else "❌ FAIL"

    if is_correct == expected:
        passed += 1
    else:
        failed += 1
        print(f"\n{status}: {description}")
        print(f"  User: '{user_ans}' | Correct: '{correct_ans}'")
        print(f"  Expected: {expected}, Got: {is_correct}")

print("\n" + "=" * 70)
print(f"Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")

if failed == 0:
    print("✅ All tests passed!")
else:
    print(f"❌ {failed} test(s) failed")

print("\n" + "=" * 70)
print("Example acceptable inputs:")
print("  'small/low' accepts: small, low")
print("  'to speak' accepts: speak, to speak")
print("  'speak' accepts: speak, to speak")
print("  'caffè' accepts: caffe, caffè")
print("  'to eat/to consume' accepts: eat, to eat, consume, to consume")
