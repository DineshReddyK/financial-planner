import streamlit as st
import pandas as pd
import math
from tools.utils import retriever, keeper

st.title("Loan Repayments Calculator")

if 'loan_amount' not in st.session_state:
    st.session_state.loan_amount = 700000
    st.session_state.loan_term = 30
    st.session_state.interest_rate = 8.1

retriever("loan_amount")
retriever("loan_term")
retriever("interest_rate")

col1, col2, col3 = st.columns(3)
loan_amount = col1.number_input("Loan Amount", min_value=0, key="_loan_amount", on_change=keeper, args=['loan_amount'])
loan_term = col2.number_input("Loan Term (in years)", min_value=1, key="_loan_term", on_change=keeper, args=['loan_term'])
interest_rate = col3.number_input("Interest Rate (in %)", min_value=0.0, key="_interest_rate", on_change=keeper, args=['interest_rate'])

st.session_state.loan_amount = loan_amount
st.session_state.loan_term = loan_term
st.session_state.interest_rate = interest_rate

print("sess: ", st.session_state.loan_term)
monthly_prepayment, yearly_prepayment, onetime_payment, ot_when = 0,0,0,0
mpp = col1.checkbox("Monthly Pre Pay")
if mpp:
    monthly_prepayment = col1.number_input("Additional Pre Pay (per month)", min_value=0, value=0)

ypp = col2.checkbox("Yearly Pre Pay")
if ypp:
    yearly_prepayment = col2.number_input("Additional Pre Pay (per year)", min_value=0, value=0)


opp = col3.checkbox("One Time Pre Pay")
if opp:
    onetime_payment = col3.number_input("One Time Pre Payment", min_value=0, value=0)
    ot_when = col3.selectbox("One Time Payment Year", range(1,loan_term))

# Calculate the repayments.
monthly_interest_rate = (interest_rate / 100) / 12
number_of_payments = loan_term * 12
monthly_payment = (
    loan_amount
    * (monthly_interest_rate * (1 + monthly_interest_rate) ** number_of_payments)
    / ((1 + monthly_interest_rate) ** number_of_payments - 1)
)

# Display the repayments.
total_payments = monthly_payment * number_of_payments
total_interest = total_payments - loan_amount

st.write("### Repayments")
col1, col2, col3 = st.columns(3)
col1.metric(label="Monthly EMI", value=f"₹{monthly_payment:,.2f}")
col3.metric(label="Total Interest", value=f"₹{total_interest:,.0f}")
col2.metric(label="Total Repayments", value=f"₹{total_payments:,.0f}")

def calculate_loan_schedule(loan_amount, loan_term_months, monthly_prepayment, ot_when):
    schedule = []
    remaining_balance = loan_amount

    original_loan_amount = loan_amount
    original_loan_term_months = loan_term_months

    #prepay_till = original_loan_term_months/2  #its worth payng only on 1st half of loan term
    #print(f"Pre payments till: {prepay_till}months / {prepay_till/12} years")
    prepay_till = original_loan_term_months

    for month in range(1, loan_term_months + 1):
        interest_payment = remaining_balance * monthly_interest_rate
        principal_payment = monthly_payment - interest_payment
        year = math.ceil(month / 12)  # Calculate the year into the loan

        m_prepayment, y_prepayment, o_prepayment = 0,0,0
        if month <= prepay_till:
            m_prepayment = monthly_prepayment

        if month % 12 == 0:
            y_prepayment = yearly_prepayment

        if ot_when == year:
            o_prepayment = onetime_payment
            #only once. loop run for each month. break it
            ot_when = 0

        prepayments = m_prepayment + y_prepayment + o_prepayment
        remaining_balance -= round(monthly_payment + prepayments - interest_payment)

        if remaining_balance <= 0:
            # Loan is fully paid, no need to continue calculating the schedule
            loan_term_months = month
            break

        schedule.append({
            'Month': month,
            'Monthly Payment': round(monthly_payment),
            'Interest Payment': round(interest_payment),
            'Principal Payment': round(principal_payment),
            'Prepayment': round(prepayments),
            'Remaining Balance': max(0, remaining_balance),  # Ensure balance doesn't go negative
            'Year': year
        })

    # Calculate total interest savings and total tenure reduced
    original_interest = (monthly_payment * original_loan_term_months) - original_loan_amount
    new_interest = (monthly_payment * loan_term_months) - loan_amount

    summary = [(original_interest, new_interest), (original_loan_term_months, loan_term_months)]
    return schedule, summary

schedule, summary = calculate_loan_schedule(loan_amount, number_of_payments, monthly_prepayment, ot_when)
df = pd.DataFrame(schedule)

interest_elms, term_elms = summary
interest_saved = interest_elms[0]-interest_elms[1]
term_reducced = term_elms[0]-term_elms[1]

if term_reducced > 0:
    st.write("### Saved Because of Prepayments")
    col1, _, col2 = st.columns(3)
    col1.metric(label="Interest Saved", value=f"₹{interest_saved:,.2f}", delta=f"{interest_saved/interest_elms[0]:.0%}")
    col2.metric(label="Tenure Reduced", value=f"{term_reducced} months", delta=f"{term_reducced/term_elms[0]:.0%}")

    col1.bar_chart([interest_elms[0], interest_elms[1]], horizontal=True)
    col2.bar_chart([term_elms[0], term_elms[1]], horizontal=True, color="#ffaa00")


# Display the data-frame as a chart.
st.write("### Payment Schedule")
payments_df = df[["Year", "Remaining Balance"]].groupby("Year").min()
st.line_chart(payments_df,
              x_label="Years",
              y="Remaining Balance")

# st.line_chart(df.set_index('Month')[["Principal Payment", "Interest Payment", "Prepayment(M)", "Prepayment(Y)"]],
#               x_label="Months",
#               y_label="Monthly Payment")

show_table = st.toggle("Show Amortization")
if show_table:
    #st.table(df[["Year", "Month", "Monthly Payment", "Interest Payment", "Principal Payment", "Prepayment", "Remaining Balance"]])
    st.dataframe(df,
                 use_container_width=True,
                 hide_index=True)