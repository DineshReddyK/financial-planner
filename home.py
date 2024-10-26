import streamlit as st

inv_cal = st.Page("./tools/1_investment_calculator.py", title="Investment Calculator")
emi_cal = st.Page("./tools/2_mortgage_calculator.py", title="Mortgage Calculator")
pay_inv = st.Page("./tools/3_payoff_or_interest.py", title="Payoff or Invest")
planner = st.Page("./tools/4_planner.py", title="Financial Planner")
pg = st.navigation(
        {
            "Tools": [emi_cal, planner, pay_inv, inv_cal],
        }
    )

pg.run()