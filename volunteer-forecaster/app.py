
from __future__ import annotations
from flask import Flask, render_template, request, jsonify
import os
import pandas as pd

from forecaster.data import load_csv, summarize_segments
from forecaster.model import simulate_shows, probability_metrics, suggest_plan

app = Flask(__name__)
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "sample_volunteer_history.csv")
DF = load_csv(DATA_PATH)
SEG = summarize_segments(DF)

@app.route("/")
def index():
    event_types = sorted(DF["event_type"].unique().tolist())
    industries = sorted(DF["industry"].unique().tolist())
    return render_template("index.html", event_types=event_types, industries=industries)

@app.post("/api/upload")
def api_upload():
    global DF, SEG
    file = request.files.get("file")
    if not file:
        return jsonify({"ok": False, "error": "No file uploaded"}), 400
    try:
        df = load_csv(file)
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    DF = df
    SEG = summarize_segments(DF)
    return jsonify({"ok": True, "segments": SEG.to_dict(orient="records")})

@app.get("/api/segments")
def api_segments():
    return jsonify({"segments": SEG.to_dict(orient="records")})

@app.post("/api/simulate")
def api_simulate():
    data = request.get_json(force=True) or {}
    print(f"Received simulation request: {data}")  # Debug logging
    
    target = int(data.get("target", 20))
    iters = int(data.get("iters", 10000))
    plan = data.get("plan", [])
    
    print(f"Target: {target}, Iterations: {iters}, Plan: {plan}")  # Debug logging
    
    if not plan:
        return jsonify({"ok": False, "error": "Plan is empty"}), 400
    
    try:
        print(f"Calling simulate_shows with plan: {plan}")  # Debug logging
        print(f"SEG shape: {SEG.shape}")  # Debug logging
        print(f"SEG columns: {list(SEG.columns)}")  # Debug logging
        
        res = simulate_shows(plan, SEG, iters=iters, seed=0)
        print(f"Simulation result: {res}")  # Debug logging
        
        pm = probability_metrics(res["totals"], target)
        print(f"Probability metrics: {pm}")  # Debug logging
        
        return jsonify({"ok": True, "summary": res, "prob": pm})
    except Exception as e:
        import traceback
        print(f"Simulation error: {str(e)}")  # Debug logging
        print(f"Traceback: {traceback.format_exc()}")  # Debug logging
        return jsonify({"ok": False, "error": str(e)}), 400

@app.post("/api/suggest")
def api_suggest():
    data = request.get_json(force=True) or {}
    target = int(data.get("target", 20))
    conf = float(data.get("conf", 0.8))
    plan = data.get("plan", [])
    if not plan:
        return jsonify({"ok": False, "error": "Plan is empty"}), 400
    try:
        sug = suggest_plan(plan, SEG, target=target, conf=conf, max_scale=20.0)
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    return jsonify({"ok": True, "suggestion": sug})

if __name__ == "__main__":
    app.run(debug=True)
