from spinelens.config import PHASE1_TOTAL_BUDGET_GBP, budget_is_balanced, phase1_budget_total
from spinelens.metrics.legibility import DEFAULT_WEIGHTS, weighted_legibility_score, weights_total


def test_phase1_budget_is_balanced() -> None:
    assert phase1_budget_total() == PHASE1_TOTAL_BUDGET_GBP
    assert budget_is_balanced()


def test_legibility_weights_sum_to_one() -> None:
    assert round(weights_total(DEFAULT_WEIGHTS), 6) == 1.0


def test_weighted_legibility_score_accepts_normalized_components() -> None:
    score = weighted_legibility_score(
        {
            "directness": 1.0,
            "turn_burden": 0.5,
            "intersection_complexity": 0.5,
            "crossing_burden": 0.25,
            "continuity": 0.75,
        }
    )
    assert 0.0 <= score <= 1.0
