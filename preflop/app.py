
from __future__ import annotations
from flask import Flask, render_template, request, jsonify
import random

from trainer.cards import card_from_str, card_to_str, full_deck, RANK_CHARS, SUIT_CHARS
from trainer.equity import estimate_equity
from trainer.odds import is_pocket_pair, is_suited, rank_gap, flop_set_prob_pocket_pair, flop_pair_or_better_unpaired, flop_flush_stats_suited, river_flush_prob_two_suited, approx_oesd_prob_on_flop
from trainer.recommend import recommend_action

app = Flask(__name__)

@app.route('/')
def index():
    ranks = list(RANK_CHARS)
    suits = list(SUIT_CHARS)
    return render_template('index.html', ranks=ranks, suits=suits)

def parse_hand(a_rank, a_suit, b_rank, b_suit):
    c1 = card_from_str(a_rank + a_suit)
    c2 = card_from_str(b_rank + b_suit)
    if c1 == c2:
        raise ValueError("Duplicate card")
    return [c1, c2]

@app.post('/api/evaluate')
def api_evaluate():
    data = request.get_json(force=True) or {}
    a_rank = data.get('a_rank', 'A')
    a_suit = data.get('a_suit', 's')
    b_rank = data.get('b_rank', 'K')
    b_suit = data.get('b_suit', 'h')
    n_opps = int(data.get('opponents', 1))
    iters = int(data.get('iters', 3000))
    seed = int(data.get('seed', 0))

    try:
        hole = parse_hand(a_rank, a_suit, b_rank, b_suit)
    except ValueError as e:
        return jsonify({'ok': False, 'error': str(e)}), 400

    eq = estimate_equity(hole, n_opponents=n_opps, iters=iters, seed=seed)

    # combinatorial odds
    pp = is_pocket_pair(*hole)
    suited = is_suited(*hole)
    gap = rank_gap(*hole)
    odds = {}
    if pp:
        odds.update(flop_set_prob_pocket_pair())
    else:
        odds.update(flop_pair_or_better_unpaired())
    if suited:
        odds.update(flop_flush_stats_suited())
        odds['flush_by_river'] = river_flush_prob_two_suited()
    else:
        # include backdoor flush chance as N/A
        odds['flush_flop'] = 0.0
        odds['flush_draw'] = 0.0
        odds['backdoor_flush'] = 0.0
        odds['flush_by_river'] = 0.0
    # OESD approx if connectors
    odds['approx_oesd_flop'] = approx_oesd_prob_on_flop(*hole)

    rec = recommend_action(eq, n_opponents=n_opps)

    return jsonify({
        'ok': True,
        'equity': eq,
        'recommendation': rec,
        'odds': odds
    })

@app.post('/api/random_hand')
def api_random_hand():
    deck = full_deck()
    rng = random.Random()
    a = deck.pop(rng.randrange(len(deck)))
    b = deck.pop(rng.randrange(len(deck)))
    return jsonify({'a': card_to_str(a), 'b': card_to_str(b)})

if __name__ == '__main__':
    app.run(debug=True)
