import streamlit as st
from tools.utils import retriever, keeper

st.header("FD Calculator")

if "principal" not in st.session_state:
    st.session_state.principal = 1000000
    st.session_state.rate = 6.0
    st.session_state.months = 12
    st.session_state.tax_slab = 30

retriever("principal")
retriever("rate")
retriever("months")
retriever("tax_slab")

col1, col2, col3, col4 = st.columns(4)
principal = col1.number_input("Principal Amount", min_value=5000, key="_principal", on_change=keeper, args=['principal'])
rate = col2.number_input("Interest Rate", min_value=0.0, key="_rate", on_change=keeper, args=['rate'])
months = col3.number_input("Investmen Period (Months)", min_value=1, key="_months", on_change=keeper, args=['months'])
tax_slab = col4.number_input("Your Tax Slab", key="_tax_slab", on_change=keeper, args=['tax_slab'])

st.divider()
st.markdown("""
            The derived values are approximate. Actual value depend on how bank does compunding.<br>
            Some banks do compunding monthly, some quaterly and some annually!
            """, unsafe_allow_html=True)
st.markdown("")

monthly_rate = rate / 100 / 12  # Monthly interest rate

# Compound interest formula: A = P * (1 + r/n)^(nt)
amount = principal * (1 + monthly_rate) ** (months)
interest = amount - principal

# Calculate TDS (Tax Deducted at Source) if interest exceeds ₹40,000
tds = 0.10 * interest if interest > 40000 else 0
total_tax = (tax_slab / 100) * interest

# Net interest after deducting TDS and total tax
net_interest = interest - tds - total_tax
profit_percentage = (net_interest / principal) * 100

col1, col2, col3 = st.columns(3)
col1.metric("Original Maturity Amount", f"₹ {principal+interest:,.2f}", delta=f"₹ {interest:,.2f}")
col2.metric("Actual Amount Received", f"₹ {principal+net_interest:,.2f}", delta=f"₹ {net_interest:,.2f}")
col3.metric("Profit percentage", f"{profit_percentage:.2f}%")

st.divider()

col1, col2, col3 = st.columns(3)
col1.metric("You will be paying TDS of", f"₹ {tds:,.2f}")
col2.metric("You will be paying TAX of", f"₹ {total_tax:,.2f}")
col3.metric("Net interest after all taxes", f"₹ {net_interest:,.2f}")
