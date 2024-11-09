import streamlit as st
import pandas as pd
import math
import numpy_financial as npf

st.title("Payoff or Invest Calculator")

col1, col2, col3, col4 = st.columns(4)

loan_remaining = col1.number_input("Loan Amount Remaining", min_value=0, value=700000)
interest = col2.number_input("Interest", min_value=0.0, value=8.0) / 100
cur_month = col3.number_input("Current Month Of The Loan", min_value=0, value=15)
months_remaining = col4.number_input("Months Remaining in Loan", min_value=0, value=60)

lumpsum = col1.number_input("Loumpsum you have", min_value=0, value=100000)
add_inv = col2.number_input("Amount you can invest per month", min_value=0, value=0)
yr_return = col3.number_input("Return you can generate per year", min_value=0.0, value=12.0) / 100


def cumipmt(rate, nper, pv, start_period, end_period, type=1):
    """
    Calculates the cumulative interest paid between two periods.

    Args:
        rate: The interest rate per period.
        nper: The total number of payment periods.
        pv: The present value of the loan.
        start_period: The first period in the calculation.
        end_period: The last period in the calculation.
        type: 0 for payments at the end of the period, 1 for the beginning.

    Returns:
        The cumulative interest paid.
    """

    if start_period < 1 or end_period < 1 or start_period > end_period:
        raise ValueError("Invalid period range")

    periods = range(start_period, end_period + 1)
    return sum(npf.ipmt(rate, per, nper, pv, 0, type) for per in periods)



st.divider()
st.write("Over the tenure of your loan")
interest_pay = -1 * cumipmt(interest/12, cur_month+months_remaining, loan_remaining, cur_month, months_remaining)
total_inv = lumpsum + add_inv * months_remaining
fv_val = -1 * npf.fv(yr_return/12, months_remaining, add_inv, lumpsum)
excess_you_made = fv_val - total_inv

data = {
    "You will pay the total interest of": f"{round(interest_pay):,}",
    "You would have invested": f"{round(total_inv):,}",
    "Your investment would have grown to": f"{round(fv_val):,}",
    "Which means, you made an excess of": f"{round(excess_you_made):,}",
}
st.dataframe(data)

if excess_you_made < interest_pay:
    st.subheader("You shuold :blue[PAY OFF] the loan")
else:
    st.subheader("You should :red[INVEST] the amount")
