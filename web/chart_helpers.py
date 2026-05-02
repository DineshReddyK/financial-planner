"""Build Chart.js configs (JSON-serializable) for calculator pages."""

from __future__ import annotations

import json
from typing import Any

_EMERALD = "#34d399"
_SLATE = "#94a3b8"
_GRID = "rgba(51,65,85,0.45)"


def _dark_options(*, y_title: str | None = None, x_title: str | None = None, legend: bool = True) -> dict[str, Any]:
    scales: dict[str, Any] = {}
    if x_title or True:
        scales["x"] = {
            "ticks": {"color": _SLATE, "maxRotation": 45, "minRotation": 0},
            "grid": {"color": _GRID},
            "title": {"display": bool(x_title), "text": x_title or "", "color": _SLATE},
        }
    scales["y"] = {
        "ticks": {"color": _SLATE},
        "grid": {"color": _GRID},
        "title": {"display": bool(y_title), "text": y_title or "", "color": _SLATE},
    }
    return {
        "responsive": True,
        "maintainAspectRatio": False,
        "plugins": {
            "legend": {"display": legend, "labels": {"color": "#cbd5e1"}},
            "tooltip": {
                "titleColor": "#f8fafc",
                "bodyColor": "#e2e8f0",
                "backgroundColor": "#0f172a",
                "borderColor": "#334155",
                "borderWidth": 1,
            },
        },
        "scales": scales,
    }


def dumps_chart(cfg: dict[str, Any]) -> str:
    return json.dumps(cfg, separators=(",", ":"))


def investment_scenarios_chart(rows: list[dict[str, Any]]) -> str | None:
    if not rows:
        return None
    labels = [str(r.get("Investment", ""))[:22] for r in rows]
    adj = [float(r.get("Actual Amount Value", 0) or 0) for r in rows]
    nom = [float(r.get("Amount Earned", 0) or 0) for r in rows]
    cfg = {
        "type": "bar",
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "label": "Inflation-adjusted (₹)",
                    "data": adj,
                    "backgroundColor": "rgba(52,211,153,0.75)",
                    "borderColor": _EMERALD,
                    "borderWidth": 1,
                },
                {
                    "label": "Nominal FV (₹)",
                    "data": nom,
                    "backgroundColor": "rgba(148,163,184,0.5)",
                    "borderColor": "#64748b",
                    "borderWidth": 1,
                },
            ],
        },
        "options": _dark_options(y_title="Amount (₹)", x_title="Scenario"),
    }
    return dumps_chart(cfg)


def mortgage_balance_line(schedule: list[dict[str, Any]]) -> str | None:
    if not schedule:
        return None
    by_year: dict[int, float] = {}
    for row in schedule:
        by_year[int(row["Year"])] = float(row["Remaining Balance"])
    years = sorted(by_year.keys())
    data = [by_year[y] for y in years]
    cfg = {
        "type": "line",
        "data": {
            "labels": [f"Y{y}" for y in years],
            "datasets": [
                {
                    "label": "Loan balance (₹)",
                    "data": data,
                    "borderColor": _EMERALD,
                    "backgroundColor": "rgba(52,211,153,0.15)",
                    "fill": True,
                    "tension": 0.25,
                    "pointRadius": 2,
                }
            ],
        },
        "options": _dark_options(y_title="Balance (₹)", x_title="Loan year"),
    }
    return dumps_chart(cfg)


def mortgage_interest_compare_chart(tot_base: float, tot_prepay: float) -> str | None:
    if tot_base <= 0 and tot_prepay <= 0:
        return None
    cfg = {
        "type": "bar",
        "data": {
            "labels": ["Total interest paid"],
            "datasets": [
                {
                    "label": "Baseline (no prepay)",
                    "data": [tot_base],
                    "backgroundColor": "rgba(148,163,184,0.55)",
                },
                {
                    "label": "With prepayments",
                    "data": [tot_prepay],
                    "backgroundColor": "rgba(52,211,153,0.75)",
                },
            ],
        },
        "options": _dark_options(y_title="Interest (₹)", legend=True),
    }
    return dumps_chart(cfg)


