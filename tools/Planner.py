import streamlit as st
import pandas as pd
import numpy as np

st.header("Planner")
st.subheader("Basic", divider="gray")
col1, col2, col3 = st.columns(3)
age = col1.slider("Current Age", min_value=15, max_value=100, value=35)
retirement_age = col2.slider("Retirement Age", min_value=35, max_value=100, value=60)
live_till = col3.slider("Life Expectancy", min_value=65, max_value=100, value=85)

inflation = col1.number_input("Inflattion Rate", min_value=0.0, max_value=100.0, value=6.0) / 100
cap_gain_tax = col2.number_input("Capital Gain Tax", min_value=0.0, max_value=100.0, value=20.0) / 100
income_tax = col3.number_input("Income Tax", min_value=0.0, max_value=100.0, value=30.0) / 100

st.subheader("Income", divider="gray")
col1, col2 = st.columns(2)
col1.markdown("**Monthly Income After Taxes & Deductions**")
in_df = pd.DataFrame({
    "Income Stream": ["Salary", "Other Income1", "Other Income2", "Other Income3"],
    "Montly Income": [50000, 0, 0, 0],
})

income_df = col1.data_editor(
            in_df,
            column_config={
                "Montly Income": st.column_config.NumberColumn(
                min_value=0,
                step=1,
                format="₹ %d",
                ),
            },
            hide_index=True,
)

monthly_income = income_df["Montly Income"].sum()
col1.metric("Total Monthly Income", f"₹ {monthly_income}")


col2.markdown("*Yearly Income After Taxes & Deductions**")
yr_df = pd.DataFrame({
        "Income Stream": ["Bonus", "Extra Income1", "Extra Income2", "Extra Income3"],
        "Yearly Income": [5250, 0, 0, 0],
})

yr_income_df = col2.data_editor(
             yr_df,
            column_config={
                "Yearly Income": st.column_config.NumberColumn(
                min_value=0, step=1, format="₹ %d",
                ),
                },
            hide_index=True,
            )

yearly_income = yr_income_df["Yearly Income"].sum()
col2.metric("Total Yearly Income", f"₹ {yearly_income}")

st.subheader("Expenses", divider="gray")
col1, col2 = st.columns(2)
col1.markdown("**Monthly Expenses**")
ex_df = pd.DataFrame({
    "Expense Stream": ["Rent", "EMI1", "EMI2", "Living Expenses", "Desire Expenses"],
    "Montly Expense": [10000, 1000, 0, 0, 0],
    }
    )

expense_df = col1.data_editor(
    ex_df,
    column_config={
        "Montly Expense": st.column_config.NumberColumn(
        min_value=0, step=1, format="₹ %d",
        ),
    },
    hide_index=True,
)

monthly_expense = expense_df ["Montly Expense" ].sum()
col1.metric("Total Monthly Expenses", f"₹ {monthly_expense}")

col2.markdown("**Yearly Expenses**")
yr_ex_df = pd.DataFrame({
    "Expense Stream": ["Insurance", "Expense1", "Expense2", "Expense3", "Expense4"],
    "Yearly Expense": [2000, 0, 0, 0, 0],
    })


yr_expense_df = col2.data_editor(
                    yr_ex_df,
                    column_config={
                        "Yearly Expense": st.column_config.NumberColumn(
                        min_value=0, step=1, format="₹ %d",
                        ),
                    },
                    hide_index=True,
)

yearly_expense = yr_expense_df["Yearly Expense"].sum()
col2.metric("Total Yearly Expenses", f"₹ {yearly_expense}")

monthly_excess = monthly_income - monthly_expense
yearly_excess = yearly_income - yearly_expense

balances_tab, portfolio_tab, plan_tab = st.tabs(["Balances", "Portpolio", "Financial Plan"])

with balances_tab:
    st.subheader("Remaining Balance")
    col1, col2 = st.columns(2)
    col1.metric(label="Monthly Excess", value=f"₹ {monthly_excess}", delta=f"{monthly_excess / monthly_income:.0%}")
    col2.metric(label="Yearly Excess", value=f"₹ {yearly_excess}", delta=f"{yearly_excess / yearly_income:.0%}" if yearly_income != 0 else 0)

