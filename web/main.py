"""FastAPI web UI (Tailwind) + JSON APIs sharing planner_core calculations."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from planner_core.services import (
    amortization_schedule,
    calc_investment_retirement_rows,
    fd_mf_savings_comparison,
    fd_net_metrics,
    monthly_emi,
    payoff_invest_comparison,
)
from web.chart_helpers import (
    fd_mf_comparison_chart,
    fd_waterfall_chart,
    investment_scenarios_chart,
    mortgage_balance_line,
    mortgage_interest_compare_chart,
    payoff_comparison_chart,
)
from web.routes_extended import router as extended_router

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app = FastAPI(
    title="Financial Planner (India)",
    description="Calculators for investments, loans, FD, goals, and Monte Carlo. Not financial advice.",
    version="3.0.0",
)
app.include_router(extended_router)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
        {"title": "Financial Planner"},
    )


@app.get("/investment", response_class=HTMLResponse)
async def investment_page(request: Request):
    return templates.TemplateResponse(request, "investment.html", {"rows": None})


@app.post("/investment", response_class=HTMLResponse)
async def investment_post(request: Request):
    form = await request.form()
    current_age = int(form.get("current_age", 35))
    retirement_age = int(form.get("retirement_age", 60))
    month_inv = float(form.get("month_inv", 10000))
    yearly_inc = float(form.get("yearly_inc", 6))
    inflation = float(form.get("inflation", 6))
    nper = max(0, (retirement_age - current_age) * 12)
    scheme_ret = {
        "FD/RD": 5,
        "Gold": 10,
        "Equity/MF": 15,
        "High Risk Equity": 20,
        "Very High Risk Equity": 25,
        "Extreme Risk Equity": 30,
    }
    rows = calc_investment_retirement_rows(
        month_inv, yearly_inc / 100, inflation / 100, scheme_ret, nper
    )
    ch = investment_scenarios_chart(rows)
    return templates.TemplateResponse(
        request,
        "investment.html",
        {
            "rows": rows,
            "current_age": current_age,
            "retirement_age": retirement_age,
            "month_inv": month_inv,
            "yearly_inc": yearly_inc,
            "inflation": inflation,
            "chart_json": ch,
        },
    )


@app.get("/mortgage", response_class=HTMLResponse)
async def mortgage_page(request: Request):
    return templates.TemplateResponse(
        request,
        "mortgage.html",
        {"schedule": None, "metrics": None},
    )


@app.post("/mortgage", response_class=HTMLResponse)
async def mortgage_post(request: Request):
    form = await request.form()
    loan_amount = float(form.get("loan_amount", 0))
    loan_term = int(form.get("loan_term", 30))
    interest_rate = float(form.get("interest_rate", 0))
    monthly_prepayment = float(form.get("monthly_prepayment", 0) or 0)
    yearly_prepayment = float(form.get("yearly_prepayment", 0) or 0)
    onetime_payment = float(form.get("onetime_payment", 0) or 0)
    onetime_year = int(form.get("onetime_year", 0) or 0)

    emi = monthly_emi(loan_amount, interest_rate, loan_term)
    n = loan_term * 12
    total_interest_nominal = emi * n - loan_amount if n else 0

    sch, tot_int_p, months_p, _ = amortization_schedule(
        loan_amount,
        interest_rate,
        loan_term,
        monthly_prepayment,
        yearly_prepayment,
        onetime_payment,
        onetime_year,
    )
    _, tot_int_b, months_b, _ = amortization_schedule(loan_amount, interest_rate, loan_term, 0, 0, 0, 0)

    has_prepay = monthly_prepayment > 0 or yearly_prepayment > 0 or onetime_payment > 0
    metrics = {
        "emi": emi,
        "total_interest_nominal": total_interest_nominal,
        "total_repayment_nominal": emi * n,
        "interest_saved": tot_int_b - tot_int_p,
        "months_saved": months_b - months_p,
        "has_prepay": has_prepay,
        "tot_int_base": tot_int_b,
        "months_base": months_b,
        "tot_int_prepay": tot_int_p,
        "months_prepay": months_p,
    }
    ch_line = mortgage_balance_line(sch)
    ch_int = (
        mortgage_interest_compare_chart(tot_int_b, tot_int_p)
        if has_prepay and tot_int_p < tot_int_b - 1e-6
        else None
    )
    return templates.TemplateResponse(
        request,
        "mortgage.html",
        {
            "schedule": sch[:360],
            "schedule_truncated": len(sch) > 360,
            "metrics": metrics,
            "loan_amount": loan_amount,
            "loan_term": loan_term,
            "interest_rate": interest_rate,
            "monthly_prepayment": monthly_prepayment,
            "yearly_prepayment": yearly_prepayment,
            "onetime_payment": onetime_payment,
            "onetime_year": onetime_year,
            "chart_json": ch_line,
            "chart_json_b": ch_int,
        },
    )


@app.get("/fd", response_class=HTMLResponse)
async def fd_page(request: Request):
    return templates.TemplateResponse(request, "fd.html", {"m": None})


@app.post("/fd", response_class=HTMLResponse)
async def fd_post(request: Request):
    form = await request.form()
    principal = float(form.get("principal", 100000))
    rate = float(form.get("rate", 6))
    months = int(form.get("months", 12))
    tax_slab = float(form.get("tax_slab", 30))
    m = fd_net_metrics(
        principal,
        rate,
        months,
        tax_slab,
        is_senior_citizen="fd_sc" in form,
        interest_payer="other" if "fd_other" in form else "bank",
    )
    ch = fd_waterfall_chart(principal, m["interest_gross"], m["tax_on_interest"], m["net_interest"])
    return templates.TemplateResponse(
        request,
        "fd.html",
        {
            "m": m,
            "principal": principal,
            "rate": rate,
            "months": months,
            "tax_slab": tax_slab,
            "fd_sc": "fd_sc" in form,
            "fd_other": "fd_other" in form,
            "chart_json": ch,
        },
    )


@app.get("/payoff", response_class=HTMLResponse)
async def payoff_page(request: Request):
    return templates.TemplateResponse(request, "payoff.html", {"res": None})


@app.post("/payoff", response_class=HTMLResponse)
async def payoff_post(request: Request):
    form = await request.form()
    res = payoff_invest_comparison(
        float(form.get("loan_remaining", 0)),
        float(form.get("interest", 0)),
        int(form.get("months_remaining", 0)),
        float(form.get("lumpsum", 0)),
        float(form.get("add_inv", 0)),
        float(form.get("yr_return", 0)),
    )
    form_data = dict(form)
    ch = payoff_comparison_chart(res)
    return templates.TemplateResponse(
        request,
        "payoff.html",
        {"res": res, "chart_json": ch, **form_data},
    )


@app.get("/fd-mf", response_class=HTMLResponse)
async def fd_mf_page(request: Request):
    return templates.TemplateResponse(request, "fd_mf.html", {"cmp": None})


@app.post("/fd-mf", response_class=HTMLResponse)
async def fd_mf_post(request: Request):
    form = await request.form()
    cmp = fd_mf_savings_comparison(
        float(form.get("principal", 0)),
        int(form.get("months", 12)),
        float(form.get("tax_slab", 30)),
        float(form.get("fd_rate", 6)),
        float(form.get("mf_cagr", 5)),
        float(form.get("savings_rate", 4.5)),
    )
    form_data = dict(form)
    ch = fd_mf_comparison_chart(cmp)
    return templates.TemplateResponse(
        request,
        "fd_mf.html",
        {"cmp": cmp, "chart_json": ch, **form_data},
    )


# --- JSON API ---


class InvestmentIn(BaseModel):
    current_age: int = Field(35, ge=15, le=100)
    retirement_age: int = Field(60, ge=35, le=100)
    month_inv: float = Field(10000, ge=0)
    yearly_inc_pct: float = Field(6, ge=0)
    inflation_pct: float = Field(6, ge=0)


@app.post("/api/investment")
async def api_investment(body: InvestmentIn):
    nper = max(0, (body.retirement_age - body.current_age) * 12)
    scheme_ret = {
        "FD/RD": 5,
        "Gold": 10,
        "Equity/MF": 15,
        "High Risk Equity": 20,
        "Very High Risk Equity": 25,
        "Extreme Risk Equity": 30,
    }
    rows = calc_investment_retirement_rows(
        body.month_inv,
        body.yearly_inc_pct / 100,
        body.inflation_pct / 100,
        scheme_ret,
        nper,
    )
    return {"months": nper, "scenarios": rows}


class MortgageIn(BaseModel):
    loan_amount: float = Field(..., ge=0)
    loan_term_years: int = Field(30, ge=1, le=50)
    interest_rate_pct: float = Field(..., ge=0)
    monthly_prepayment: float = 0
    yearly_prepayment: float = 0
    onetime_payment: float = 0
    onetime_payment_year: int = 0


@app.post("/api/mortgage")
async def api_mortgage(body: MortgageIn):
    emi = monthly_emi(body.loan_amount, body.interest_rate_pct, body.loan_term_years)
    sch, ti_p, mp, _ = amortization_schedule(
        body.loan_amount,
        body.interest_rate_pct,
        body.loan_term_years,
        body.monthly_prepayment,
        body.yearly_prepayment,
        body.onetime_payment,
        body.onetime_payment_year,
    )
    _, ti_b, mb, _ = amortization_schedule(
        body.loan_amount, body.interest_rate_pct, body.loan_term_years, 0, 0, 0, 0
    )
    return {
        "emi": emi,
        "schedule_months": len(sch),
        "total_interest_with_prepay": ti_p,
        "total_interest_baseline": ti_b,
        "interest_saved": ti_b - ti_p,
        "tenure_months_with_prepay": mp,
        "tenure_months_baseline": mb,
        "schedule_preview": sch[:60],
    }


class FdIn(BaseModel):
    principal: float = Field(..., ge=0)
    rate_pct: float = Field(..., ge=0)
    months: int = Field(..., ge=1)
    tax_slab_pct: float = Field(30, ge=0, le=100)
    is_senior_citizen: bool = False
    interest_payer: Literal["bank", "other"] = "bank"


@app.post("/api/fd")
async def api_fd(body: FdIn):
    return fd_net_metrics(
        body.principal,
        body.rate_pct,
        body.months,
        body.tax_slab_pct,
        is_senior_citizen=body.is_senior_citizen,
        interest_payer=body.interest_payer,
    )