def fd_waterfall_chart(principal: float, interest_gross: float, tax: float, net_int: float) -> str | None:
    cfg = {
        "type": "bar",
        "data": {
            "labels": ["Principal", "Gross interest", "Tax on interest", "Net interest"],
            "datasets": [
                {
                    "label": "₹",
                    "data": [principal, interest_gross, tax, net_int],
                    "backgroundColor": [
                        "rgba(148,163,184,0.6)",
                        "rgba(52,211,153,0.7)",
                        "rgba(251,191,36,0.55)",
                        "rgba(52,211,153,0.9)",
                    ],
                }
            ],
        },
        "options": {**_dark_options(y_title="₹", legend=False)},
    }
    return dumps_chart(cfg)


def payoff_comparison_chart(res: dict[str, Any]) -> str | None:
    ti = float(res.get("total_remaining_interest") or 0)
    profit = float(res.get("investment_profit") or 0)
    fv = float(res.get("investment_fv") or 0)
    cfg = {
        "type": "bar",
        "data": {
            "labels": ["Loan interest (remaining)", "Investment profit", "Investment FV"],
            "datasets": [
                {
                    "label": "₹",
                    "data": [ti, profit, fv],
                    "backgroundColor": [
                        "rgba(251,113,133,0.65)",
                        "rgba(52,211,153,0.75)",
                        "rgba(56,189,248,0.55)",
                    ],
                }
            ],
        },
        "options": _dark_options(y_title="Amount (₹)", legend=False),
    }
    return dumps_chart(cfg)


def fd_mf_comparison_chart(cmp: dict[str, Any]) -> str | None:
    fd_n = float(cmp["fd"]["net_interest"])
    mf_n = float(cmp["mf"]["net_returns"])
    s_n = float(cmp["savings"]["net_interest"])
    cfg = {
        "type": "bar",
        "data": {
            "labels": ["Fixed deposit", "Mutual fund", "Savings"],
            "datasets": [
                {
                    "label": "After-tax return (₹)",
                    "data": [fd_n, mf_n, s_n],
                    "backgroundColor": [
                        "rgba(52,211,153,0.75)",
                        "rgba(56,189,248,0.65)",
                        "rgba(148,163,184,0.55)",
                    ],
                }
            ],
        },
        "options": _dark_options(y_title="Net return (₹)", legend=False),
    }
    return dumps_chart(cfg)


def _sip_balance_series(
    months: int,
    lump: float,
    pmt: float,
    annual_ret: float,
    step_pct: float,
) -> list[float]:
    if months <= 0:
        return []
    r = annual_ret / 100 / 12
    series: list[float] = []
    fv = lump
    pm = pmt
    m_in_year = 0
    for m in range(1, months + 1):
        fv = fv * (1 + r) + pm
        series.append(fv)
        m_in_year += 1
        if m_in_year >= 12 and m < months:
            pm *= 1 + step_pct / 100
            m_in_year = 0
    return series


def sip_goal_line_chart(months: int, lump: float, pm: float, ret: float, step: float) -> str | None:
    if months <= 0:
        return None
    raw = _sip_balance_series(months, lump, pm, ret, step)
    if not raw:
        return None
    stride = max(1, months // 48)
    labels = [str(i) for i in range(stride, months + 1, stride)]
    data = [raw[i - 1] for i in range(stride, months + 1, stride)]
    if months % stride != 0:
        labels.append(str(months))
        data.append(raw[-1])
    cfg = {
        "type": "line",
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "label": "Projected corpus (₹)",
                    "data": data,
                    "borderColor": _EMERALD,
                    "backgroundColor": "rgba(52,211,153,0.12)",
                    "fill": True,
                    "tension": 0.2,
                    "pointRadius": 0,
                }
            ],
        },
        "options": _dark_options(y_title="Corpus (₹)", x_title="Month"),
    }
    return dumps_chart(cfg)


