import streamlit as st

st.header("Lumpsum investment on FD or MF (Growth Plan)?")

def calculate_fd_returns(principal, rate, time, tax_slab):
    interest = principal * (rate / 100) * time
    tds = 0.10 * interest if interest > 40000 else 0  # TDS is applicable if interest exceeds ₹40,000
    total_tax = (tax_slab / 100) * interest
    net_interest = interest - tds - total_tax
    profit_percentage = (net_interest / principal) * 100
    return net_interest, profit_percentage

def calculate_cagr(principal, cagr, time):
    return principal * ((1 + cagr / 100) ** time - 1)

def calculate_mf_returns(principal, cagr, time, tax_slab):
    returns = calculate_cagr(principal, cagr, time)
    if time < 1:
        stcg_tax = (tax_slab / 100) * returns  # STCG at slab rate for holdings less than 1 year
        net_returns = returns - stcg_tax
    elif time < 2:
        stcg_tax = 0.20 * returns  # STCG at 20% for holdings between 12 and 24 months
        net_returns = returns - stcg_tax
    else:
        exempt_ltcg = min(returns, 125000)  # Exempt up to ₹1.25 lakh
        taxable_ltcg = max(0, returns - 125000)
        ltcg_tax = 0.125 * taxable_ltcg  # LTCG at 12.5% over ₹1.25 lakh
        net_returns = exempt_ltcg + (returns - taxable_ltcg) - ltcg_tax
    profit_percentage = (net_returns / principal) * 100
    return net_returns, profit_percentage

col1, col2, col3 = st.columns(3)
principal = col1.number_input("Principal Amount", min_value=5000, value=1000000)
time = col2.number_input("Investmen Period (Years)", min_value=1, value=1)
tax_slab = col3.number_input("Your Tax Slab", value=30.0)
fd_rate = col1.number_input("FD Interest Rate (per Year)", min_value=0.0, value=6.0)
mf_cagr = col2.number_input("MF CAGR", min_value=0.0, value=5.0)

fd_net, fd_profit = calculate_fd_returns(principal, fd_rate, time, tax_slab)
mf_net, mf_profit = calculate_mf_returns(principal, mf_cagr, time, tax_slab)

st.write(f"\nFixed Deposit (FD) returns after tax: ₹{fd_net:,.2f}, Profit percentage: {fd_profit:.2f}%")
st.write(f"Growth Mutual Fund returns after tax: ₹{mf_net:,.2f}, Profit percentage: {mf_profit:.2f}%")

if fd_net > mf_net:
    st.write("\nFixed Deposit (FD) is the better option based on net returns.")
else:
    st.write("\nGrowth Mutual Fund is the better option based on net returns.")

