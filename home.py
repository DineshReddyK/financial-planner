import streamlit as st

inv_cal = st.Page("./tools/1_investment_calculator.py", title="Investment Calculator")
emi_cal = st.Page("./tools/2_mortgage_calculator.py", title="Mortgage Calculator")
fd_cal = st.Page("./tools/5_fd_calculator.py", title="FD Calculator")
pay_inv = st.Page("./tools/3_payoff_or_interest.py", title="Payoff or Invest")
fd_mf = st.Page("./tools/6_fd_or_mf.py", title="FD or MF (Growth Plan)")
planner = st.Page("./tools/4_planner.py", title="Financial Planner")
pg = st.navigation(
        {
            "Tools": [emi_cal, fd_cal, planner, pay_inv, inv_cal, fd_mf],
        }
    )

pg.run()