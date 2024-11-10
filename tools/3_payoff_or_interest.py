import streamlit as st
import numpy_financial as npf
from tools.utils import retriever, keeper

st.title("Payoff or Invest Calculator")

if "loan_remaining" not in st.session_state:
    st.session_state.loan_remaining = 700000
    st.session_state.interest = 8.0
    st.session_state.cur_month = 15
    st.session_state.months_remaining = 60
    st.session_state.lumpsum = 100000
    st.session_state.add_inv = 0
    st.session_state.yr_return = 12.0

retriever("lumpsum")
retriever("add_inv")
retriever("interest")
retriever("cur_month")
retriever("yr_return")
retriever("loan_remaining")
retriever("months_remaining")
col1, col2, col3, col4 = st.columns(4)

loan_remaining = col1.number_input("Loan Amount Remaining", min_value=0, key="_loan_remaining", on_change=keeper, args=['loan_remaining'])
interest = col2.number_input("Interest", min_value=0.0, key="_interest", on_change=keeper, args=['interest'])
cur_month = col3.number_input("Current Month Of The Loan", min_value=0, key="_cur_month", on_change=keeper, args=['cur_month'])
months_remaining = col4.number_input("Months Remaining in Loan", min_value=0, key="_months_remaining", on_change=keeper, args=['months_remaining'])

lumpsum = col1.number_input("Loumpsum you have", min_value=0, key="_lumpsum", on_change=keeper, args=['lumpsum'])
add_inv = col2.number_input("Amount you can invest per month", min_value=0, key="_add_inv", on_change=keeper, args=['add_inv'])
yr_return = col3.number_input("Return you can generate per year", min_value=0.0, key="_yr_return", on_change=keeper, args=['yr_return'])

interest_p = interest / 100
yr_return_p = yr_return / 100

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
interest_pay = -1 * cumipmt(interest_p/12, cur_month+months_remaining, loan_remaining, cur_month, months_remaining)
total_inv = lumpsum + add_inv * months_remaining
fv_val = -1 * npf.fv(yr_return_p/12, months_remaining, add_inv, lumpsum)
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
