"""Pure financial calculation helpers (India-oriented; not tax/legal advice)."""

from __future__ import annotations

import math
from typing import Any, Literal

import numpy_financial as npf

# --- India income-tax reference values (FY 2025-26 onwards unless noted) ---
# Section 194A thresholds when payer is a bank / co-op society / post office (Finance Act 2025).
TDS_194A_BANK_THRESHOLD_OTHERS = 50_000.0
TDS_194A_BANK_THRESHOLD_SENIOR = 100_000.0
# Section 194A when payer is not a bank / co-op society / post office (Finance Act 2025).
TDS_194A_NONBANK_THRESHOLD = 10_000.0
TDS_194A_RATE = 0.10

# Specified equity-oriented mutual funds / STT-paid: STCG holding ≤12m (statutory; cess/surcharge not layered here).
EQUITY_MF_STCG_RATE_PCT = 20.0
# LTCG on such funds: exemption then rate (cess/surcharge not layered here).
EQUITY_MF_LTCG_EXEMPT = 125_000.0
EQUITY_MF_LTCG_RATE = 0.125


def monthly_emi(loan_amount: float, annual_rate_pct: float, loan_term_years: int) -> float:
    """Standard amortizing EMI; handles zero interest."""
    n = int(loan_term_years * 12)
    if n <= 0 or loan_amount <= 0:
        return 0.0
    r = (annual_rate_pct / 100) / 12
    if abs(r) < 1e-15:
        return loan_amount / n
    return loan_amount * (r * (1 + r) ** n) / ((1 + r) ** n - 1)


def amortization_schedule(
    loan_amount: float,
    annual_rate_pct: float,
    loan_term_years: int,
    monthly_prepayment: float = 0.0,
    yearly_prepayment: float = 0.0,
    onetime_payment: float = 0.0,
    onetime_payment_year: int = 0,
) -> tuple[list[dict[str, Any]], float, int, float]:
    """
    Returns (schedule_rows, total_interest_paid, months_until_paid_off, monthly_emi).

    Prepayments reduce principal; one-time prepayment applies once in onetime_payment_year (1-indexed loan year).
    """
    monthly_interest_rate = (annual_rate_pct / 100) / 12
    number_of_payments = int(loan_term_years * 12)
    payment = monthly_emi(loan_amount, annual_rate_pct, loan_term_years)

    schedule: list[dict[str, Any]] = []
    remaining = float(loan_amount)
    total_interest = 0.0
    one_time_used = False

    if number_of_payments <= 0:
        return [], 0.0, 0, payment

    month = 0
    while month < number_of_payments and remaining > 1e-6:
        month += 1
        interest_payment = remaining * monthly_interest_rate
        principal_payment = payment - interest_payment
        year = math.ceil(month / 12)

        m_prepay = monthly_prepayment
        y_prepay = yearly_prepayment if month % 12 == 0 else 0.0
        o_prepay = 0.0
        if (
            onetime_payment > 0
            and not one_time_used
            and onetime_payment_year > 0
            and year == onetime_payment_year
        ):
            o_prepay = onetime_payment
            one_time_used = True

        prepayments = m_prepay + y_prepay + o_prepay
        remaining -= principal_payment + prepayments
        total_interest += interest_payment

        row = {
            "Month": month,
            "Monthly Payment": round(payment),
            "Interest Payment": round(interest_payment),
            "Principal Payment": round(principal_payment),
            "Prepayment": round(prepayments),
            "Remaining Balance": max(0.0, remaining),
            "Year": year,
        }
        schedule.append(row)

        if remaining <= 0:
            remaining = 0.0
            schedule[-1]["Remaining Balance"] = 0.0
            break

    return schedule, total_interest, month, payment


