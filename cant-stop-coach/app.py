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
    
    # Fix: Handle empty active_runners case properly
    turn_data = gs.get("turn", {})
    active_runners = turn_data.get("active_runners", {})
    tr = TurnState(
        active_runners={int(k): int(v) for k, v in active_runners.items()} if active_runners else {},
        last_roll=tuple(turn_data["last_roll"]) if turn_data.get("last_roll") else None
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
    try:
        data = request.get_json(force=True) or {}
        num_players = int(data.get("num_players", 2))
        
        # Validate number of players
        if num_players < 2 or num_players > 4:
            return jsonify({"ok": False, "error": "Number of players must be between 2 and 4"}), 400
        
        s = new_game(num_players)
        save_state(s)
        return jsonify({"ok": True, "state": s.to_dict()})
    except (ValueError, TypeError):
        return jsonify({"ok": False, "error": "Invalid number of players"}), 400
    except Exception as e:
        return jsonify({"ok": False, "error": f"New game failed: {str(e)}"}), 500

@app.get("/api/state")
def api_state():
    try:
        s = get_state()
        return jsonify({"state": s.to_dict()})
    except Exception as e:
        return jsonify({"ok": False, "error": f"Failed to get state: {str(e)}"}), 500

@app.get("/api/bust_status")
def api_bust_status():
    """Check if the current player has busted."""
    try:
        s = get_state()
        from cantstop.engine import has_busted
        busted = has_busted(s)
        return jsonify({
            "busted": busted,
            "can_stop": not busted,
            "message": "Bust! Turn will end automatically." if busted else "Turn is active."
        })
    except Exception as e:
        return jsonify({"ok": False, "error": f"Failed to check bust status: {str(e)}"}), 500

@app.get("/api/debug")
def api_debug():
    """Debug endpoint to help troubleshoot game state issues."""
    try:
        s = get_state()
        from cantstop.state import validate_game_state
        
        # Validate state consistency
        validation_errors = validate_game_state(s)
        
        # Get some debug info
        debug_info = {
            "state_valid": len(validation_errors) == 0,
            "validation_errors": validation_errors,
            "current_player": s.current,
            "num_players": s.num_players,
            "winner": s.winner,
            "active_runners_count": len(s.turn.active_runners),
            "free_runners": s.turn.free_runners,
            "has_last_roll": s.turn.last_roll is not None,
            "claimed_columns": [c for c, p in s.claimed_by.items() if p is not None],
            "player_positions": {
                f"player_{i}": {
                    "permanent_pos": dict(p.permanent_pos),
                    "claimed": list(p.claimed)
                } for i, p in enumerate(s.players)
            }
        }
        
        return jsonify({"ok": True, "debug": debug_info})
    except Exception as e:
        return jsonify({"ok": False, "error": f"Debug failed: {str(e)}"}), 500

@app.post("/api/roll")
def api_roll():
    try:
        s = get_state()
        rng = random.Random()
        r = roll_dice(rng)
        s.turn.last_roll = r
        save_state(s)
        pairs = legal_pairings(s, r)
        
        # Check if player busted
        busted = len(pairs) == 0
        if busted:
            from cantstop.engine import handle_bust
            handle_bust(s)
            save_state(s)
            return jsonify({
                "roll": r, 
                "pairings": pairs, 
                "busted": True, 
                "message": "Bust! Turn ended automatically."
            })
        
        return jsonify({"roll": r, "pairings": pairs, "busted": False})
    except Exception as e:
        return jsonify({"ok": False, "error": f"Roll failed: {str(e)}"}), 500

@app.post("/api/apply_pairing")
def api_apply_pairing():
    try:
        s = get_state()
        data = request.get_json(force=True) or {}
        p = data.get("pairing", [])
        
        # Fix: Better input validation
        if not isinstance(p, list) or len(p) != 2:
            return jsonify({"ok": False, "error": "pairing must be a list of 2 integers"}), 400
        
        try:
            p = tuple(int(x) for x in p)
        except (ValueError, TypeError):
            return jsonify({"ok": False, "error": "pairing values must be integers"}), 400
        
        # Ensure the pairing is legal given last_roll
        if not s.turn.last_roll:
            return jsonify({"ok": False, "error": "no last roll"}), 400
        if tuple(p) not in legal_pairings(s, tuple(s.turn.last_roll)):
            return jsonify({"ok": False, "error": "illegal pairing"}), 400
        
        info = apply_pairing(s, tuple(p))
        save_state(s)
        
        # Check if player busted after applying pairing (no more legal moves)
        from cantstop.engine import has_busted
        if has_busted(s):
            from cantstop.engine import handle_bust
            handle_bust(s)
            save_state(s)
            return jsonify({
                "ok": True, 
                "info": info, 
                "state": s.to_dict(),
                "busted": True,
                "message": "Bust after applying pairing! Turn ended automatically."
            })
        
        return jsonify({"ok": True, "info": info, "state": s.to_dict(), "busted": False})
    except Exception as e:
        return jsonify({"ok": False, "error": f"Apply pairing failed: {str(e)}"}), 500

@app.post("/api/stop")
def api_stop():
    try:
        s = get_state()
        
        # Check if player has busted
        from cantstop.engine import has_busted
        if has_busted(s):
            return jsonify({"ok": False, "error": "Cannot stop when busted. Turn will end automatically."}), 400
        
        # Stopping ends turn, banks progress, may switch player
        from cantstop.engine import stop_and_bank
        stop_and_bank(s)
        save_state(s)
        return jsonify({"ok": True, "state": s.to_dict()})
    except Exception as e:
        return jsonify({"ok": False, "error": f"Stop failed: {str(e)}"}), 500

@app.post("/api/odds")
def api_odds():
    try:
        s = get_state()
        p_b = bust_prob(s)
        adv = adv_prob_by_column(s)
        return jsonify({"p_bust": p_b, "adv_by_col": adv})
    except Exception as e:
        return jsonify({"ok": False, "error": f"Odds calculation failed: {str(e)}"}), 500

@app.post("/api/coach/recommend")
def api_coach_recommend():
    try:
        s = get_state()
        data = request.get_json(force=True) or {}
        iters = int(data.get("iters", 2000))
        risk = data.get("risk", "neutral")
        
        # Validate risk parameter
        if risk not in ["averse", "neutral", "seeking"]:
            risk = "neutral"
        
        # Validate iterations
        iters = max(100, min(10000, iters))  # Clamp between 100 and 10000
        
        rec = recommend_press_or_park(s, iters=iters, seed=0, risk=risk)
        # If there's a last roll pending, also suggest a pairing
        pairing_suggestion = None
        if s.turn.last_roll:
            pairing_suggestion = recommend_pairing_after_roll(s, tuple(s.turn.last_roll), iters=max(500, iters//2), seed=1, risk=risk)
        return jsonify({"recommendation": rec, "pairing": pairing_suggestion})
    except Exception as e:
        return jsonify({"ok": False, "error": f"Coach recommendation failed: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