with portfolio_tab:
    st.subheader("Investment Portpolio")
    col1, col2 = st.columns(2)
    total_invest_per_month = monthly_excess
    safe_asset_proportion = age / 100
    stock_asset_proportion = 1 - safe_asset_proportion

    safe_asset_investment = int(total_invest_per_month * safe_asset_proportion)
    stock_asset_investment = int(total_invest_per_month * stock_asset_proportion)
    sa_irr = 7
    safe_asset_df = pd.DataFrame(
        {
            "Safe Asset": ["FD/RD", "EPF/VPF/PPF", "Gold/SGB", "Corporate Bonds"],
            "IRR": [f"~ {sa_irr}%", f"~ {sa_irr}%", f"~ {sa_irr}%", f"~ {sa_irr}%"],
            "Investment": ["ANY", "ANY", "ANY", "ANY"],
        }
    )


    def get_investment_distribution(age):
        table = {
        "Largecap": {"20-30": 40, "30-40": 50, "40+": 60},
        "Midcap":   {"20-30": 30, "30-40": 30, "40+": 30},
        "Smallcap": {"20-30": 30, "30-40": 20, "40+": 10},
        }
        age_range = "20-30" if age < 30 else "30-40" if age < 40 else "40+"
        # Get the percentages for each category
        return [percentages [age_range] for percentages in table.values()]


    distribution = get_investment_distribution(age)
    investments = [stock_asset_investment * percent/100 for percent in distribution]
    mf_irr = [12, 15, 18]
    stock_asset_df = pd.DataFrame(
        {
            "Stock Asset": ["Largecap Mutual Funds", "Midcap Mutual Funds", "Smallcap Mutual Funds"],
            "IRR": [ f"~ {num}%" for num in mf_irr],
            "Distribution": [f"{num}%" for num in distribution],
            "Investment": investments,
        }
    )

    st.info("Based on your age and risk profile, I suggest the following investment distribution", icon="™")
    col1, col2, col3 = st.columns(3)
    col1.metric("Safe Asset Investment",  f"{safe_asset_proportion:.0%}")
    col2.metric("Stock Asset Investment", f"{stock_asset_proportion:.0%}")

    col1.metric("Safe Asset Investment", f"₹ {safe_asset_investment}")
    col2.metric("Stock Asset Investment", f"₹ {stock_asset_investment}")

    st.markdown("**Investment Options**")
    st.dataframe(safe_asset_df, hide_index=True)
    st.dataframe(stock_asset_df, hide_index=True)

    # Calculate the sum product
    blend_stock_return = np.dot(distribution, mf_irr)
    col3.metric("Blended Stock Return", f" {blend_stock_return/100}%")