def calc_investment_retirement_rows(
    month_inv: float,
    yearly_inc_p: float,
    inflation_p: float,
    scheme_returns_pct: dict[str, float],
    nper_months: int,
) -> list[dict[str, Any]]:
    """Mirrors the retirement SIP projection with annual step-up and inflation adjustment."""

    def calc_ret(
        m_inv: float,
        yearly_inc_p_: float,
        inflation_p_: float,
        inv_return_rate: float,
        nper: int,
    ) -> tuple[float, float]:
        monthly_return_rate = inv_return_rate / 12
        monthly_inflation_p = inflation_p_ / 12
        adjusted_value = 0.0
        final_fv = 0.0
        mi = m_inv
        for m in range(1, nper + 1):
            fv = mi * ((1 + monthly_return_rate) ** (nper - m))
            npv = fv / ((1 + monthly_inflation_p) ** (nper - m))
            adjusted_value += npv
            final_fv += fv
            if m % 12 == 0:
                mi *= 1 + yearly_inc_p_
        return adjusted_value, final_fv

    rows: list[dict[str, Any]] = []
    for name, pct in scheme_returns_pct.items():
        adj, fv = calc_ret(month_inv, yearly_inc_p, inflation_p, pct / 100, nper_months)
        rows.append(
            {
                "Investment": name,
                "~Return": f"{pct}%",
                "Amount Earned": round(fv),
                "Actual Amount Value": round(adj),
                "i.e At the end of retirement": f"{(round(adj) / 10000000):.2f} crore in today's money",
            }
        )
    return rows


def fd_net_metrics(
    principal: float,
    rate_pct: float,
    months: int,
    tax_slab_pct: float,
    *,
    is_senior_citizen: bool = False,
    interest_payer: Literal["bank", "other"] = "bank",
) -> dict[str, float]:
    """
    FD maturity with monthly compounding (approximation).

    Interest is taxed at slab rate. TDS (if any) is withholding against that liability — do not subtract TDS and slab tax twice.

    TDS threshold follows Section 194A as amended by Finance Act 2025 (FY 2025-26+): bank/co-op/post office payers
    use ₹50k (general) / ₹1L (senior 60+); other payers use ₹10k. PAN / 206AA higher rates not modeled.
    """
    monthly_rate = rate_pct / 100 / 12
    amount = principal * (1 + monthly_rate) ** months
    interest = amount - principal
    tax_on_interest = interest * (tax_slab_pct / 100)
    net_interest = interest - tax_on_interest
    if interest_payer == "bank":
        tds_threshold = TDS_194A_BANK_THRESHOLD_SENIOR if is_senior_citizen else TDS_194A_BANK_THRESHOLD_OTHERS
    else:
        tds_threshold = TDS_194A_NONBANK_THRESHOLD
    tds_estimate = TDS_194A_RATE * interest if interest > tds_threshold else 0.0
    profit_pct = (net_interest / principal) * 100 if principal else 0.0
    return {
        "maturity_gross": amount,
        "interest_gross": interest,
        "tax_on_interest": tax_on_interest,
        "net_interest": net_interest,
        "tds_estimate": tds_estimate,
        "tds_threshold": tds_threshold,
        "profit_pct": profit_pct,
    }


def calculate_cagr_gain(principal: float, cagr_pct: float, months: int) -> float:
    years = months / 12
    return principal * ((1 + cagr_pct / 100) ** years - 1)


