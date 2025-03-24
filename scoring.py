import functools
import numpy as np

def score(bids, tricks_won):
    final_scores = [0, 0]  # [NS, EW]
    bags = [0, 0]  # [NS, EW]

    for i, bid in enumerate(bids):
        team = i % 2
        tricks = tricks_won[i]
        bid_value = int(bid)

        if tricks >= bid_value:
            final_scores[team] += bid_value * 10
            bags[team] += tricks - bid_value
        else:
            final_scores[team] -= bid_value * 10

    # Apply bags penalty
    for team in range(2):
        final_scores[team] += bags[team]
        if bags[team] >= 10:
            final_scores[team] -= 100
            bags[team] -= 10

    return final_scores

def score_round(bids, tricks_won):
    ns_bids = [bids[0], bids[2]]
    ew_bids = [bids[1], bids[3]]
    ns_tricks = [tricks_won[0], tricks_won[2]]
    ew_tricks = [tricks_won[1], tricks_won[3]]

    ns_score = score(ns_bids, ns_tricks)
    ew_score = score(ew_bids, ew_tricks)

    return ns_score, ew_score

@functools.lru_cache()
def contract_scores_by_trick(bids, tricks_won):
    scores = np.zeros(14)
    if not bids:
        return scores

    for i in range(14):
        scores[i] = score_round(bids, tricks_won)

    return scores
