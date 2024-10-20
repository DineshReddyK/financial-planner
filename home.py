import streamlit as st

emi_cal = st.Page("./tools/mortgage_calculator.py", title="Mortgage Calculator")
planner = st.Page("./tools/Planner.py", title="Financial Planner")
pg = st.navigation(
        {
            #"Account": [logout_page],
            "Tools": [emi_cal, planner],
        }
    )

pg.run()