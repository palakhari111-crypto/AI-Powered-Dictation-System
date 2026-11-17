from backend.app.services.evaluation_service import evaluate

def test_perfect_text():
    result = evaluate("The cat sat.", "The cat sat.")
    assert result["word_accuracy"] == 100
    assert result["overall_score"] == 100

def test_missing_word_detected():
    result = evaluate("The boy went to school.", "The boy went school.")
    assert result["missing_words"] >= 1

def test_extra_word_detected():
    result = evaluate("The boy went home.", "The boy quickly went home.")
    assert result["extra_words"] >= 1
