"""Additional calculator routes (FastAPI)."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from planner_core.extended import (
    credit_card_months_to_payoff,
    education_goal_sip,
    emergency_fund_plan,
    epf_projected_corpus,
    fv_of_sip,
    monte_carlo_retirement_corpus,
    nps_projected_corpus,
    personal_loan_summary,
    ppf_maturity_estimate,
    real_return_pct,
    rent_vs_buy_snapshot,
    senior_interest_tds_note,
    sip_monthly_for_target,
    swp_months_until_depleted,
)
from web.chart_helpers import (
    credit_card_line,
    education_goal_chart,
    emergency_chart,
    monte_carlo_band_chart,
    personal_loan_interest_chart,
    real_return_bar,
    rent_buy_chart,
    retirement_three_pillar_chart,
    senior_tds_gauge_chart,
    sip_goal_line_chart,
    swp_line_chart,
)

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter(tags=["extended"])


def _form(req: Request, name: str, ctx: dict):
    pretty = (
        name.removesuffix(".html").replace("-", " ").replace("_", " ").title()
    )
    ctx = {k: v for k, v in ctx.items() if k != "request"}
    ctx.setdefault("title", pretty)
    return templates.TemplateResponse(req, name, ctx)


@router.get("/sip-goal", response_class=HTMLResponse)
async def sip_goal_get(request: Request):
    return _form(request, "sip_goal.html", {"sip": None})


@router.post("/sip-goal", response_class=HTMLResponse)
async def sip_goal_post(request: Request):
    f = dict(await request.form())
    target = float(f.get("target", 0))
    months = int(float(f.get("months", 120)))
    ret = float(f.get("ret", 12))
    lump = float(f.get("lump", 0))
    sip = sip_monthly_for_target(target, months, ret, lump)
    pm = float(f.get("pm", 0))
    step = float(f.get("step", 0))
    fv = fv_of_sip(pm, months, ret, lump, step)
    ch = sip_goal_line_chart(months, lump, pm, ret, step)
    return _form(request, "sip_goal.html", {**f, "sip": sip, "fv_proj": fv, "chart_json": ch})


@router.get("/emergency", response_class=HTMLResponse)
async def em_get(request: Request):
    return _form(request, "emergency.html", {"plan": None})


@router.post("/emergency", response_class=HTMLResponse)
async def em_post(request: Request):
    f = dict(await request.form())
    plan = emergency_fund_plan(
        float(f.get("exp_m", 0)),
        float(f.get("buf", 6)),
        float(f.get("cur", 0)),
        float(f.get("add_m", 0)),
        float(f.get("yield_pct", 6)),
    )
    ch = emergency_chart(
        float(plan["target_corpus"]),
        float(f.get("cur", 0)),
        float(f.get("add_m", 0)),
        float(f.get("yield_pct", 6)),
    )
    return _form(request, "emergency.html", {**f, "plan": plan, "chart_json": ch})


@router.get("/rent-buy", response_class=HTMLResponse)
async def rb_get(request: Request):
    return _form(request, "rent_buy.html", {"snap": None})


@router.post("/rent-buy", response_class=HTMLResponse)
async def rb_post(request: Request):
    f = dict(await request.form())
    snap = rent_vs_buy_snapshot(
        int(float(f.get("H", 15))),
        float(f.get("price", 0)),
        float(f.get("down_pct", 20)),
        float(f.get("loan_r", 8.5)),
        int(float(f.get("loan_y", 20))),
        float(f.get("app", 5)),
        float(f.get("maint", 1)),
        float(f.get("rent0", 0)),
        float(f.get("rent_g", 5)),
        float(f.get("alt", 10)),
    )
    ch = rent_buy_chart(snap)
    return _form(request, "rent_buy.html", {**f, "snap": snap, "chart_json": ch})


@router.get("/retirement-accounts", response_class=HTMLResponse)
async def ra_get(request: Request):
    return _form(request, "retirement_accounts.html", {"epf": None, "nps": None, "ppf": None})


@router.post("/retirement-accounts", response_class=HTMLResponse)
async def ra_post(request: Request):
    f = dict(await request.form())
    epf = epf_projected_corpus(
        float(f.get("epf_sb", 0)),
        float(f.get("epf_ee", 0)),
        float(f.get("epf_er", 0)),
        float(f.get("epf_i", 8)),
        float(f.get("epf_y", 15)),
        float(f.get("epf_sg", 0)),
    )
    nps = nps_projected_corpus(
        float(f.get("nps_m", 0)),
        float(f.get("nps_y", 20)),
        float(f.get("nps_r", 10)),
        float(f.get("nps_e", 0.09)),
    )
    ppf = ppf_maturity_estimate(float(f.get("ppf_yd", 0)), float(f.get("ppf_r", 7)), int(float(f.get("ppf_y", 15))))
    ch = retirement_three_pillar_chart(epf["corpus"], nps["corpus"], ppf["corpus"])
    return _form(
        request,
        "retirement_accounts.html",
        {**f, "epf": epf, "nps": nps, "ppf": ppf, "chart_json": ch},
    )


@router.get("/debt", response_class=HTMLResponse)
async def debt_get(request: Request):
    return _form(request, "debt.html", {"cc": None, "pl": None})


@router.post("/debt", response_class=HTMLResponse)
async def debt_post(request: Request):
    f = dict(await request.form())
    cc_b = float(f.get("cc_b", 0))
    cc_a = float(f.get("cc_a", 36))
    cc_p = float(f.get("cc_p", 0))
    pl_p = float(f.get("pl_p", 0))
    cc = credit_card_months_to_payoff(cc_b, cc_a, cc_p)
    pl = personal_loan_summary(pl_p, float(f.get("pl_r", 14)), int(float(f.get("pl_m", 36))))
    ch_cc = credit_card_line(cc_b, cc_a, cc_p)
    ch_pl = personal_loan_interest_chart(pl_p, pl["total_paid"]) if pl_p > 0 else None
    return _form(
        request,
        "debt.html",
        {**f, "cc": cc, "pl": pl, "chart_json_cc": ch_cc, "chart_json_pl": ch_pl},
    )


@router.get("/utilities", response_class=HTMLResponse)
async def util_get(request: Request):
    return _form(
        request,
        "utilities.html",
        {"sen": None, "rr": None, "swp": None, "senior_checked": True},
    )


@router.post("/utilities", response_class=HTMLResponse)
async def util_post(request: Request):
    f = dict(await request.form())
    sen = senior_interest_tds_note(float(f.get("sen_ai", 0)), "sen_sc" in f)
    rr = real_return_pct(float(f.get("rr_n", 0)), float(f.get("rr_i", 6)))
    swp = swp_months_until_depleted(
        float(f.get("swp_c", 0)),
        float(f.get("swp_w", 0)),
        float(f.get("swp_r", 8)),
        float(f.get("swp_inf", 0)),
    )
    ch_sen = senior_tds_gauge_chart(sen["annual_interest"], sen["tds_threshold"])
    ch_rr = real_return_bar(float(f.get("rr_n", 0)), float(f.get("rr_i", 6)), rr)
    ch_swp = swp_line_chart(
        float(f.get("swp_c", 0)),
        float(f.get("swp_w", 0)),
        float(f.get("swp_r", 8)),
        float(f.get("swp_inf", 0)),
    )
    return _form(
        request,
        "utilities.html",
        {
            **f,
            "sen": sen,
            "rr": rr,
            "swp": swp,
            "senior_checked": "sen_sc" in f,
            "chart_json_sen": ch_sen,
            "chart_json_rr": ch_rr,
            "chart_json_swp": ch_swp,
        },
    )


@router.get("/education-goal", response_class=HTMLResponse)
async def edu_get(request: Request):
    return _form(request, "education_goal.html", {"eg": None})


@router.post("/education-goal", response_class=HTMLResponse)
async def edu_post(request: Request):
    f = dict(await request.form())
    eg = education_goal_sip(
        float(f.get("today", 0)),
        float(f.get("yrs", 10)),
        float(f.get("einfl", 10)),
        float(f.get("inv_r", 12)),
        float(f.get("cur", 0)),
    )
    ch = education_goal_chart(eg["nominal_goal"], float(f.get("cur", 0)))
    return _form(request, "education_goal.html", {**f, "eg": eg, "chart_json": ch})


@router.get("/monte-carlo", response_class=HTMLResponse)
async def mc_get(request: Request):
    return _form(request, "monte_carlo.html", {"mc": None})


@router.post("/monte-carlo", response_class=HTMLResponse)
async def mc_post(request: Request):
    f = dict(await request.form())
    mc = monte_carlo_retirement_corpus(
        float(f.get("init", 0)),
        float(f.get("pm", 0)),
        int(float(f.get("mo", 240))),
        float(f.get("mu", 11)),
        float(f.get("sig", 15)),
        int(float(f.get("paths", 500))),
        int(float(f.get("seed", 42))),
    )
    ch = monte_carlo_band_chart(mc)
    return _form(request, "monte_carlo.html", {**f, "mc": mc, "chart_json": ch})


# --- JSON ---


class SipGoalIn(BaseModel):
    target: float = Field(..., ge=0)
    months: int = Field(120, ge=1)
    annual_return_pct: float = Field(12, ge=0)
    lump_now: float = 0


@router.post("/api/sip-goal")
async def api_sip_goal(body: SipGoalIn):
    return sip_monthly_for_target(body.target, body.months, body.annual_return_pct, body.lump_now)


class EmergencyIn(BaseModel):
    monthly_expenses: float = Field(..., ge=0)
    target_months: float = Field(6, ge=0.5, le=60)
    current_savings: float = 0
    monthly_contribution: float = 0
    savings_yield_annual_pct: float = Field(6, ge=0)


@router.post("/api/emergency-fund")
async def api_emergency(body: EmergencyIn):
    return emergency_fund_plan(
        body.monthly_expenses,
        body.target_months,
        body.current_savings,
        body.monthly_contribution,
        body.savings_yield_annual_pct,
    )


class MonteCarloIn(BaseModel):
    initial: float = 0
    monthly_contribution: float = 0
    months: int = Field(240, ge=1)
    mean_annual_return_pct: float = Field(11, ge=0)
    volatility_annual_pct: float = Field(15, ge=0.1)
    n_paths: int = Field(500, ge=50, le=5000)
    seed: int = 42


@router.post("/api/monte-carlo")
async def api_mc(body: MonteCarloIn):
    return monte_carlo_retirement_corpus(
        body.initial,
        body.monthly_contribution,
        body.months,
        body.mean_annual_return_pct,
        body.volatility_annual_pct,
        body.n_paths,
        body.seed,
    )
