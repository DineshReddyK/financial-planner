"""Additional India-oriented calculators (illustrative; not tax/legal advice)."""

from __future__ import annotations

import math
from typing import Any

import numpy as np
import numpy_financial as npf

from planner_core.services import monthly_emi


def sip_monthly_for_target(
    target_corpus: float,
    months: int,
    annual_return_pct: float,
    lump_now: float = 0.0,
) -> dict[str, float]:
    """Constant monthly SIP (end-of-month) to reach target_corpus given lump_now grows at same rate."""
    if months <= 0:
        return {"monthly_sip": 0.0, "fv_from_lump": lump_now, "gap": max(0.0, target_corpus - lump_now)}
    r = annual_return_pct / 100 / 12
    fv_lump = float(lump_now * ((1 + r) ** months))
    gap = max(0.0, target_corpus - fv_lump)
    if gap <= 1e-9:
        return {"monthly_sip": 0.0, "fv_from_lump": fv_lump, "gap": 0.0}
    pmt = float(-npf.pmt(r, months, 0.0, -gap))
    return {"monthly_sip": pmt, "fv_from_lump": fv_lump, "gap": gap}


def fv_of_sip(
    monthly_payment: float,
    months: int,
    annual_return_pct: float,
    lump_now: float = 0.0,
    yearly_step_up_pct: float = 0.0,
) -> float:
    """FV with optional annual step-up on SIP amount."""
    if months <= 0:
        return lump_now
    r = annual_return_pct / 100 / 12
    fv = lump_now * ((1 + r) ** months)
    pmt = monthly_payment
    m_in_year = 0
    for m in range(1, months + 1):
        fv = fv * (1 + r) + pmt
        m_in_year += 1
        if m_in_year >= 12 and m < months:
            pmt *= 1 + yearly_step_up_pct / 100
            m_in_year = 0
    return float(fv)


def emergency_fund_plan(
    monthly_expenses: float,
    target_months: float,
    current_savings: float,
    monthly_contribution: float,
    savings_yield_annual_pct: float,
) -> dict[str, float]:
    target = monthly_expenses * target_months
    gap = max(0.0, target - current_savings)
    if gap <= 0:
        return {
            "target_corpus": target,
            "gap": 0.0,
            "months_to_target": 0.0,
            "monthly_expenses": monthly_expenses,
            "target_months": target_months,
        }
    if monthly_contribution <= 0:
        return {
            "target_corpus": target,
            "gap": gap,
            "months_to_target": None,
            "monthly_expenses": monthly_expenses,
            "target_months": target_months,
        }
    r = savings_yield_annual_pct / 100 / 12
    bal = current_savings
    mo = 0
    while bal < target - 1e-6 and mo < 1200:
        mo += 1
        bal = bal * (1 + r) + monthly_contribution
    if bal < target - 1e-6:
        return {
            "target_corpus": target,
            "gap": gap,
            "months_to_target": None,
            "monthly_expenses": monthly_expenses,
            "target_months": target_months,
        }
    return {
        "target_corpus": target,
        "gap": gap,
        "months_to_target": float(mo),
        "monthly_expenses": monthly_expenses,
        "target_months": target_months,
    }


def credit_card_months_to_payoff(balance: float, apr_pct: float, monthly_payment: float) -> dict[str, Any]:
    """Minimum payment that only covers interest leads to None (never)."""
    if balance <= 0:
        return {"months": 0, "total_interest": 0.0, "reachable": True}
    if monthly_payment <= 0:
        return {"months": None, "total_interest": None, "reachable": False}
    r = apr_pct / 100 / 12
    b = balance
    total_int = 0.0
    for mo in range(1, 1201):
        int_ch = b * r
        princ = monthly_payment - int_ch
        total_int += int_ch
        if princ <= 0:
            return {"months": None, "total_interest": None, "reachable": False}
        b -= princ
        if b <= 0.01:
            return {"months": mo, "total_interest": total_int, "reachable": True}
    return {"months": None, "total_interest": total_int, "reachable": False}


def personal_loan_summary(principal: float, apr_pct: float, tenure_months: int) -> dict[str, float]:
    years = max(tenure_months / 12, 1 / 12)
    emi = monthly_emi(principal, apr_pct, years)
    total = emi * tenure_months
    return {"emi": emi, "total_paid": total, "interest": total - principal}


