import streamlit as st
import pandas as pd
import google.generativeai as genai

st.set_page_config(page_title="AI Business Analyst - E-commerce", layout="wide")

st.title("AI Business Analyst - E-commerce")

# Gemini API Key
api_key = st.text_input(
    "Enter Gemini API Key",
    type="password"
)

if api_key:
    genai.configure(api_key=api_key)

st.write("Upload your sales CSV file to get started.")

# Manager Brief
st.subheader("Manager Brief")

manager_brief = st.text_area(
    "Enter a business question:",
    placeholder="Why is sales declining? Which category should we promote? Which region needs attention?"
)

# File Upload
uploaded_file = st.file_uploader(
    "Upload a CSV file",
    type=["csv"]
)

if uploaded_file is not None:

    try:
        df = pd.read_csv(uploaded_file, encoding="utf-8")
    except:
        df = pd.read_csv(uploaded_file, encoding="latin1")

    st.subheader("1. Data Preview")

    st.write(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")

    st.dataframe(df.head())

    st.write("Available Columns:")
    st.write(df.columns.tolist())

    # KPIs
    sales_col = "Sales"
    profit_col = "Profit"

    if sales_col in df.columns and profit_col in df.columns:

        total_sales = df[sales_col].sum()
        total_profit = df[profit_col].sum()

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Total Sales",
                f"${total_sales:,.2f}"
            )

        with col2:
            st.metric(
                "Total Profit",
                f"${total_profit:,.2f}"
            )

        # Category Chart
        if "Category" in df.columns:

            category_sales = (
                df.groupby("Category")["Sales"]
                .sum()
                .sort_values(ascending=False)
            )

            st.subheader("Sales by Category")
            st.bar_chart(category_sales)

        # Region Chart
        if "Region" in df.columns:

            region_sales = (
                df.groupby("Region")["Sales"]
                .sum()
                .sort_values(ascending=False)
            )

            st.subheader("Sales by Region")
            st.bar_chart(region_sales)

        # Monthly Trend
        if "Order.Date" in df.columns:

            df["Order.Date"] = pd.to_datetime(
                df["Order.Date"],
                errors="coerce"
            )

            monthly_sales = (
                df.groupby(
                    df["Order.Date"].dt.to_period("M")
                )["Sales"]
                .sum()
            )

            monthly_sales.index = monthly_sales.index.astype(str)

            st.subheader("Monthly Sales Trend")
            st.line_chart(monthly_sales)

        # Manager Brief Output
        if manager_brief:

            st.subheader("Manager Question")
            st.write(manager_brief)

            st.subheader("Business Summary")

            st.write(f"""
Total Sales: ${total_sales:,.2f}

Total Profit: ${total_profit:,.2f}

Top Category: {category_sales.idxmax()}

Top Region: {region_sales.idxmax()}
""")

            # AI Insights
            if api_key:

                prompt = f"""
You are an E-commerce Business Analyst.

Total Sales: {total_sales}
Total Profit: {total_profit}

Top Category: {category_sales.idxmax()}
Top Region: {region_sales.idxmax()}

Manager Question:
{manager_brief}

Give 5 business insights and recommendations.
"""

                try:

                    model = genai.GenerativeModel(
                        "gemini-2.5-flash"
                    )

                    response = model.generate_content(
                        prompt
                    )

                    st.subheader("AI Business Insights")

                    st.write(response.text)

                except Exception as e:

                    st.error(
                        f"AI Error: {e}"
                    )

    st.subheader("2. Basic Info")
    st.write(df.dtypes)

    st.subheader("3. Summary Statistics")
    st.write(df.describe())

else:
    st.info(
        "Please upload an e-commerce sales CSV to begin."
    )