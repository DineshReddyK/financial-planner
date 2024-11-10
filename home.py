import streamlit as st
st.set_page_config(layout='wide')
inv_cal = st.Page("./tools/1_investment_calculator.py", title="Investment Calculator")
emi_cal = st.Page("./tools/2_mortgage_calculator.py", title="Mortgage Calculator")
pay_inv = st.Page("./tools/3_payoff_or_interest.py", title="Payoff or Invest")
fd_cal = st.Page("./tools/5_fd_calculator.py", title="FD Calculator")
fd_mf = st.Page("./tools/6_fd_or_mf.py", title="FD or MF")
planner = st.Page("./tools/4_planner.py", title="Financial Planner")
pg = st.navigation(
        {
            "Tools": [inv_cal, emi_cal, pay_inv, fd_cal, fd_mf, planner],
        }
    )

pg.run()