def rent_vs_buy_snapshot(
    horizon_years: int,
    home_price: float,
    down_payment_pct: float,
    loan_rate_annual_pct: float,
    loan_tenure_years: int,
    home_appreciation_annual_pct: float,
    maintenance_annual_pct_of_home: float,
    rent_first_year_monthly: float,
    rent_increase_annual_pct: float,
    alternate_investment_annual_pct: float,
) -> dict[str, Any]:
    """
    Month-level simplified comparison: renter invests down payment + monthly surplus
    (buyer cash flow − rent) at alternate_investment_annual_pct.
    Buyer ends with home value − any remaining loan (typically 0 if horizon >= loan).
    """
    months = max(1, horizon_years * 12)
    down = home_price * (down_payment_pct / 100)
    loan_amt = max(0.0, home_price - down)
    emi = monthly_emi(loan_amt, loan_rate_annual_pct, loan_tenure_years) if loan_amt > 0 else 0.0
    maint_m = home_price * (maintenance_annual_pct_of_home / 100) / 12

    r_inv = alternate_investment_annual_pct / 100 / 12
    r_home_m = home_appreciation_annual_pct / 100 / 12

    buyer_loan_bal = loan_amt
    r_loan = loan_rate_annual_pct / 100 / 12
    home_val = home_price

    renter_inv = down
    rent_m = rent_first_year_monthly

    total_rent_paid = 0.0
    total_buy_cash = down

    loan_months_total = loan_tenure_years * 12

    for m in range(1, months + 1):
        # capture before deducting so buy_monthly is correct in the month loan is fully paid
        loan_active = buyer_loan_bal > 1e-6
        int_port = buyer_loan_bal * r_loan if loan_active else 0.0
        princ = emi - int_port if loan_active else 0.0
        buyer_loan_bal = max(0.0, buyer_loan_bal - princ)
        home_val *= 1 + r_home_m

        buy_monthly = (emi if loan_active else 0.0) + maint_m
        total_buy_cash += buy_monthly

        if m % 12 == 1 and m > 1:
            rent_m *= 1 + rent_increase_annual_pct / 100

        total_rent_paid += rent_m
        surplus = buy_monthly - rent_m
        renter_inv = renter_inv * (1 + r_inv) + surplus

    buyer_net_worth = home_val - buyer_loan_bal
    renter_net_worth = renter_inv

    return {
        "buyer_net_worth_end": buyer_net_worth,
        "renter_net_worth_end": renter_net_worth,
        "total_buy_cash_outflow": total_buy_cash,
        "total_rent_paid": total_rent_paid,
        "home_value_end": home_val,
        "remaining_loan": buyer_loan_bal,
        "better": "buy" if buyer_net_worth > renter_net_worth else "rent",
    }


def epf_projected_corpus(
    starting_balance: float,
    monthly_employee_contribution: float,
    monthly_employer_contribution: float,
    annual_interest_pct: float,
    years: float,
    salary_growth_annual_pct: float = 0.0,
) -> dict[str, float]:
    """Yearly compounding on opening balance + sum of monthly flows approximated as mid-year."""
    bal = starting_balance
    emp = monthly_employee_contribution
    er = monthly_employer_contribution
    r = annual_interest_pct / 100
    for _ in range(max(1, int(math.ceil(years)))):
        yearly_contrib = (emp + er) * 12
        bal = (bal + yearly_contrib * 0.5) * (1 + r) + yearly_contrib * 0.5
        emp *= 1 + salary_growth_annual_pct / 100
        er *= 1 + salary_growth_annual_pct / 100
    return {"corpus": bal, "years_modeled": int(math.ceil(years))}


def nps_projected_corpus(
    monthly_contribution: float,
    years: float,
    annual_return_pct: float,
    annual_expense_ratio_pct: float = 0.09,
) -> dict[str, float]:
    net_r = (annual_return_pct - annual_expense_ratio_pct) / 100
    m_net = net_r / 12
    months = int(years * 12)
    fv = float(-npf.fv(m_net, months, -monthly_contribution, 0))
    total_in = monthly_contribution * months
    return {"corpus": fv, "total_contributed": total_in, "gain": fv - total_in}


def ppf_maturity_estimate(
    yearly_deposit: float,
    annual_rate_pct: float,
    years: int,
) -> dict[str, float]:
    """Yearly compounding; deposit at start of each year (PPF-style illustration)."""
    cap = min(150000.0, max(0.0, yearly_deposit))
    bal = 0.0
    for _ in range(max(1, years)):
        bal = (bal + cap) * (1 + annual_rate_pct / 100)
    total_in = cap * years
    return {"corpus": bal, "total_deposited": total_in, "interest_earned": bal - total_in}


