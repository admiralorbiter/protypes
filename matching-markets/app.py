
from __future__ import annotations
from flask import Flask, render_template, request, jsonify
import json, os, random

from lab.model import Scenario
from lab.data import generate_world
from lab.scenarios import apply_scenario
from lab.da import deferred_acceptance
from lab.metrics import summarize, diff_metrics

app = Flask(__name__)
WORLD = None  # populated on first request
SEED = int(os.environ.get("SEED", "1234"))

def get_world():
    global WORLD
    if WORLD is None:
        WORLD = generate_world(N=8000, M=24, seed=SEED)
    return WORLD

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/debug")
def debug():
    return render_template("debug.html")

@app.post("/api/run")
def api_run():
    world = get_world()
    data = request.get_json(force=True) or {}

    # Baseline scenario
    baseline = Scenario(
        legacy_on_private=True,
        test_required_private_elite=False,
        reserve_first_gen=0.0,
        reserve_rural=0.0,
        reserve_pell=0.0,
        public_in_state_share=0.7
    )
    apply_scenario(world, baseline, seed=SEED)
    match_s_to_c_base, match_c_to_s_base = deferred_acceptance(world, baseline, random.Random(SEED))
    metrics_base = summarize(world, match_s_to_c_base)

    # Alternative scenario from payload
    alt = Scenario(
        legacy_on_private=bool(data.get("legacy_on_private", True)),
        test_required_private_elite=bool(data.get("test_required_private_elite", False)),
        reserve_first_gen=float(data.get("reserve_first_gen", 0.0)),
        reserve_rural=float(data.get("reserve_rural", 0.0)),
        reserve_pell=float(data.get("reserve_pell", 0.0)),
        public_in_state_share=float(data.get("public_in_state_share", 0.7)),
        num_private_elites_test_required=int(data.get("num_private_elites_test_required", 4))
    )
    apply_scenario(world, alt, seed=SEED+1)
    match_s_to_c_alt, match_c_to_s_alt = deferred_acceptance(world, alt, random.Random(SEED+1))
    metrics_alt = summarize(world, match_s_to_c_alt)

    delta = diff_metrics(metrics_base, metrics_alt)

    return jsonify({
        "ok": True,
        "baseline": metrics_base,
        "alternative": metrics_alt,
        "delta": delta
    })

if __name__ == "__main__":
    app.run(debug=True)
