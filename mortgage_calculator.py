import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import math

st.title("Loan Repayments Calculator")

# st.write("### Input Data")
col1, col2, col3 = st.columns(3)
loan_amount = col1.number_input("Loan Amount", min_value=0, value=700000)
loan_term = col2.number_input("Loan Term (in years)", min_value=1, value=30)
interest_rate = col3.number_input("Interest Rate (in %)", min_value=0.0, value=8.1)
monthly_prepayment = col1.number_input("Additional Pre Pay (per month)", min_value=0, value=0)
yearly_prepayment = col2.number_input("Additional Pre Pay (per year)", min_value=0, value=0)
onetime_payment = col3.number_input("One Time Pre Payment", min_value=0, value=0)

show_table = st.toggle("Show Amortization")

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

def calculate_loan_schedule(loan_amount, loan_term_months, monthly_prepayment):
    schedule = []
    remaining_balance = loan_amount

    original_loan_amount = loan_amount
    original_loan_term_months = loan_term_months

    prepay_till = original_loan_term_months/2

    for month in range(1, loan_term_months + 1):
        interest_payment = remaining_balance * monthly_interest_rate
        principal_payment = monthly_payment - interest_payment
        year = math.ceil(month / 12)  # Calculate the year into the loan

        prepayment = 0
        if month <= prepay_till:
            prepayment = monthly_prepayment

        remaining_balance -= (monthly_payment + prepayment - interest_payment)

        if remaining_balance <= 0:
            # Loan is fully paid, no need to continue calculating the schedule
            loan_term_months = month
            break

        schedule.append({
            'Month': month,
            'Monthly Payment': monthly_payment,
            'Interest Payment': interest_payment,
            'Principal Payment': principal_payment,
            'Prepayment': prepayment,
            'Remaining Balance': max(0, remaining_balance),  # Ensure balance doesn't go negative
            'Year': year
        })

    # Calculate total interest savings and total tenure reduced
    original_interest = (monthly_payment * original_loan_term_months) - original_loan_amount
    new_interest = (monthly_payment * loan_term_months) - loan_amount
    interest_savings = original_interest - new_interest
    tenure_reduced_months = original_loan_term_months - loan_term_months

    summary = [interest_savings, tenure_reduced_months]
    return schedule, summary

schedule, summaary = calculate_loan_schedule(loan_amount, number_of_payments, monthly_prepayment)
df = pd.DataFrame(schedule)

st.write("### Saved Because of Prepayments")
col1, col2, _ = st.columns(3)
col1.metric(label="Interest Saved", value=f"₹{summaary[0]:,.2f}")
col2.metric(label="Tenure Reduced", value=f"{summaary[1]} months")

# Display the data-frame as a chart.
st.write("### Payment Schedule")
payments_df = df[["Year", "Remaining Balance"]].groupby("Year").min()
st.line_chart(payments_df,
              x_label="Years",
              y="Remaining Balance")

st.line_chart(df.set_index('Month')[["Principal Payment", "Interest Payment", "Prepayment"]],
              x_label="Months",
              y_label="Monthly Payment")

if show_table:
    st.table(df[["Year", "Month", "Monthly Payment", "Interest Payment", "Principal Payment", "Prepayment", "Remaining Balance"]])