def emergency_chart(
    target: float,
    cur: float,
    monthly_add: float,
    yield_pct: float,
) -> str | None:
    if target <= 0:
        return None
    if cur >= target:
        cfg = {
            "type": "bar",
            "data": {
                "labels": ["Target", "Saved"],
                "datasets": [{"label": "₹", "data": [target, cur], "backgroundColor": ["rgba(251,113,133,0.5)", "rgba(52,211,153,0.75)"]}],
            },
            "options": _dark_options(y_title="₹", legend=False),
        }
        return dumps_chart(cfg)
    if monthly_add <= 0:
        cfg = {
            "type": "bar",
            "data": {
                "labels": ["Saved", "Gap to target"],
                "datasets": [
                    {
                        "label": "₹",
                        "data": [cur, max(0.0, target - cur)],
                        "backgroundColor": ["rgba(148,163,184,0.65)", "rgba(251,191,36,0.55)"],
                    }
                ],
            },
            "options": _dark_options(y_title="₹", legend=False),
        }
        return dumps_chart(cfg)
    r = yield_pct / 100 / 12
    bal = cur
    labels: list[str] = ["0"]
    balances: list[float] = [bal]
    mo = 0
    while bal < target - 1e-6 and mo < 1200:
        mo += 1
        bal = bal * (1 + r) + monthly_add
        if mo <= 24 or mo % 3 == 0 or bal >= target - 1e-6:
            labels.append(str(mo))
            balances.append(min(bal, target))
    tgt_line = [target] * len(labels)
    cfg = {
        "type": "line",
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "label": "Savings balance (₹)",
                    "data": balances,
                    "borderColor": _EMERALD,
                    "backgroundColor": "rgba(52,211,153,0.15)",
                    "fill": True,
                    "tension": 0.15,
                },
                {
                    "label": "Target",
                    "data": tgt_line,
                    "borderColor": "#f87171",
                    "borderDash": [6, 4],
                    "pointRadius": 0,
                    "fill": False,
                },
            ],
        },
        "options": _dark_options(y_title="₹", x_title="Month"),
    }
    return dumps_chart(cfg)


def rent_buy_chart(snap: dict[str, Any]) -> str | None:
    b = float(snap.get("buyer_net_worth_end") or 0)
    r = float(snap.get("renter_net_worth_end") or 0)
    cfg = {
        "type": "bar",
        "data": {
            "labels": ["Buyer (home − loan)", "Renter (invested surplus)"],
            "datasets": [
                {
                    "label": "Terminal net worth (₹)",
                    "data": [b, r],
                    "backgroundColor": ["rgba(52,211,153,0.75)", "rgba(56,189,248,0.65)"],
                }
            ],
        },
        "options": _dark_options(y_title="₹", legend=False),
    }
    return dumps_chart(cfg)


def retirement_three_pillar_chart(epf_c: float, nps_c: float, ppf_c: float) -> str | None:
    cfg = {
        "type": "bar",
        "data": {
            "labels": ["EPF (illustr.)", "NPS (illustr.)", "PPF (illustr.)"],
            "datasets": [
                {
                    "label": "Corpus (₹)",
                    "data": [epf_c, nps_c, ppf_c],
                    "backgroundColor": [
                        "rgba(52,211,153,0.75)",
                        "rgba(56,189,248,0.65)",
                        "rgba(251,191,36,0.55)",
                    ],
                }
            ],
        },
        "options": _dark_options(y_title="₹", legend=False),
    }
    return dumps_chart(cfg)


def credit_card_balance_series(balance: float, apr_pct: float, payment: float) -> tuple[list[int], list[float]] | None:
    if balance <= 0 or payment <= 0:
        return None
    r = apr_pct / 100 / 12
    b = balance
    months: list[int] = []
    bals: list[float] = []
    months.append(0)
    bals.append(b)
    for mo in range(1, 601):
        int_ch = b * r
        princ = payment - int_ch
        if princ <= 0:
            return None
        b -= princ
        months.append(mo)
        bals.append(max(0.0, b))
        if b <= 0.01:
            break
    return months, bals


def credit_card_line(balance: float, apr_pct: float, payment: float) -> str | None:
    ser = credit_card_balance_series(balance, apr_pct, payment)
    if ser is None:
        return None
    labels_int, data = ser
    cfg = {
        "type": "line",
        "data": {
            "labels": [str(x) for x in labels_int],
            "datasets": [
                {
                    "label": "Outstanding balance (₹)",
                    "data": data,
                    "borderColor": "#fb7185",
                    "backgroundColor": "rgba(251,113,133,0.15)",
                    "fill": True,
                    "tension": 0.2,
                    "pointRadius": 0,
                }
            ],
        },
        "options": _dark_options(y_title="Balance (₹)", x_title="Month"),
    }
    return dumps_chart(cfg)


