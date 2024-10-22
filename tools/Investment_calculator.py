import streamlit as st

col1, buff, col2 = st.columns([2,1,2])
current_age = col1.slider("Current Age", min_value=15, max_value=100, value=35)
retirement_age = col2.slider("Retirement Age", min_value=35, max_value=100, value=60)

col1, col2, col3 = st.columns(3)
month_inv = col1.number_input("Montly Contribution", min_value=0, value=5000)
yearly_inc = col2.number_input("Yearly Increase In Contribution", min_value=0.0, max_value=100.0, value=5.0) / 100
inflation = col3.number_input("Inflattion Rate", min_value=0.0, max_value=100.0, value=6.0) / 100

#nper - number of periods (months)
nper = (retirement_age - current_age) * 12

def calc_ret(month_inv, yearly_inc, inflation, inv_return_rate, nper):
    monthly_return_rate = inv_return_rate / 12
    monthly_inflation = inflation / 12
    adjusted_value = 0
    final_fv = 0

    for month in range(1, nper+1):
    #calculate future value for this months contributaion
        fv = month_inv * ((1+monthly_return_rate) ** (nper-month))
        npv = fv / ((1+monthly_inflation) ** (nper-month))
        adjusted_value += npv
        final_fv += fv


        if month % 12 == 0:
            month_inv *= (1+yearly_inc)
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
    adjusted_value, final_fv = calc_ret(month_inv, yearly_inc, inflation, val/100, nper)
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