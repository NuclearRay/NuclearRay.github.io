from flask import Flask, render_template, request, session, redirect, url_for
from typing import List, Dict, Tuple

from currency_optimizer import (
    CurrencyOptimizer,
    CurrencyPackage,
    create_common_packages,
)

app = Flask(__name__)
app.secret_key = "dev-secret-change-me"


def _deserialize_custom_packages() -> List[CurrencyPackage]:
    entries = session.get("custom_packages", [])
    packages: List[CurrencyPackage] = []
    for e in entries:
        try:
            packages.append(CurrencyPackage(float(e["cost"]), int(e["currency"]), e.get("name", "Custom")))
        except Exception:
            continue
    return packages


def get_packages_from_form() -> List[CurrencyPackage]:
    preset = (request.form.get("preset") or request.args.get("preset") or "").strip()
    preset = preset if preset else None
    if preset == "custom":
        pkgs = _deserialize_custom_packages()
        return pkgs if pkgs else create_common_packages(None)
    return create_common_packages(preset)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/optimize", methods=["GET", "POST"])
def optimize():
    result = None
    packages = get_packages_from_form() if request.method == "POST" else create_common_packages()
    preset = request.form.get("preset") if request.method == "POST" else None

    if request.method == "POST":
        try:
            target = int(request.form.get("target", "0"))
            optimizer = CurrencyOptimizer(packages)
            cost, solution = optimizer.find_optimal_purchase_unbounded(target)
            total_currency = sum(pkg.currency_amount * qty for pkg, qty in solution.items())
            efficiency = (total_currency / cost) if cost > 0 else 0
            plan = [
                {
                    "name": pkg.name,
                    "cost": pkg.cost,
                    "qty": qty,
                    "coins": pkg.currency_amount * qty,
                    "subtotal": pkg.cost * qty,
                }
                for pkg, qty in solution.items()
                if qty > 0
            ]
            result = {
                "target": target,
                "cost": cost,
                "total_currency": total_currency,
                "efficiency": efficiency,
                "plan": plan,
            }
        except Exception as e:
            result = {"error": str(e)}

    return render_template("optimize.html", result=result, preset=preset, packages=packages)


@app.route("/exact", methods=["GET", "POST"])
def exact():
    result = None
    packages = get_packages_from_form() if request.method == "POST" else create_common_packages()
    preset = request.form.get("preset") if request.method == "POST" else None

    if request.method == "POST":
        try:
            target = int(request.form.get("target", "0"))
            max_k = int(request.form.get("max_k", "100"))
            optimizer = CurrencyOptimizer(packages)
            k, cost, solution = optimizer.find_exact_or_scaled(target, max_multiplier=max_k)
            if k == 0 or cost is None:
                result = {"no_solution": True, "target": target, "max_k": max_k}
            else:
                exact_target = k * target
                plan = [
                    {
                        "name": pkg.name,
                        "cost": pkg.cost,
                        "qty": qty,
                        "coins": pkg.currency_amount * qty,
                        "subtotal": pkg.cost * qty,
                    }
                    for pkg, qty in solution.items()
                    if qty > 0
                ]
                total_currency = sum(p["coins"] for p in plan)
                efficiency = (total_currency / cost) if cost > 0 else 0
                result = {
                    "target": target,
                    "k": k,
                    "exact_target": exact_target,
                    "cost": cost,
                    "efficiency": efficiency,
                    "plan": plan,
                }
        except Exception as e:
            result = {"error": str(e)}

    return render_template("exact.html", result=result, preset=preset, packages=packages)


@app.route("/spend", methods=["GET", "POST"])
def spend():
    result = None
    preset = request.form.get("preset") if request.method == "POST" else None

    if request.method == "POST":
        try:
            budget = int(request.form.get("budget", "0"))
            costs_raw = request.form.get("costs", "").strip()
            costs = [int(x) for x in costs_raw.split(',') if x.strip()]
            mode = (request.form.get("repeatable", "y").lower() or 'y').startswith('y')

            optimizer = CurrencyOptimizer(create_common_packages(preset))
            if mode:
                spent, counts = optimizer.optimize_spend_unbounded(budget, costs)
            else:
                spent, counts = optimizer.optimize_spend_01(budget, costs)

            plan = [{"cost": c, "qty": q, "subtotal": c * q} for c, q in sorted(counts.items(), reverse=True)]
            result = {
                "budget": budget,
                "spent": spent,
                "leftover": budget - spent,
                "plan": plan,
                "repeatable": mode,
                "costs": costs_raw,
            }
        except Exception as e:
            result = {"error": str(e)}

    return render_template("spend.html", result=result, preset=preset)


@app.route("/analyze", methods=["GET", "POST"])
def analyze():
    packages = get_packages_from_form() if request.method == "POST" else create_common_packages()
    preset = request.form.get("preset") if request.method == "POST" else None
    optimizer = CurrencyOptimizer(packages)
    analysis = optimizer.analyze_packages()
    return render_template("analyze.html", analysis=analysis, preset=preset)


@app.route("/custom", methods=["GET", "POST"])
def custom():
    # Stored as list of dicts: {name, cost, currency}
    if request.method == "POST":
        action = request.form.get("action")
        items = session.get("custom_packages", [])

        if action == "add":
            try:
                name = request.form.get("name", "Custom Package").strip() or "Custom Package"
                cost = float(request.form.get("cost", "0"))
                currency = int(request.form.get("currency", "0"))
                if cost > 0 and currency > 0:
                    items.append({"name": name, "cost": cost, "currency": currency})
                    session["custom_packages"] = items
            except Exception:
                pass
        elif action == "remove":
            try:
                idx = int(request.form.get("index", "-1"))
                if 0 <= idx < len(items):
                    items.pop(idx)
                    session["custom_packages"] = items
            except Exception:
                pass
        elif action == "clear":
            session["custom_packages"] = []

        return redirect(url_for("custom"))

    # GET
    items = session.get("custom_packages", [])
    return render_template("custom.html", items=items)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
