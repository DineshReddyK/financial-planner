import streamlit as st

st.header("FD or Liquid MF (Growth Plan)?")

def calculate_fd_returns(principal, rate, months, tax_slab):
    monthly_rate = rate / 100 / 12

    # Compound interest formula: A = P * (1 + r/n)^(nt)
    amount = principal * (1 + monthly_rate) ** (months)
    interest = amount - principal

    # TDS is applicable if interest exceeds ₹40,000
    tds = 0.10 * interest if interest > 40000 else 0
    total_tax = (tax_slab / 100) * interest

    net_interest = interest - tds - total_tax
    profit_percentage = (net_interest / principal) * 100
    return net_interest, profit_percentage, interest, tds, total_tax

def calculate_cagr(principal, cagr, months):
    time = months / 12  # Convert months to years
    return principal * ((1 + cagr / 100) ** time - 1)

def calculate_mf_returns(principal, cagr, months, tax_slab):
    returns = calculate_cagr(principal, cagr, months)
    stcg_tax, ltcg_tax = 0,0
    if months < 12:
        stcg_tax = (tax_slab / 100) * returns  # STCG at slab rate for holdings less than 12 months
        net_returns = returns - stcg_tax
    else:
        exempt_ltcg = min(returns, 125000)  # Exempt up to ₹1.25 lakh
        taxable_ltcg = max(0, returns - 125000)
        ltcg_tax = 0.125 * taxable_ltcg  # LTCG at 12.5% over ₹1.25 lakh
        net_returns = exempt_ltcg + (returns - taxable_ltcg) - ltcg_tax
    profit_percentage = (net_returns / principal) * 100
    return net_returns, profit_percentage, returns, stcg_tax, ltcg_tax

def calculate_savings_returns(principal, rate, months, tax_slab):
    time = months / 12
    interest = principal * (rate / 100) * time
    total_tax = (tax_slab / 100) * interest
    net_interest = interest - total_tax
    profit_percentage = (net_interest / principal) * 100
    return net_interest, profit_percentage, interest, total_tax

st.markdown("**Want to invest lumpsum for short duration and can't decide which is best risk free investment?**")
st.markdown("**Possible risk free investment options are**")
st.markdown("1. FD\n2. Liquid MF (Growth) \n3. Savings Bank")
st.divider()

col1, col2, col3 = st.columns(3)
principal = col1.number_input("Principal Amount", min_value=5000, value=1000000)
months = col2.number_input("Investmen Period (Months)", min_value=1, value=12)
tax_slab = col3.number_input("Your Tax Slab", value=30.0)
fd_rate = col1.number_input("FD Interest Rate (Year)", min_value=0.0, value=6.0)
savings_rate = col2.number_input("Bank Interest Rate (Year)", min_value=0.0, value=4.5)
mf_cagr = col3.number_input("MF CAGR", min_value=0.0, value=5.0)

fd_net, fd_profit, fd_int_o, fd_tds, fd_tot_tax = calculate_fd_returns(principal, fd_rate, months, tax_slab)
mf_net, mf_profit, mf_ret_o, stcg_tax, ltcg_tax = calculate_mf_returns(principal, mf_cagr, months, tax_slab)
s_net, s_profit, s_ret_o, s_tax = calculate_savings_returns(principal, savings_rate, months, tax_slab)

st.divider()
col1, col2, col3, col4 = st.columns(4)
col1.metric("FD interest earned", f"₹{fd_int_o:,.1f}")
col2.metric("FD TDS paid", f"₹{fd_tds:,.1f}")
col3.metric("FD TAX paid", f"₹{fd_tot_tax:,.1f}")
col4.metric("FD returns after tax",  f"₹{fd_net:,.1f}",  f"{fd_profit:.2f}%")
st.divider()
col1, col2, col3, col4 = st.columns(4)
col1.metric("Growth MF actual returns", f"₹{mf_ret_o:,.1f}")
col2.metric("Growth MF STCG tax", f"₹{stcg_tax:,.1f}")
col3.metric("Growth MF LTCG tax", f"₹{ltcg_tax:,.1f}")
col4.metric("Growth MF returns after tax", f"₹{mf_net:,.2f}",  f"{mf_profit:.2f}%")

st.divider()
col1, col2, col3, col4 = st.columns(4)
col1.metric("Savings Account Returns", f"₹{s_ret_o:,.2f}")
col2.metric("Savings Account Tax", f"₹{s_tax:,.2f}")
col4.metric("Savings Account returns after tax", f"₹{s_net:,.2f}", f"{s_profit:.2f}%")


if fd_net > mf_net and fd_net > s_net:
    st.subheader("Based on net returns :blue[Fixed Deposit] is the better option.")
elif mf_net > fd_net and mf_net > s_net:
    st.subheader("Based on net returns :blue[Growth Mutual Fund] is the better option.")
else:
    st.subheader("Based on net returns :blue[Savings Account] is the better option.")