def senior_interest_tds_note(
    annual_interest: float,
    is_senior_citizen: bool,
) -> dict[str, Any]:
    """Thresholds for interest-only TDS avoidance (illustrative; Form 15H etc. not modeled)."""
    thr = 50000 if is_senior_citizen else 40000
    likely_tds = annual_interest > thr
    return {"tds_threshold": thr, "likely_tds_if_no_exemption": likely_tds, "annual_interest": annual_interest}


def real_return_pct(nominal_annual_pct: float, inflation_annual_pct: float) -> float:
    """Fisher approximation."""
    n = nominal_annual_pct / 100
    i = inflation_annual_pct / 100
    if (1 + i) <= 0:
        return 0.0
    return ((1 + n) / (1 + i) - 1) * 100


def swp_months_until_depleted(
    starting_corpus: float,
    monthly_withdrawal: float,
    annual_return_pct: float,
    annual_inflation_on_withdrawal_pct: float = 0.0,
) -> dict[str, Any]:
    """How many months corpus lasts with optional rising withdrawal."""
    bal = starting_corpus
    w = monthly_withdrawal
    r = annual_return_pct / 100 / 12
    inf_m = annual_inflation_on_withdrawal_pct / 100 / 12
    for mo in range(1, 1201):
        bal = bal * (1 + r) - w
        w *= 1 + inf_m
        if bal <= 0:
            return {"months": mo, "depleted": True}
    return {"months": None, "depleted": False}


def monte_carlo_retirement_corpus(
    initial: float,
    monthly_contribution: float,
    months: int,
    mean_annual_return_pct: float,
    volatility_annual_pct: float,
    n_paths: int = 500,
    seed: int | None = None,
) -> dict[str, Any]:
    """Lognormal monthly returns; contributions at month end."""
    rng = np.random.default_rng(seed)
    if months <= 0:
        return {"median": initial, "p10": initial, "p90": initial, "paths": n_paths}
    mu = mean_annual_return_pct / 100
    sig = volatility_annual_pct / 100
    dt = 1 / 12
    mu_m = (mu - 0.5 * sig * sig) * dt
    sig_m = sig * math.sqrt(dt)
    finals = []
    for _ in range(n_paths):
        bal = initial
        for _m in range(months):
            z = rng.standard_normal()
            bal = bal * math.exp(mu_m + sig_m * z) + monthly_contribution
        finals.append(bal)
    arr = np.array(finals)
    return {
        "median": float(np.median(arr)),
        "p10": float(np.percentile(arr, 10)),
        "p90": float(np.percentile(arr, 90)),
        "mean": float(np.mean(arr)),
        "paths": n_paths,
    }


_ALLOCATIONS: dict[str, dict[str, tuple[float, float]]] = {
    "conservative": {
        "Large-cap / index equity": (0.30, 11.0),
        "Debt MF / FD": (0.35, 7.0),
        "PPF / EPF top-up": (0.20, 8.0),
        "Gold (SGB / ETF)": (0.10, 8.0),
        "Liquid fund": (0.05, 6.5),
    },
    "moderate": {
        "Flexi-cap equity SIP": (0.50, 12.0),
        "Debt MF / hybrid": (0.25, 8.0),
        "PPF / EPF top-up": (0.10, 8.0),
        "Gold (SGB / ETF)": (0.10, 8.0),
        "Liquid fund": (0.05, 6.5),
    },
    "aggressive": {
        "Mid / small-cap equity": (0.60, 14.0),
        "Flexi-cap / hybrid": (0.15, 10.0),
        "PPF / EPF top-up": (0.05, 8.0),
        "Gold (SGB / ETF)": (0.10, 8.0),
        "Liquid fund": (0.10, 6.5),
    },
}


