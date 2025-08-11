
from flask import Flask, render_template, request, jsonify
import math
import random
import statistics

app = Flask(__name__)

# -----------------------
# Pages
# -----------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/birthday")
def birthday():
    return render_template("birthday.html")

@app.route("/monty")
def monty():
    return render_template("monty.html")

@app.route("/clt")
def clt():
    return render_template("clt.html")

@app.route("/benford")
def benford():
    return render_template("benford.html")

@app.route("/lln")
def lln():
    return render_template("lln.html")

@app.route("/life")
def life():
    return render_template("life.html")

# -----------------------
# Helpers
# -----------------------
def clamp(val, lo, hi):
    try:
        v = float(val)
    except Exception:
        return None
    return max(lo, min(hi, v))

def first_significant_digit(x: float):
    """Return first significant digit (1..9) of a positive number x; None if not defined."""
    if x is None or x <= 0 or math.isnan(x) or math.isinf(x):
        return None
    # Use log10 to avoid slow loops
    try:
        exp = math.floor(math.log10(x))
        frac = x / (10 ** exp)  # in [1,10)
        d = int(frac)
        if 1 <= d <= 9:
            return d
        # Fallback if something weird happens with floating point
        s = f"{x:.12g}"
        for ch in s:
            if ch.isdigit() and ch != '0':
                return int(ch)
    except Exception:
        pass
    return None

# -----------------------
# APIs
# -----------------------
@app.route("/api/birthday")
def api_birthday():
    group_size = request.args.get("group_size", 23)
    trials = request.args.get("trials", 5000)

    group_size = int(clamp(group_size, 2, 366))
    trials = int(clamp(trials, 100, 20000))

    # Theoretical probability (no leap day)
    if group_size > 365:
        theoretical = 1.0
    else:
        prod = 1.0
        for k in range(group_size):
            prod *= (365.0 - k) / 365.0
        theoretical = 1.0 - prod

    # Simulation
    duplicates = 0
    for _ in range(trials):
        seen = set()
        dup = False
        for _ in range(group_size):
            b = random.randint(1, 365)
            if b in seen:
                dup = True
                break
            seen.add(b)
        if dup:
            duplicates += 1

    simulated = duplicates / trials

    return jsonify({
        "group_size": group_size,
        "trials": trials,
        "theoretical": theoretical,
        "simulated": simulated
    })

@app.route("/api/monty")
def api_monty():
    strategy = request.args.get("strategy", "both").lower()
    trials = int(clamp(request.args.get("trials", 10000), 100, 50000))

    def simulate(strategy: str, n: int):
        wins = 0
        for _ in range(n):
            prize = random.randint(0, 2)
            pick = random.randint(0, 2)
            # Host opens a goat door not chosen by the player
            doors = {0,1,2}
            remaining = list(doors - {pick, prize}) if pick != prize else list(doors - {pick})
            host_opens = random.choice(remaining)
            unopened = list(doors - {pick, host_opens})
            if strategy == "switch":
                final_pick = unopened[0] if unopened[0] != pick else unopened[1]
            else:
                final_pick = pick
            if final_pick == prize:
                wins += 1
        return wins / n

    if strategy == "both":
        result = {
            "stay": simulate("stay", trials),
            "switch": simulate("switch", trials),
            "trials": trials
        }
    elif strategy in ("stay", "switch"):
        result = {
            "strategy": strategy,
            "win_rate": simulate(strategy, trials),
            "trials": trials
        }
    else:
        return jsonify({"error": "strategy must be one of: both, stay, switch"}), 400

    return jsonify(result)