def personal_loan_interest_chart(principal: float, total_paid: float) -> str | None:
    if principal <= 0:
        return None
    interest = max(0.0, total_paid - principal)
    cfg = {
        "type": "doughnut",
        "data": {
            "labels": ["Principal", "Interest"],
            "datasets": [
                {
                    "data": [principal, interest],
                    "backgroundColor": ["rgba(148,163,184,0.75)", "rgba(251,191,36,0.65)"],
                    "borderColor": "#0f172a",
                    "borderWidth": 2,
                }
            ],
        },
        "options": {
            "responsive": True,
            "maintainAspectRatio": False,
            "plugins": {
                "legend": {"labels": {"color": "#cbd5e1"}},
                "tooltip": {
                    "titleColor": "#f8fafc",
                    "bodyColor": "#e2e8f0",
                    "backgroundColor": "#0f172a",
                },
            },
        },
    }
    return dumps_chart(cfg)


def swp_corpus_series(
    corpus: float,
    withdraw: float,
    ret_pct: float,
    infl_pct: float,
    max_months: int = 600,
) -> tuple[list[int], list[float]]:
    bal = corpus
    w = withdraw
    r = ret_pct / 100 / 12
    inf_m = infl_pct / 100 / 12
    labels: list[int] = [0]
    vals: list[float] = [max(0.0, bal)]
    step = max(1, max_months // 120)
    for mo in range(1, max_months + 1):
        bal = bal * (1 + r) - w
        w *= 1 + inf_m
        if mo % step == 0 or bal <= 0:
            labels.append(mo)
            vals.append(max(0.0, bal))
        if bal <= 0:
            break
    return labels, vals


def swp_line_chart(corpus: float, withdraw: float, ret_pct: float, infl_pct: float) -> str | None:
    if corpus <= 0:
        return None
    labels, vals = swp_corpus_series(corpus, withdraw, ret_pct, infl_pct)
    cfg = {
        "type": "line",
        "data": {
            "labels": [str(x) for x in labels],
            "datasets": [
                {
                    "label": "Corpus (₹)",
                    "data": vals,
                    "borderColor": _EMERALD,
                    "backgroundColor": "rgba(52,211,153,0.12)",
                    "fill": True,
                    "tension": 0.15,
                    "pointRadius": 0,
                }
            ],
        },
        "options": _dark_options(y_title="₹", x_title="Month"),
    }
    return dumps_chart(cfg)


def education_goal_chart(nominal_goal: float, current: float) -> str | None:
    cfg = {
        "type": "bar",
        "data": {
            "labels": ["Nominal goal", "Already saved"],
            "datasets": [
                {
                    "label": "₹",
                    "data": [nominal_goal, current],
                    "backgroundColor": ["rgba(52,211,153,0.85)", "rgba(148,163,184,0.65)"],
                }
            ],
        },
        "options": _dark_options(y_title="₹", legend=False),
    }
    return dumps_chart(cfg)


def monte_carlo_band_chart(mc: dict[str, Any]) -> str | None:
    cfg = {
        "type": "bar",
        "data": {
            "labels": ["10th percentile", "Median", "Mean", "90th percentile"],
            "datasets": [
                {
                    "label": "Ending corpus (₹)",
                    "data": [
                        float(mc.get("p10") or 0),
                        float(mc.get("median") or 0),
                        float(mc.get("mean") or 0),
                        float(mc.get("p90") or 0),
                    ],
                    "backgroundColor": [
                        "rgba(251,113,133,0.55)",
                        "rgba(52,211,153,0.85)",
                        "rgba(148,163,184,0.55)",
                        "rgba(56,189,248,0.55)",
                    ],
                }
            ],
        },
        "options": _dark_options(y_title="₹", legend=False),
    }
    return dumps_chart(cfg)


def senior_tds_gauge_chart(annual_interest: float, threshold: float) -> str | None:
    """Simple bar: interest vs threshold."""
    cfg = {
        "type": "bar",
        "data": {
            "labels": ["Annual interest", "TDS threshold (info)"],
            "datasets": [
                {
                    "label": "₹",
                    "data": [annual_interest, threshold],
                    "backgroundColor": ["rgba(52,211,153,0.65)", "rgba(148,163,184,0.45)"],
                }
            ],
        },
        "options": _dark_options(y_title="₹", legend=False),
    }
    return dumps_chart(cfg)


def real_return_bar(nominal: float, inflation: float, real_pct: float) -> str | None:
    cfg = {
        "type": "bar",
        "data": {
            "labels": ["Nominal %", "Inflation %", "Real % (Fisher)"],
            "datasets": [
                {
                    "label": "%",
                    "data": [nominal, inflation, real_pct],
                    "backgroundColor": [
                        "rgba(52,211,153,0.65)",
                        "rgba(251,191,36,0.55)",
                        "rgba(56,189,248,0.65)",
                    ],
                }
            ],
        },
        "options": _dark_options(y_title="Percent", legend=False),
    }
    return dumps_chart(cfg)


# ── Financial Planner ────────────────────────────────────────────────────────

_PALETTE = [
    "rgba(52,211,153,0.80)",   # emerald
    "rgba(56,189,248,0.75)",   # sky
    "rgba(167,139,250,0.75)",  # violet
    "rgba(251,191,36,0.75)",   # amber
    "rgba(148,163,184,0.55)",  # slate
]


def planner_allocation_doughnut(sip_rows: list[dict]) -> str | None:
    """Doughnut of monthly SIP allocation by category."""
    if not sip_rows:
        return None
    labels = [r["category"] for r in sip_rows]
    data = [r["monthly_sip"] for r in sip_rows]
    if sum(data) < 1:
        return None
    cfg = {
        "type": "doughnut",
        "data": {
            "labels": labels,
            "datasets": [{
                "data": data,
                "backgroundColor": _PALETTE[:len(labels)],
                "borderColor": "#0f172a",
                "borderWidth": 2,
            }],
        },
        "options": {
            "responsive": True,
            "maintainAspectRatio": False,
            "plugins": {
                "legend": {"display": True, "position": "right", "labels": {"color": "#cbd5e1", "padding": 12}},
                "tooltip": {
                    "titleColor": "#f8fafc",
                    "bodyColor": "#e2e8f0",
                    "backgroundColor": "#0f172a",
                    "borderColor": "#334155",
                    "borderWidth": 1,
                    "callbacks": {
                        "label": "function(c){return ' ₹'+c.parsed.toLocaleString('en-IN')}"
                    },
                },
            },
            "cutout": "62%",
        },
    }
    return dumps_chart(cfg)


def planner_corpus_chart(sip_rows: list[dict]) -> str | None:
    """Horizontal bar chart of projected corpus per category at retirement."""
    if not sip_rows:
        return None
    rows = sorted(sip_rows, key=lambda r: r["fv_total"], reverse=True)
    labels = [r["category"] for r in rows]
    fv_sip = [r["fv_sip"] for r in rows]
    fv_lump = [r["fv_lump"] for r in rows]
    opts = _dark_options(x_title="₹ at retirement", legend=True)
    opts["indexAxis"] = "y"
    opts["scales"]["x"]["ticks"]["callback"] = "function(v){return '₹'+Math.round(v/100000)/10+'L'}"
    cfg = {
        "type": "bar",
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "label": "From monthly SIP",
                    "data": fv_sip,
                    "backgroundColor": "rgba(52,211,153,0.70)",
                },
                {
                    "label": "From lumpsum",
                    "data": fv_lump,
                    "backgroundColor": "rgba(56,189,248,0.60)",
                },
            ],
        },
        "options": {**opts, "plugins": {**opts["plugins"], "legend": {"display": True, "labels": {"color": "#cbd5e1"}}}},
    }
    return dumps_chart(cfg)


def planner_cashflow_chart(income: float, essential: float, discretionary: float, emi: float, surplus: float) -> str | None:
    """Stacked bar showing income breakdown."""
    if income <= 0:
        return None
    cfg = {
        "type": "bar",
        "data": {
            "labels": ["Monthly cashflow"],
            "datasets": [
                {"label": "Essential expenses", "data": [essential], "backgroundColor": "rgba(251,113,133,0.70)"},
                {"label": "Discretionary", "data": [discretionary], "backgroundColor": "rgba(251,191,36,0.65)"},
                {"label": "EMI outgo", "data": [emi], "backgroundColor": "rgba(148,163,184,0.55)"},
                {"label": "Investable surplus", "data": [max(0.0, surplus)], "backgroundColor": "rgba(52,211,153,0.75)"},
            ],
        },
        "options": {
            **_dark_options(y_title="₹ / month", legend=True),
            "scales": {
                "x": {"stacked": True, "ticks": {"color": _SLATE}, "grid": {"color": _GRID}},
                "y": {"stacked": True, "ticks": {"color": _SLATE}, "grid": {"color": _GRID},
                      "title": {"display": True, "text": "₹ / month", "color": _SLATE}},
            },
        },
    }
    return dumps_chart(cfg)