def full_financial_plan(
    monthly_income: float,
    monthly_essential: float,
    monthly_discretionary: float,
    monthly_emi_outgo: float,
    current_lumpsum: float,
    current_age: int,
    retirement_age: int,
    risk_profile: str = "moderate",
) -> dict[str, Any]:
    """
    Comprehensive financial snapshot + allocation plan.

    Returns a dict with health indicators, monthly surplus, emergency fund status,
    suggested SIP + lumpsum allocation, and projected corpus at retirement.
    """
    total_expenses = monthly_essential + monthly_discretionary + monthly_emi_outgo
    monthly_surplus = monthly_income - total_expenses
    savings_rate = (monthly_surplus / monthly_income * 100) if monthly_income > 0 else 0.0

    # Emergency fund: 6 months of living expenses (excluding EMI)
    monthly_living = monthly_essential + monthly_discretionary
    emergency_target = monthly_living * 6
    emergency_gap = max(0.0, emergency_target - current_lumpsum)
    emergency_months_covered = min(6.0, current_lumpsum / monthly_living) if monthly_living > 1 else 6.0

    # Investable amounts
    investable_lumpsum = max(0.0, current_lumpsum - emergency_target)
    monthly_investable = max(0.0, monthly_surplus)

    emi_ratio = (monthly_emi_outgo / monthly_income * 100) if monthly_income > 0 else 0.0

    # Health ratings
    if savings_rate >= 30:
        savings_health = ("excellent", "Excellent (>30%)", "emerald")
    elif savings_rate >= 20:
        savings_health = ("good", "Good (20–30%)", "emerald")
    elif savings_rate >= 10:
        savings_health = ("ok", "Could improve (10–20%)", "amber")
    elif monthly_surplus >= 0:
        savings_health = ("low", "Low (<10%) — review expenses", "amber")
    else:
        savings_health = ("deficit", "Deficit — expenses exceed income", "rose")

    if emi_ratio <= 30:
        debt_health = ("ok", f"Manageable ({emi_ratio:.0f}% of income)", "emerald")
    elif emi_ratio <= 50:
        debt_health = ("high", f"Moderate load ({emi_ratio:.0f}% of income)", "amber")
    else:
        debt_health = ("very_high", f"High ({emi_ratio:.0f}% of income) — may limit savings", "rose")

    if emergency_gap <= 0:
        em_health = ("covered", "Fully covered (6 months)", "emerald")
    elif current_lumpsum >= monthly_living * 3:
        em_health = ("partial", f"{emergency_months_covered:.1f} months covered — top up", "amber")
    else:
        em_health = ("low", f"Only {emergency_months_covered:.1f} months — build urgently", "rose")

    years = max(0, retirement_age - current_age)
    months = years * 12
    alloc_map = _ALLOCATIONS.get(risk_profile.lower(), _ALLOCATIONS["moderate"])

    sip_rows: list[dict[str, Any]] = []
    total_corpus = 0.0

    for name, (pct, return_pct) in alloc_map.items():
        sip_amt = monthly_investable * pct
        lump_amt = investable_lumpsum * pct
        r = return_pct / 100 / 12

        if months > 0 and r > 1e-12:
            fv_sip = sip_amt * (((1 + r) ** months - 1) / r) * (1 + r)
        else:
            fv_sip = sip_amt * months

        fv_lump = lump_amt * ((1 + return_pct / 100) ** years) if years > 0 else lump_amt
        fv_total = fv_sip + fv_lump
        total_corpus += fv_total

        sip_rows.append({
            "category": name,
            "pct": round(pct * 100),
            "monthly_sip": round(sip_amt),
            "lump_deploy": round(lump_amt),
            "assumed_return": return_pct,
            "fv_sip": round(fv_sip),
            "fv_lump": round(fv_lump),
            "fv_total": round(fv_total),
        })

    return {
        "monthly_income": monthly_income,
        "monthly_essential": monthly_essential,
        "monthly_discretionary": monthly_discretionary,
        "monthly_emi_outgo": monthly_emi_outgo,
        "total_expenses": total_expenses,
        "monthly_surplus": monthly_surplus,
        "savings_rate": savings_rate,
        "savings_health": savings_health,
        "emergency_target": emergency_target,
        "emergency_gap": emergency_gap,
        "emergency_months_covered": emergency_months_covered,
        "em_health": em_health,
        "investable_lumpsum": investable_lumpsum,
        "monthly_investable": monthly_investable,
        "emi_ratio": emi_ratio,
        "debt_health": debt_health,
        "years": years,
        "risk_profile": risk_profile,
        "sip_rows": sip_rows,
        "total_corpus": round(total_corpus),
    }


def education_goal_sip(
    future_cost: float,
    years_to_goal: float,
    education_inflation_annual_pct: float,
    investment_return_annual_pct: float,
    current_savings: float,
) -> dict[str, float]:
    """Inflate goal to nominal future cost, then SIP."""
    months = max(1, int(round(years_to_goal * 12)))
    nominal_goal = future_cost * ((1 + education_inflation_annual_pct / 100) ** years_to_goal)
    return {"nominal_goal": nominal_goal, **sip_monthly_for_target(nominal_goal, months, investment_return_annual_pct, current_savings)}
