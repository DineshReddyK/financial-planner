import streamlit as st

emi_cal = st.Page("./tools/mortgage_calculator.py", title="Mortgage Calculator")
planner = st.Page("./tools/Planner.py", title="Financial Planner")
pay_inv = st.Page("./tools/payoff_or_interest.py", title="Payoff or Invest?")
inv_cal = st.Page("./tools/investment_calculator.py", title="Investment Calculator")
pg = st.navigation(
        {
            "Tools": [emi_cal, planner, pay_inv, inv_cal],
        }
    )

pg.run()