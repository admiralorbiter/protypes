from __future__ import annotations
from flask import Flask, render_template, request, jsonify, session
from flask import redirect, url_for
from dataclasses import asdict
import json, os, random

from cantstop.state import new_game, GameState
from cantstop.engine import roll_dice, legal_pairings, apply_pairing, stop_and_bank, compute_turn_gain, finished_columns_this_turn
from cantstop.odds import bust_prob, adv_prob_by_column
from cantstop.mcts import recommend_press_or_park, recommend_pairing_after_roll
from cantstop.constants import COLUMNS, COLUMN_HEIGHTS

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")

def get_state() -> GameState:
    gs = session.get("state")
    if not gs:
        s = new_game(2)
        session["state"] = s.to_dict()
        return s
    # Rehydrate
    from cantstop.state import PlayerState, TurnState
    players = []
    for p in gs["players"]:
        ps = PlayerState(permanent_pos={int(k):int(v) for k,v in p["permanent_pos"].items()}, claimed=set(p["claimed"]))
        players.append(ps)
    s = GameState(players=players, num_players=gs["num_players"])
    s.claimed_by = {int(k): v for k, v in gs["claimed_by"].items()}
    s.current = gs["current"]
    s.winner = gs["winner"]
    tr = TurnState(
        active_runners={int(k): int(v) for k, v in gs["turn"]["active_runners"].items()},
        last_roll=tuple(gs["turn"]["last_roll"]) if gs["turn"]["last_roll"] else None
    )
    s.turn = tr
    return s

def save_state(s: GameState):
    session["state"] = s.to_dict()

@app.route("/")
def index():
    s = get_state()
    return render_template("index.html", state=s.to_dict(), COLUMNS=COLUMNS, TOP=COLUMN_HEIGHTS)

@app.post("/api/new_game")
def api_new_game():
    data = request.get_json(force=True) or {}
    num_players = int(data.get("num_players", 2))
    s = new_game(num_players)
    save_state(s)
    return jsonify({"ok": True, "state": s.to_dict()})

@app.get("/api/state")
def api_state():
    s = get_state()
    return jsonify({"state": s.to_dict()})

@app.post("/api/roll")
def api_roll():
    s = get_state()
    rng = random.Random()
    r = roll_dice(rng)
    s.turn.last_roll = r
    save_state(s)
    pairs = legal_pairings(s, r)
    return jsonify({"roll": r, "pairings": pairs})

@app.post("/api/apply_pairing")
def api_apply_pairing():
    s = get_state()
    data = request.get_json(force=True) or {}
    p = tuple(data.get("pairing", []))
    if len(p) != 2:
        return jsonify({"ok": False, "error": "pairing required"}), 400
    # Ensure the pairing is legal given last_roll
    if not s.turn.last_roll:
        return jsonify({"ok": False, "error": "no last roll"}), 400
    if tuple(p) not in legal_pairings(s, tuple(s.turn.last_roll)):
        return jsonify({"ok": False, "error": "illegal pairing"}), 400
    info = apply_pairing(s, tuple(p))
    save_state(s)
    # Recompute legal next pairings if they want to keep rolling using same dice (they don't; they roll again)
    return jsonify({"ok": True, "info": info, "state": s.to_dict()})

@app.post("/api/stop")
def api_stop():
    s = get_state()
    # Stopping ends turn, banks progress, may switch player
    stop_and_bank(s)
    save_state(s)
    return jsonify({"ok": True, "state": s.to_dict()})

@app.post("/api/odds")
def api_odds():
    s = get_state()
    p_b = bust_prob(s)
    adv = adv_prob_by_column(s)
    return jsonify({"p_bust": p_b, "adv_by_col": adv})

@app.post("/api/coach/recommend")
def api_recommend():
    s = get_state()
    data = request.get_json(force=True) or {}
    iters = int(data.get("iters", 2000))
    risk = data.get("risk", "neutral")
    rec = recommend_press_or_park(s, iters=iters, seed=0, risk=risk)
    # If there's a last roll pending, also suggest a pairing
    pairing_suggestion = None
    if s.turn.last_roll:
        pairing_suggestion = recommend_pairing_after_roll(s, tuple(s.turn.last_roll), iters=max(500, iters//2), seed=1, risk=risk)
    return jsonify({"recommendation": rec, "pairing": pairing_suggestion})

if __name__ == "__main__":
    app.run(debug=True)