def mf_after_tax_returns(principal: float, cagr_pct: float, months: int, tax_slab_pct: float) -> dict[str, float]:
    """
    After-tax gain on a lump sum for an equity-oriented / STT-paid growth-style MF (illustrative).

    STCG (≤12 months): statutory 20% on gains (not marginal slab). LTCG: 12.5% on gains above ₹1.25L exemption.
    Cess/surcharge and grandfathering are not applied. ``tax_slab_pct`` is unused for this equity path (kept for API compatibility).
    """
    _ = tax_slab_pct  # kept for callers comparing FD (slab) vs MF in one form
    returns = calculate_cagr_gain(principal, cagr_pct, months)
    stcg_tax = 0.0
    ltcg_tax = 0.0
    if months < 12:
        stcg_tax = (EQUITY_MF_STCG_RATE_PCT / 100) * returns
        net_returns = returns - stcg_tax
    else:
        taxable_ltcg = max(0.0, returns - EQUITY_MF_LTCG_EXEMPT)
        ltcg_tax = EQUITY_MF_LTCG_RATE * taxable_ltcg
        net_returns = returns - ltcg_tax
    profit_pct = (net_returns / principal) * 100 if principal else 0.0
    return {
        "gross_returns": returns,
        "stcg_tax": stcg_tax,
        "ltcg_tax": ltcg_tax,
        "net_returns": net_returns,
        "profit_pct": profit_pct,
    }


def savings_simple_interest_net(principal: float, annual_rate_pct: float, months: int, tax_slab_pct: float) -> dict[str, float]:
    years = months / 12
    interest = principal * (annual_rate_pct / 100) * years
    tax = (tax_slab_pct / 100) * interest
    net_interest = interest - tax
    profit_pct = (net_interest / principal) * 100 if principal else 0.0
    return {"interest": interest, "tax": tax, "net_interest": net_interest, "profit_pct": profit_pct}


def fd_mf_savings_comparison(
    principal: float,
    months: int,
    tax_slab_pct: float,
    fd_rate_pct: float,
    mf_cagr_pct: float,
    savings_rate_pct: float,
) -> dict[str, Any]:
    fd = fd_net_metrics(principal, fd_rate_pct, months, tax_slab_pct)
    mf = mf_after_tax_returns(principal, mf_cagr_pct, months, tax_slab_pct)
    sav = savings_simple_interest_net(principal, savings_rate_pct, months, tax_slab_pct)
    if fd["net_interest"] >= mf["net_returns"] and fd["net_interest"] >= sav["net_interest"]:
        winner = "fd"
    elif mf["net_returns"] >= fd["net_interest"] and mf["net_returns"] >= sav["net_interest"]:
        winner = "mf"
    else:
        winner = "savings"
    return {"fd": fd, "mf": mf, "savings": sav, "winner": winner}


def cumulative_interest_remaining(
    annual_rate_pct: float,
    months_remaining: int,
    principal_remaining: float,
    *,
    payment_at_beginning: bool = False,
) -> float:
    """Total interest payable over months_remaining on current balance (standard amortizing loan)."""
    if months_remaining <= 0 or principal_remaining <= 0:
        return 0.0
    rate = (annual_rate_pct / 100) / 12
    typ = 1 if payment_at_beginning else 0
    total = 0.0
    for per in range(1, months_remaining + 1):
        total += float(-npf.ipmt(rate, per, months_remaining, principal_remaining, 0, typ))
    return total


def payoff_invest_comparison(
    loan_remaining: float,
    interest_annual_pct: float,
    months_remaining: int,
    lumpsum: float,
    add_inv_monthly: float,
    investment_annual_return_pct: float,
) -> dict[str, Any]:
    """
    Compares (simplified) total remaining loan interest vs investing lump sum + monthly SIP.

    Recommendation is heuristic: meaningful when lump sum is large vs loan; not a full partial-prepayment optimizer.
    """
    interest_pay = cumulative_interest_remaining(interest_annual_pct, months_remaining, loan_remaining)
    r = investment_annual_return_pct / 100 / 12
    n = months_remaining
    fv_val = float(-npf.fv(r, n, -add_inv_monthly, -lumpsum))
    total_inv = lumpsum + add_inv_monthly * n
    excess_profit = fv_val - total_inv
    suggest_payoff = excess_profit < interest_pay
    return {
        "total_remaining_interest": interest_pay,
        "total_contributed": total_inv,
        "investment_fv": fv_val,
        "investment_profit": excess_profit,
        "suggest_payoff": suggest_payoff,
    }
