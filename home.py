import streamlit as st

st.set_page_config(layout='wide')

with st.sidebar:
    st.markdown("**NOTE**")
    st.markdown("I am not a registered financial advisor. This project is inspired by multiple financial advisors and their calculators.")

inv_cal = st.Page("./tools/1_investment_calculator.py", title="Investment Calculator")
emi_cal = st.Page("./tools/2_mortgage_calculator.py", title="Mortgage Calculator")
fd_cal = st.Page("./tools/3_fd_calculator.py", title="FD Calculator")
pay_inv = st.Page("./tools/4_payoff_or_interest.py", title="Payoff or Invest")
fd_mf = st.Page("./tools/5_fd_or_mf.py", title="FD or MF")
planner = st.Page("./tools/6_planner.py", title="Financial Planner")

pg = st.navigation(
        {
            "Tools": [inv_cal, emi_cal, fd_cal, pay_inv, fd_mf, planner],
        }
    )


pg.run()