# -----------------------------------------
# FIX PYTHON PATH
# -----------------------------------------
import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# -----------------------------------------
# IMPORTS
# -----------------------------------------
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from sqlalchemy import create_engine
from datetime import datetime

from ingestion.file_uploader import load_file
from analytics.risk_engine import assign_risk
from database.db_loader import load_to_db

# -----------------------------------------
# PAGE CONFIG
# -----------------------------------------
st.set_page_config(
    page_title="Credit Card Misuse Analytics",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------
# DATABASE CONNECTION
# -----------------------------------------
engine = create_engine(
    "mysql+pymysql://root:mysql123@localhost/card_misuse_analytics"
)

# -----------------------------------------
# LOAD DATA
# -----------------------------------------
@st.cache_data(ttl=60)
def load_data():
    return pd.read_sql("SELECT * FROM vw_latest_transactions", engine)

df = load_data()

# -----------------------------------------
# CSV HELPER
# -----------------------------------------
@st.cache_data
def convert_df_to_csv(dataframe):
    return dataframe.to_csv(index=False).encode("utf-8")

# -----------------------------------------
# SIDEBAR
# -----------------------------------------
with st.sidebar:
    st.markdown("## 💳 Card Analytics")
    uploaded_file = st.file_uploader(
        "Upload CSV / Excel",
        type=["csv", "xlsx", "xls"]
    )

# -----------------------------------------
# FILE UPLOAD HANDLER (SAFE)
# -----------------------------------------
if uploaded_file:
    try:
        with st.spinner("Processing data..."):
            df_new = load_file(uploaded_file)

            required_cols = {"transaction_id", "amount"}
            missing = required_cols - set(df_new.columns)

            if missing:
                st.error(f"Missing required columns: {missing}")
                st.stop()

            # Assign risk ONLY if customer_id exists
            if "customer_id" in df_new.columns:
                df_new = assign_risk(df_new)
            else:
                df_new["risk_level"] = "Normal"

            load_to_db(df_new, uploaded_file.name)

        st.success("✓ Data uploaded successfully")
        st.cache_data.clear()
        st.rerun()

    except Exception as e:
        st.error(f"Upload failed: {e}")
        st.stop()

# -----------------------------------------
# HEADER
# -----------------------------------------
st.markdown("""
<div class='main-header'>
    <div class='main-title'>💳 Credit Card Misuse Analytics</div>
    <div class='main-subtitle'>Real-time transaction monitoring</div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------
# SEARCH
# -----------------------------------------
search = st.text_input("Search (customer / city / channel)")

if search:
    df = df[
        df.astype(str)
        .apply(lambda x: x.str.contains(search, case=False, na=False))
        .any(axis=1)
    ]

# -----------------------------------------
# FILTERS (SAFE)
# -----------------------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    if "customer_id" in df.columns:
        customer = st.selectbox("Customer", ["All"] + sorted(df["customer_id"].dropna().unique()))
    else:
        customer = "All"

with col2:
    risk = st.selectbox("Risk", ["All"] + sorted(df["risk_level"].dropna().unique()))

with col3:
    channel = st.selectbox("Channel", ["All"] + sorted(df["channel"].dropna().unique()))

with col4:
    city = st.selectbox("City", ["All"] + sorted(df["city"].dropna().unique()))

if customer != "All" and "customer_id" in df.columns:
    df = df[df["customer_id"] == customer]
if risk != "All":
    df = df[df["risk_level"] == risk]
if channel != "All":
    df = df[df["channel"] == channel]
if city != "All":
    df = df[df["city"] == city]

# -----------------------------------------
# METRICS
# -----------------------------------------
m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric("Total Txns", len(df))
with m2:
    st.metric("Normal", (df["risk_level"] == "Normal").sum())
with m3:
    st.metric("Amount", f"₹{df['amount'].sum():,.0f}")
with m4:
    st.metric("High Risk", (df["risk_level"] == "High Risk").sum())

# -----------------------------------------
# DONUT CHART
# -----------------------------------------
risk_counts = df["risk_level"].value_counts()

fig = go.Figure(go.Pie(
    labels=risk_counts.index,
    values=risk_counts.values,
    hole=0.55
))

fig.update_layout(height=400)
st.plotly_chart(fig, width="stretch")

# -----------------------------------------
# YEAR BAR (SAFE COPY)
# -----------------------------------------
if "transaction_date" in df.columns:
    df_temp = df.copy()
    df_temp["transaction_date"] = pd.to_datetime(df_temp["transaction_date"], errors="coerce")
    df_temp["year"] = df_temp["transaction_date"].dt.year
    year_counts = df_temp["year"].value_counts().sort_index()

    fig_year = go.Figure(go.Bar(
        x=year_counts.index,
        y=year_counts.values
    ))

    st.plotly_chart(fig_year, width="stretch")

# -----------------------------------------
# TRANSACTION TABLE
# -----------------------------------------
st.dataframe(df.head(100), use_container_width=True, height=500)

# -----------------------------------------
# DOWNLOAD
# -----------------------------------------
st.download_button(
    "Download CSV",
    convert_df_to_csv(df),
    file_name=f"transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
    mime="text/csv"
)
