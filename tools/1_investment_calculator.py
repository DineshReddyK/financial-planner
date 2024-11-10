import streamlit as st
from tools.utils import retriever, keeper

st.header("Investment Calculator")

if 'current_age' not in st.session_state:
    st.session_state.current_age = 35
    st.session_state.retirement_age = 60
    st.session_state.month_inv = 10000
    st.session_state.yearly_inc = 6.0
    st.session_state.inflation = 6.0

retriever("current_age")
retriever("retirement_age")
retriever("month_inv")
retriever("yearly_inc")
retriever("inflation")

col1, col2, col3 = st.columns(3)
current_age = col1.slider("Current Age", min_value=15, max_value=100, key="_current_age", on_change=keeper, args=['current_age'])
retirement_age = col2.slider("Retirement Age", min_value=35, max_value=100, key="_retirement_age", on_change=keeper, args=['retirement_age'])
col1, col2, col3 = st.columns(3)
inflation = col3.number_input("Inflation Rate", min_value=0.0, max_value=100.0, key="_inflation", on_change=keeper, args=['inflation'])
month_inv = col1.number_input("Montly Contribution", min_value=0, key="_month_inv", on_change=keeper, args=['month_inv'])
yearly_inc = col2.number_input("Yearly Increase In Contribution", min_value=0.0, max_value=100.0, key="_yearly_inc", on_change=keeper, args=['yearly_inc'])
inflation_p = inflation / 100
yearly_inc_p = yearly_inc / 100

#nper - number of periods (months)
nper = (retirement_age - current_age) * 12

def calc_ret(month_inv, yearly_inc_p, inflation_p, inv_return_rate, nper):
    monthly_return_rate = inv_return_rate / 12
    monthly_inflation_p = inflation_p / 12
    adjusted_value = 0
    final_fv = 0

    for month in range(1, nper+1):
    #calculate future value for this months contributaion
        fv = month_inv * ((1+monthly_return_rate) ** (nper-month))
        npv = fv / ((1+monthly_inflation_p) ** (nper-month))
        adjusted_value += npv
        final_fv += fv


        if month % 12 == 0:
            month_inv *= (1+yearly_inc_p)
    return adjusted_value,final_fv

scheme_ret = {
    "FD/RD": 5,
    "Gold" : 10,
    "Equity/MF": 15,
    "High Risk Equity": 20,
    "Very High Risk Equity": 25,
    "Extream Risk Equity": 30,
}

schedule = []
for key, val in scheme_ret.items():
    adjusted_value, final_fv = calc_ret(month_inv, yearly_inc_p, inflation_p, val/100, nper)
    schedule.append(
        {
            "Investment": key,
            "~Return": f"{val}%",
            "Amount Earned": round(final_fv),
            "Actual Amount Value": round(adjusted_value),
            "i.e At the end of retirement": f"{(round(adjusted_value)/10000000):.2f} crore in todays money"
        }
    )

st.divider()
st.markdown("**With the above numbers, possible returns you could make by your retirement time are**")
st.dataframe(schedule)