with plan_tab:
    st.subheader("Financial Planinng")
    st.markdown("**Investment Approach**")
    irr = [sa_irr] + mf_irr
    tax_p = [ int(num*100) for num in (income_tax, cap_gain_tax, cap_gain_tax, cap_gain_tax)]
    cur_inv_share = [(safe_asset_proportion*100)] + [(stock_asset_proportion*num) for num in distribution]
    retirement_inv_share = [50, 50, 0, 0]
    save_approch_df = pd.DataFrame(
        {
            "Asset": ["Fixed Returns", "Largecap Mutual Funds", "Midcap Mutual Funds", "Smallcap Mutual Funds"],
            "Returns":[ f"{num}%" for num in irr],
            "Tax on Gain" :  [ f"{num}%" for num in tax_p],
            "Current Investment Share": [ f"{num}%" for num in cur_inv_share],
            "Retirement Investment Share": [ f"{num}%" for num in retirement_inv_share],
        }
    )
    st.dataframe(save_approch_df, hide_index=True)
    col1, buff, col2 = st.columns([2,1,2])

    blend_inv_return = np.dot(irr, cur_inv_share)/100
    blended_inv_tax = np.dot(tax_p, cur_inv_share)/100
    col1.metric("Blended Current Return", f"{blend_inv_return}%")
    col2.metric("Blended Current Tax", f"{blended_inv_tax}%")

    blen_ret_return = np.dot(irr, retirement_inv_share)/100
    blended_ret_tax = np.dot(tax_p, retirement_inv_share)/100
    col1.metric("Blended Retirement Return", f"{blen_ret_return}%")
    col2.metric("Blended Retirement Tax", f"{blended_ret_tax}%")

    col1, col2, col3 = st.columns([1.5,2,2])
    step_up_per_year = col1.number_input("Step Up Investment Per Year", min_value=1, max_value=50, value=5)
    cur_lumpsom_inv = col2.number_input("Lumpsum Investment", min_value=1, value=500000)
    post_ret_amount_need = col3.number_input("Amount Need Per Month Post Retirement", min_value=1, value=80000)

    def get_end_save(cur_status, current_investment, additional_expense, additional_saving, planned_exp):
        if cur_status == "Dead": return 0
        if cur_status == "Earning":
            end_saving = current_investment + (current_investment * blend_inv_return/100) + additional_saving
            end_saving = end_saving - planned_exp/(1-blended_ret_tax/100) - additional_expense/(1-blended_ret_tax/100)
        else:
            end_saving = current_investment + (current_investment * blen_ret_return/100) + additional_saving
            end_saving = end_saving - planned_exp - additional_expense
        return end_saving

    retirement_plan_df = pd.DataFrame()
    current_investment = cur_lumpsom_inv
    additional_expense = 0

    for current_age in range(age,100):
        if "df" in st.session_state:
            additional_expense = round(st.session_state.df.loc[st.session_state.df["Age"] == current_age, "Additional Expenses"].iloc[0])

        if current_age == age:
            cur_status = "Earning"
            additional_saving = monthly_excess*12
            planned_exp = 0
        elif current_age < retirement_age:
            cur_status = "Earning"
            additional_saving = additional_saving + (additional_saving * step_up_per_year/100)
            planned_exp = 0
        elif current_age < live_till:
            cur_status = "Retired"
            additional_saving = 0
            if current_age == retirement_age:
                planned_exp = post_ret_amount_need * (1 + inflation) ** (retirement_age - age) * 12
            else:
                planned_exp = pm_planned_exp + (pm_planned_exp * inflation)
        elif current_age >= live_till:
            cur_status = "Dead"
            planned_exp = 0
            additional_saving = 0

        end_saving = get_end_save(cur_status, current_investment, additional_expense, additional_saving, planned_exp)

        retirement_plan_df = retirement_plan_df._append(
            {
                "Age": current_age,
                "Current Saving": round(current_investment),
                "Planned Expenses": round(planned_exp),
                "Additional Expenses": round(additional_expense),
                "Additional Saving": round(additional_saving),
                "End Saving": round(end_saving),
                "Status": cur_status,
            },
            ignore_index=True
        )
        current_investment = end_saving
        pm_planned_exp = planned_exp
        if cur_status == "Dead": break


    with st.form("Additioanl_Expenses"):
        m_age = st.selectbox("Any additional expenses?", retirement_plan_df['Age'])
        m_add_exp = st.number_input("Additional Expense", min_value=0, value=0)
        submitted = st.form_submit_button("Submit")

    if submitted:
        #df = retirement_plan_df
        retirement_plan_df.loc[retirement_plan_df["Age"] == m_age, "Additional Expenses"] = m_add_exp
        for current_age in range(age,99):
            i = current_age - age
            if current_age < live_till:
                if i > 0:
                    retirement_plan_df.loc[i, "Current Saving"] = round(retirement_plan_df.loc[i-1, "End Saving"])

                row = retirement_plan_df.loc[retirement_plan_df["Age"] == current_age]
                retirement_plan_df.loc[i, "End Saving"] = round(get_end_save(row["Status"].iloc[0], row["Current Saving"].iloc[0],
                                                    row["Additional Expenses"].iloc[0], row["Additional Saving"].iloc[0],
                                                    row["Planned Expenses"].iloc[0]))
        st.session_state.df = retirement_plan_df

    if ("df" not in st.session_state) or (not retirement_plan_df.equals(st.session_state.df)):
        st.session_state.df = retirement_plan_df
    else:
        retirement_plan_df = st.session_state.df

    num_rows = len(retirement_plan_df)
    st.dataframe(st.session_state.df,
                hide_index=True,
                use_container_width=True,
                height=(num_rows + 1) * 35 + 3)
