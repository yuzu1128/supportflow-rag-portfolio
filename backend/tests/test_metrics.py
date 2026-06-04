from app.evaluation.metrics import (
    EvaluationCase,
    EvaluationPrediction,
    abstention_accuracy,
    citation_rate,
    evaluate_predictions,
    mrr,
    recall_at_k,
)


def test_recall_at_k_and_mrr():
    assert recall_at_k(["a", "b", "c"], ["b", "x"], 2) == 0.5
    assert mrr(["a", "b", "c"], ["b"]) == 0.5
    assert mrr(["a", "b"], ["z"]) == 0.0


def test_citation_and_abstention_metrics():
    cases = [
        EvaluationCase("known", ["doc-1"], should_abstain=False),
        EvaluationCase("unknown", [], should_abstain=True),
    ]
    predictions = [
        EvaluationPrediction(["doc-1"], ["doc-1"], abstained=False),
        EvaluationPrediction([], [], abstained=True),
    ]

    assert citation_rate(predictions) == 0.5
    assert abstention_accuracy(cases, predictions) == 1.0
    metrics = evaluate_predictions(cases, predictions, k=1)
    assert metrics["recall_at_1"] == 1.0
    assert metrics["mrr"] == 1.0
