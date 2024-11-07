import streamlit as st

st.header("FD Calculator")
col1, buff, col2 = st.columns([2,1,2])
principal = col1.number_input("Principal Amount", min_value=5000, value=1000000)
rate = col2.number_input("Interest Rate", min_value=0.0, value=6.0)
time = col1.number_input("Investmen Period (Years)", min_value=1, value=1)
tax_slab = col2.number_input("Your Tax Slab", value=30.0)

st.divider()

interest = principal * (rate / 100) * time
tds = 0.10 * interest
total_tax = (tax_slab / 100) * interest
net_interest = interest - total_tax
profit_percentage = (net_interest / principal) * 100

col1, col2, col3 = st.columns(3)
col1.metric("Original Maturity Amount", f"₹ {principal+interest}", delta=f"₹ {interest:,.2f}")
col2.metric("Actual Amount Received", f"₹ {principal+net_interest}", delta=f"₹ {net_interest:,.2f}")
col3.metric("Profit percentage", f"{profit_percentage:.2f}%")

st.divider()

col1, col2, col3 = st.columns(3)
col1.metric("You will be paying TDS of", f"₹ {tds:,.2f}")
col2.metric("You will be paying TAX of", f"₹ {total_tax:,.2f}")
col3.metric("Net interest after all taxes", f"₹ {net_interest:,.2f}")
