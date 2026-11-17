import re
import difflib
import string

def tokens(text: str):
    return re.findall(r"\w+|[^\w\s]", text, flags=re.UNICODE)

def evaluate(expected: str, actual: str):
    exp = tokens(expected)
    act = tokens(actual)
    matcher = difflib.SequenceMatcher(a=exp, b=act, autojunk=False)
    details = []
    missing = extra = substitutions = 0
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        e = exp[i1:i2]
        a = act[j1:j2]
        if tag == "delete":
            missing += len(e)
            kind = "missing_word"
        elif tag == "insert":
            extra += len(a)
            kind = "extra_word"
        else:
            substitutions += min(len(e), len(a))
            kind = "substitution_or_spelling"
        details.append({"type": kind, "expected": " ".join(e), "student": " ".join(a)})
    expected_words = [x for x in exp if x not in string.punctuation]
    actual_words = [x for x in act if x not in string.punctuation]
    word_match = difflib.SequenceMatcher(a=[x.lower() for x in expected_words],
                                         b=[x.lower() for x in actual_words], autojunk=False)
    correct_words = sum(block.size for block in word_match.get_matching_blocks())
    word_accuracy = 100 * correct_words / max(1, len(expected_words))
    char_ratio = difflib.SequenceMatcher(a=expected.lower(), b=actual.lower(), autojunk=False).ratio()
    capitalization_errors = sum(1 for e, a in zip(expected_words, actual_words)
                                 if e.lower() == a.lower() and e != a)
    punctuation_errors = sum(1 for e, a in zip(exp, act)
                             if e in string.punctuation and a in string.punctuation and e != a)
    # Conservative transparent score: token-level accuracy is primary.
    overall = round(max(0.0, min(100.0, word_accuracy * 0.85 + char_ratio * 15)), 2)
    return {
        "overall_score": overall,
        "word_accuracy": round(word_accuracy, 2),
        "character_accuracy": round(char_ratio * 100, 2),
        "spelling_errors": substitutions,
        "missing_words": missing,
        "extra_words": extra,
        "punctuation_errors": punctuation_errors,
        "capitalization_errors": capitalization_errors,
        "details": details
    }
