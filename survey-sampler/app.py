
from __future__ import annotations
from flask import Flask, render_template, request, jsonify
from planner.formulas import OneGroupInput, sample_size_one_group, GroupRow, MultiGroupInput, overall_moe_from_allocation, allocate, solve_total_n_for_overall_moe, per_group_moe_targets, invites_from_alloc, n_diff_proportions

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.post("/api/one")
def api_one():
    data = request.get_json(force=True) or {}
    try:
        N = data.get("N")
        N = int(N) if (N is not None and str(N).strip() != "") else None
        conf = float(data.get("conf", 0.95))
        p_est = float(data.get("p_est", 0.5))
        deff = float(data.get("deff", 1.0))
        rr = float(data.get("response_rate", 1.0))
        if "moe" in data and data["moe"] not in (None, ""):
            moe = float(data["moe"]) / 100.0  # input as %
            res = sample_size_one_group(OneGroupInput(N=N, moe=moe, n=None, conf=conf, p_est=p_est, deff=deff, response_rate=rr))
        elif "n" in data and data["n"] not in (None, ""):
            n = int(data["n"])
            res = sample_size_one_group(OneGroupInput(N=N, moe=None, n=n, conf=conf, p_est=p_est, deff=deff, response_rate=rr))
        else:
            return jsonify({"ok": False, "error": "Provide either 'moe' (%) or 'n'."}), 400
        return jsonify({"ok": True, "n_required": res.n_required, "invitations_needed": res.invitations_needed, "moe_achieved": res.moe_achieved, "fpc_applied": res.fpc_applied, "details": res.details})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400

@app.post("/api/multi")
def api_multi():
    data = request.get_json(force=True) or {}
    mode = data.get("mode", "overall")  # "overall" or "per_group"
    conf = float(data.get("conf", 0.95))
    style = data.get("allocation", "proportional")  # proportional|balanced|neyman
    groups_in = data.get("groups", [])
    groups = []
    for g in groups_in:
        groups.append(GroupRow(
            name=g.get("name","Group"),
            N=int(g.get("N", 0)),
            p_est=float(g.get("p_est", 0.5)),
            deff=float(g.get("deff", 1.0)),
            response_rate=float(g.get("response_rate", 1.0)),
            min_n=int(g.get("min_n", 0))
        ))
    if mode == "overall":
        target_moe = float(data.get("target_moe", 5.0)) / 100.0
        total_n, alloc = solve_total_n_for_overall_moe(groups, conf, target_moe, style=style)
    elif mode == "per_group":
        target_moe = float(data.get("target_moe", 5.0)) / 100.0
        alloc = per_group_moe_targets(groups, conf, target_moe)
        total_n = sum(alloc)
    else:
        return jsonify({"ok": False, "error": "Unknown mode"}), 400

    invites = invites_from_alloc(groups, alloc)
    overall_moe = overall_moe_from_allocation(groups, alloc, conf)
    per_group = []
    for g, n, inv in zip(groups, alloc, invites):
        per_group.append({
            "name": g.name,
            "N": g.N,
            "p_est": g.p_est,
            "deff": g.deff,
            "response_rate": g.response_rate,
            "n_required": n,
            "invitations_needed": inv
        })
    return jsonify({"ok": True, "overall_moe": overall_moe, "total_n": total_n, "total_invites": sum(invites), "per_group": per_group, "allocation": style, "mode": mode})

@app.post("/api/ab")
def api_ab():
    data = request.get_json(force=True) or {}
    try:
        conf = float(data.get("conf", 0.95))
        power = float(data.get("power", 0.8))
        delta = float(data.get("delta", 0.05))  # absolute difference
        p1 = float(data.get("p1_est", 0.5))
        p2 = float(data.get("p2_est", 0.5))
        deff1 = float(data.get("deff1", 1.0))
        deff2 = float(data.get("deff2", 1.0))
        N1 = data.get("N1")
        N2 = data.get("N2")
        N1 = int(N1) if (N1 not in (None,"")) else None
        N2 = int(N2) if (N2 not in (None,"")) else None
        n1, n2 = n_diff_proportions(delta=delta, conf=conf, power=power, p1=p1, p2=p2, deff1=deff1, deff2=deff2, N1=N1, N2=N2)
        return jsonify({"ok": True, "n_group1": n1, "n_group2": n2})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)