@app.route("/api/clt")
def api_clt():
    dist = request.args.get("dist", "uniform").lower()
    sample_size = int(clamp(request.args.get("sample_size", 30), 1, 400))
    num_samples = int(clamp(request.args.get("num_samples", 1000), 100, 5000))
    bins = int(clamp(request.args.get("bins", 25), 10, 60))
    p = clamp(request.args.get("p", 0.5), 0.0, 1.0)

    if dist not in ("uniform", "exponential", "bernoulli"):
        return jsonify({"error": "dist must be one of: uniform, exponential, bernoulli"}), 400

    def rv():
        if dist == "uniform":
            return random.random()  # U(0,1)
        elif dist == "exponential":
            u = 1.0 - random.random()
            return -math.log(u)  # Exp(1)
        else:  # bernoulli
            return 1.0 if random.random() < p else 0.0

    # Theoretical moments
    if dist == "uniform":
        mu, var = 0.5, 1.0/12.0
        params = {"a": 0.0, "b": 1.0}
    elif dist == "exponential":
        mu, var = 1.0, 1.0
        params = {"lambda": 1.0}
    else:  # bernoulli
        mu, var = p, p*(1.0-p)
        params = {"p": p}

    # Sample means
    means = []
    for _ in range(num_samples):
        s = 0.0
        for _ in range(sample_size):
            s += rv()
        means.append(s / sample_size)

    # Histogram
    lo, hi = min(means), max(means)
    # pad range slightly so the outer bars don't touch edges
    pad = (hi - lo) * 0.05 if hi > lo else 0.1
    lo -= pad
    hi += pad
    width = (hi - lo) / bins
    counts = [0] * bins
    for m in means:
        idx = int((m - lo) / width)
        if idx < 0:
            idx = 0
        elif idx >= bins:
            idx = bins - 1
        counts[idx] += 1
    buckets = [{"x0": lo + i*width, "x1": lo + (i+1)*width, "count": c} for i, c in enumerate(counts)]

    # Normal approximation curve
    sigma_mean = math.sqrt(var / sample_size) if var >= 0 else 0.0
    curve_points = []
    # Scale normal pdf to histogram counts by multiplying by bin width and num_samples
    for i in range(200):
        x = lo + (hi - lo) * (i / 199.0)
        if sigma_mean > 0:
            pdf = (1.0 / (sigma_mean * math.sqrt(2*math.pi))) * math.exp(-0.5 * ((x - mu)/sigma_mean) ** 2)
            y = pdf * width * num_samples
        else:
            y = 0.0
        curve_points.append({"x": x, "y": y})

    summary = {
        "empirical_mean": statistics.fmean(means),
        "empirical_std": statistics.pstdev(means) if len(means) > 1 else 0.0,
        "min": min(means),
        "max": max(means),
        "theoretical_mean": mu,
        "theoretical_std_of_mean": sigma_mean
    }

    return jsonify({
        "dist": dist,
        "params": params,
        "sample_size": sample_size,
        "num_samples": num_samples,
        "bins": bins,
        "buckets": buckets,
        "normal_curve": curve_points,
        "summary": summary
    })

@app.route("/api/benford")
def api_benford():
    generator = request.args.get("generator", "loguniform").lower()
    n = int(clamp(request.args.get("n", 5000), 100, 200000))

    if generator not in ("uniform", "loguniform", "exponential"):
        return jsonify({"error": "generator must be one of: uniform, loguniform, exponential"}), 400

    def sample_value():
        if generator == "uniform":
            return random.uniform(1.0, 1_000_000.0)
        elif generator == "loguniform":
            # 10 ** U(0, 6) gives log-uniform across decades 1..1e6
            return 10.0 ** random.uniform(0.0, 6.0)
        else:  # exponential
            u = 1.0 - random.random()
            return -math.log(u)

    counts = {d: 0 for d in range(1, 10)}
    used = 0
    for _ in range(n):
        x = sample_value()
        d = first_significant_digit(x)
        if d is not None:
            counts[d] += 1
            used += 1

    expected = {d: math.log10(1 + 1/d) for d in range(1, 10)}
    expected_counts = {d: expected[d] * used for d in range(1, 10)}

    # Chi-square statistic for goodness-of-fit to Benford
    chi2 = 0.0
    for d in range(1, 10):
        e = expected_counts[d]
        o = counts[d]
        if e > 0:
            chi2 += (o - e) ** 2 / e

    return jsonify({
        "generator": generator,
        "n": used,
        "counts": counts,
        "expected": expected,
        "chi_square": chi2
    })

@app.route("/api/lln")
def api_lln():
    flips = int(clamp(request.args.get("flips", 1000), 10, 5000))
    p = clamp(request.args.get("p", 0.5), 0.0, 1.0)

    running = []
    heads = 0
    for i in range(1, flips + 1):
        if random.random() < p:
            heads += 1
        running.append(heads / i)

    # downsample if too long to reduce payload
    if len(running) > 1500:
        step = len(running) // 1500
        running = [running[i] for i in range(0, len(running), step)]
    return jsonify({
        "p": p,
        "flips": flips,
        "running_mean": running
    })

if __name__ == "__main__":
    app.run(debug=True)
