# -----------------------------------------
# FIX PYTHON PATH
# -----------------------------------------
import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

# -----------------------------------------
# IMPORTS
# -----------------------------------------
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
from datetime import datetime
import io

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
# CUSTOM CSS (Enhanced Power BI Style)
# -----------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@300;400;600;700;800&display=swap');
    
    /* Main Background - Dark Blue like Power BI */
    .stApp {
        background: linear-gradient(135deg, #0d2847 0%, #1a3a5c 50%, #0d2847 100%);
        font-family: 'Segoe UI', sans-serif;
    }
    
    /* Hide Streamlit Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Segoe UI', sans-serif !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    p, div, span, label {
        font-family: 'Segoe UI', sans-serif !important;
        color: #e8f0f7 !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3a5f 0%, #0d2847 100%);
        border-right: 2px solid #2d4a6d;
    }
    
    /* Sidebar Headers */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #00d4ff !important;
        font-weight: 700 !important;
    }
    
    /* Metric Cards - Power BI Style */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d4a6d 100%);
        padding: 25px;
        border-radius: 10px;
        border-left: 5px solid #00bcf2;
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.4);
        transition: all 0.3s ease;
    }
    
    [data-testid="stMetric"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 24px rgba(0, 188, 242, 0.3);
        border-left-color: #00d4ff;
    }
    
    [data-testid="stMetric"] label {
        font-size: 12px !important;
        font-weight: 600 !important;
        color: #ffffff !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-size: 32px !important;
        font-weight: 700 !important;
        color: #00d4ff !important;
        text-shadow: 0 2px 4px rgba(0, 188, 242, 0.3);
    }
    
    /* Chart Containers - Enhanced */
    .chart-card {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d4a6d 100%);
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4);
        margin: 15px 0;
        border: 2px solid #2d4a6d;
        transition: all 0.3s ease;
    }
    
    .chart-card:hover {
        border-color: #00bcf2;
        box-shadow: 0 12px 30px rgba(0, 188, 242, 0.2);
    }
    
    .chart-title {
        font-size: 16px;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 20px;
        text-transform: uppercase;
        letter-spacing: 1px;
        border-bottom: 2px solid #00bcf2;
        padding-bottom: 10px;
    }
    
    /* Select Boxes - Enhanced */
    .stSelectbox > div > div {
        background: #2d4a6d !important;
        border: 2px solid #3d5a7d !important;
        border-radius: 6px;
        color: #ffffff !important;
    }
    
    .stSelectbox label {
        color: #ffffff !important;
        font-size: 13px !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* File Uploader */
    [data-testid="stFileUploader"] {
        background: #2d4a6d;
        padding: 25px;
        border-radius: 10px;
        border: 3px dashed #3d5a7d;
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #00bcf2;
        background: #1e3a5f;
        box-shadow: 0 4px 12px rgba(0, 188, 242, 0.2);
    }
    
    /* Data Table - Enhanced */
    .dataframe {
        background: #1e3a5f !important;
        color: #ffffff !important;
        border-radius: 10px;
        border: 1px solid #2d4a6d;
    }
    
    .dataframe th {
        background: #0d2847 !important;
        color: #00d4ff !important;
        font-weight: 800 !important;
        font-size: 13px !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        padding: 12px 8px !important;
        border-bottom: 2px solid #00bcf2 !important;
    }
    
    .dataframe td {
        color: #ffffff !important;
        font-weight: 500 !important;
        padding: 10px 8px !important;
        border-bottom: 1px solid #2d4a6d !important;
    }
    
    /* Search Box - Enhanced */
    .stTextInput > div > div > input {
        background: #2d4a6d !important;
        border: 2px solid #3d5a7d !important;
        border-radius: 6px;
        color: #ffffff !important;
        font-weight: 500 !important;
        padding: 10px 15px !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #00bcf2 !important;
        box-shadow: 0 0 0 2px rgba(0, 188, 242, 0.2) !important;
    }
    
    .stTextInput label {
        color: #ffffff !important;
        font-size: 13px !important;
        font-weight: 700 !important;
    }
    
    /* Header */
    .main-header {
        background: linear-gradient(90deg, #0d2847 0%, #1e3a5f 100%);
        padding: 30px 40px;
        border-radius: 12px;
        border-left: 6px solid #00bcf2;
        margin-bottom: 30px;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4);
    }
    
    .main-title {
        font-size: 32px;
        font-weight: 800;
        color: #ffffff;
        margin: 0;
        text-shadow: 0 3px 6px rgba(0, 0, 0, 0.3);
    }
    
    .main-subtitle {
        font-size: 14px;
        color: #b8c7d9;
        margin: 8px 0 0 0;
        font-weight: 500;
    }
    
    /* Buttons - Enhanced */
    .stButton > button {
        background: linear-gradient(135deg, #00bcf2 0%, #0095c7 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        box-shadow: 0 4px 12px rgba(0, 188, 242, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #00d4ff 0%, #00bcf2 100%) !important;
        box-shadow: 0 6px 16px rgba(0, 212, 255, 0.4) !important;
        transform: translateY(-2px);
    }
    
    /* Download Button Specific */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #00ff88 0%, #00cc6e 100%) !important;
        color: #0d2847 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        font-weight: 800 !important;
        font-size: 14px !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        box-shadow: 0 4px 12px rgba(0, 255, 136, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #00ffaa 0%, #00ff88 100%) !important;
        box-shadow: 0 6px 16px rgba(0, 255, 136, 0.5) !important;
        transform: translateY(-2px);
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 12px;
        height: 12px;
    }
    
    ::-webkit-scrollbar-track {
        background: #0d2847;
        border-radius: 6px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #2d4a6d 0%, #3d5a7d 100%);
        border-radius: 6px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #3d5a7d 0%, #4d6a8d 100%);
    }
    
    /* Multi-select styling */
    .stMultiSelect > div > div {
        background: #2d4a6d !important;
        border: 2px solid #3d5a7d !important;
    }
    
    /* Success/Error Messages */
    .stSuccess {
        background: linear-gradient(135deg, #1e4d3a 0%, #2d6d5a 100%) !important;
        color: #00ff88 !important;
        border-left: 5px solid #00ff88 !important;
        font-weight: 600 !important;
        padding: 15px !important;
        border-radius: 8px !important;
    }
    
    .stError {
        background: linear-gradient(135deg, #4d1e1e 0%, #6d2d2d 100%) !important;
        color: #ff4444 !important;
        border-left: 5px solid #ff4444 !important;
        font-weight: 600 !important;
        padding: 15px !important;
        border-radius: 8px !important;
    }
    
    /* Info Box */
    .info-box {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d4a6d 100%);
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #00bcf2;
        margin: 15px 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    
    .info-box p {
        font-size: 12px;
        margin: 5px 0;
        color: #ffffff !important;
        font-weight: 600;
    }
    
    .info-box .label {
        color: #00d4ff !important;
        font-weight: 700 !important;
    }
    
    /* Sidebar Transaction Box */
    .sidebar-txn-card {
        background: linear-gradient(135deg, #2d4a6d 0%, #1e3a5f 100%);
        padding: 15px;
        border-radius: 8px;
        border-left: 3px solid #00bcf2;
        margin: 10px 0;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.3);
        transition: all 0.2s ease;
    }
    
    .sidebar-txn-card:hover {
        border-left-color: #00d4ff;
        box-shadow: 0 5px 15px rgba(0, 188, 242, 0.3);
        transform: translateX(3px);
    }
    
    .sidebar-txn-card .txn-id {
        font-size: 11px;
        color: #00d4ff !important;
        font-weight: 700;
        margin-bottom: 8px;
    }
    
    .sidebar-txn-card .txn-detail {
        font-size: 10px;
        color: #ffffff !important;
        margin: 3px 0;
        font-weight: 500;
    }
    
    .sidebar-txn-card .risk-badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 9px;
        font-weight: 700;
        margin-top: 5px;
    }
    
    .risk-normal {
        background: #00bcf2;
        color: #0d2847;
    }
    
    .risk-medium {
        background: #ffa500;
        color: #0d2847;
    }
    
    .risk-high {
        background: #ff4444;
        color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------
# DATABASE CONNECTION
# -----------------------------------------
engine = create_engine(
    "mysql+pymysql://root:mysql123@localhost/card_misuse_analytics"
)

# -----------------------------------------
# LOAD DATA FROM DATABASE
# -----------------------------------------
@st.cache_data(ttl=60)
def load_data():
    return pd.read_sql("SELECT * FROM vw_latest_transactions", engine)

df = load_data()

# -----------------------------------------
# HELPER FUNCTION FOR CSV DOWNLOAD
# -----------------------------------------
@st.cache_data
def convert_df_to_csv(dataframe):
    return dataframe.to_csv(index=False).encode('utf-8')

# -----------------------------------------
# SIDEBAR
# -----------------------------------------
with st.sidebar:
    st.markdown("""
        <div style='text-align: center; padding: 20px 0;'>
            <div style='font-size: 50px; margin-bottom: 10px;'>💳</div>
            <h2 style='margin: 0; font-size: 20px; color: #00d4ff;'>Card Analytics</h2>
            <p style='margin: 5px 0 0 0; font-size: 12px; color: #7d8a9e;'>Misuse Detection System</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<hr style='border: none; border-top: 2px solid #2d4a6d; margin: 20px 0;'>", unsafe_allow_html=True)
    
    # Upload Section
    st.markdown("### 📤 UPLOAD DATASET")
    uploaded_file = st.file_uploader(
        "Choose CSV or Excel file",
        type=["csv", "xlsx", "xls"],
        label_visibility="collapsed"
    )
    
if uploaded_file:
    try:
        with st.spinner("Processing data..."):
            df_new = load_file(uploaded_file)

            # 🔒 FINAL VALIDATION (UI-level)
            required_cols = {"transaction_id", "customer_id", "amount"}
            missing = required_cols - set(df_new.columns)

            if missing:
                st.error(f"Uploaded file missing required columns: {missing}")
                st.stop()

            df_new = assign_risk(df_new)
            load_to_db(df_new, uploaded_file.name)

        st.success("✓ Data uploaded successfully!")
        st.rerun()

    except Exception as e:
        st.error(f"Upload failed: {e}")
        st.stop()

    st.markdown("<hr style='border: none; border-top: 2px solid #2d4a6d; margin: 20px 0;'>", unsafe_allow_html=True)
    
    # Recent Transactions in Sidebar
    st.markdown("### 📊 RECENT TRANSACTIONS")
    
    # Show last 5 transactions
    recent_txns = df.head(5)
    
    for idx, row in recent_txns.iterrows():
        # Determine risk badge class
        risk_class = "risk-normal"
        if row.get('risk_level') == "Medium Risk":
            risk_class = "risk-medium"
        elif row.get('risk_level') == "High Risk":
            risk_class = "risk-high"
        
        st.markdown(f"""
            <div class='sidebar-txn-card'>
                <div class='txn-id'>ID: {row.get('transaction_id', 'N/A')}</div>
                <div class='txn-detail'><b>Customer:</b> {row.get('customer_id', 'N/A')}</div>
                <div class='txn-detail'><b>Amount:</b> ₹{row.get('amount', 0):,.0f}</div>
                <div class='txn-detail'><b>City:</b> {row.get('city', 'N/A')}</div>
                <div class='txn-detail'><b>Channel:</b> {row.get('channel', 'N/A')}</div>
                <span class='risk-badge {risk_class}'>{row.get('risk_level', 'Normal')}</span>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<hr style='border: none; border-top: 2px solid #2d4a6d; margin: 20px 0;'>", unsafe_allow_html=True)
    
    # Download Section
    st.markdown("### 💾 DOWNLOAD DATA")
    
    csv_data = convert_df_to_csv(df)
    
    st.download_button(
        label="📥 Download Full Dataset (CSV)",
        data=csv_data,
        file_name=f"card_transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
    )
    
    st.markdown("<hr style='border: none; border-top: 2px solid #2d4a6d; margin: 20px 0;'>", unsafe_allow_html=True)
    
    # Info Section
    st.markdown(f"""
        <div class='info-box'>
            <p class='label'>SYSTEM STATUS</p>
            <p>🟢 Database: Connected</p>
            <p>📊 Records: {len(df):,}</p>
            <p>🕒 Last Updated: {datetime.now().strftime('%I:%M %p')}</p>
            <p>📅 {datetime.now().strftime('%B %d, %Y')}</p>
        </div>
    """, unsafe_allow_html=True)

# -----------------------------------------
# HEADER
# -----------------------------------------
st.markdown("""
    <div class='main-header'>
        <div class='main-title'>💳 Credit Card Misuse Analytics</div>
        <div class='main-subtitle'>Real-time transaction monitoring and fraud detection dashboard</div>
    </div>
""", unsafe_allow_html=True)

# -----------------------------------------
# SEARCH & FILTERS
# -----------------------------------------
st.markdown("### 🔍 Filters & Search")

# Search box
search_col1, search_col2 = st.columns([3, 1])
with search_col1:
    search_term = st.text_input("🔎 Search transactions", placeholder="Search by customer ID, city, or channel...", label_visibility="collapsed")

# Apply search filter
if search_term:
    df = df[
        df['customer_id'].astype(str).str.contains(search_term, case=False, na=False) |
        df['city'].astype(str).str.contains(search_term, case=False, na=False) |
        df['channel'].astype(str).str.contains(search_term, case=False, na=False)
    ]

# Filter section
st.markdown("<div style='margin: 15px 0;'>", unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)

with col1:
    customer = st.selectbox(
        "Customer ID",
        ["All"] + sorted(df["customer_id"].dropna().unique().tolist())
    )

with col2:
    risk = st.selectbox(
        "Risk Level",
        ["All"] + sorted(df["risk_level"].dropna().unique().tolist())
    )

with col3:
    channel = st.selectbox(
        "Channel",
        ["All"] + sorted(df["channel"].dropna().unique().tolist())
    )

with col4:
    city = st.selectbox(
        "City",
        ["All"] + sorted(df["city"].dropna().unique().tolist())
    )

# Apply filters
if customer != "All":
    df = df[df["customer_id"] == customer]
if risk != "All":
    df = df[df["risk_level"] == risk]
if channel != "All":
    df = df[df["channel"] == channel]
if city != "All":
    df = df[df["city"] == city]

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------
# KEY METRICS ROW
# -----------------------------------------
st.markdown("<div style='margin: 25px 0;'>", unsafe_allow_html=True)
m1, m2, m3, m4 = st.columns(4)

total_txns = len(df)
total_amount = df['amount'].sum()
normal_txns = (df["risk_level"] == "Normal").sum() if "Normal" in df["risk_level"].values else 0
high_risk_txns = (df["risk_level"] == "High Risk").sum()

with m1:
    st.metric("Total Transactions", f"{total_txns:,}")

with m2:
    st.metric("Normal Txns", f"{normal_txns:,}")

with m3:
    st.metric("Total Amount", f"₹{total_amount:,.0f}")

with m4:
    st.metric("High Risk Txns", f"{high_risk_txns:,}")

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------
# CHARTS ROW 1: Donut Chart + Bar Chart (LARGER)
# -----------------------------------------
chart_col1, chart_col2 = st.columns([1, 1])

# DONUT CHART - Risk Level Distribution (LARGER)
with chart_col1:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.markdown("<div class='chart-title'>Count of transaction_id by risk_level</div>", unsafe_allow_html=True)
    
    risk_counts = df['risk_level'].value_counts()
    
    # Power BI colors
    colors = {
        'Normal': '#00bcf2',
        'Medium Risk': '#ffa500',
        'High Risk': '#ff4444'
    }
    
    fig_donut = go.Figure(data=[go.Pie(
        labels=risk_counts.index,
        values=risk_counts.values,
        hole=0.55,
        marker=dict(
            colors=[colors.get(label, '#999999') for label in risk_counts.index],
            line=dict(color='#0d2847', width=3)
        ),
        textinfo='label+percent',
        textfont=dict(size=14, color='white', family='Segoe UI'),
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percent: %{percent}<extra></extra>'
    )])
    
    fig_donut.update_layout(
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400,
        margin=dict(l=20, r=20, t=20, b=20),
        legend=dict(
            font=dict(color='white', size=12, family='Segoe UI'),
            orientation='h',
            yanchor='bottom',
            y=-0.15,
            xanchor='center',
            x=0.5
        ),
        annotations=[dict(
            text=f'<b>{risk_counts.sum()}</b><br>Total',
            x=0.5, y=0.5,
            font=dict(size=24, color='white', family='Segoe UI'),
            showarrow=False
        )]
    )
    
    st.plotly_chart(fig_donut, use_container_width=True, key='donut_risk')
    st.markdown("</div>", unsafe_allow_html=True)

# BAR CHART - Transaction by Year (LARGER)
with chart_col2:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.markdown("<div class='chart-title'>Count of transaction_id by Year</div>", unsafe_allow_html=True)
    
    # Assuming you have a date column
    if 'transaction_date' in df.columns or 'date' in df.columns:
        date_col = 'transaction_date' if 'transaction_date' in df.columns else 'date'
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df['year'] = df[date_col].dt.year
        year_counts = df['year'].value_counts().sort_index()
    else:
        # If no date column, create sample data
        year_counts = pd.Series([total_txns], index=[2024])
    
    fig_year = go.Figure(data=[
        go.Bar(
            x=year_counts.index,
            y=year_counts.values,
            marker=dict(
                color='#00bcf2',
                line=dict(color='#0d2847', width=2)
            ),
            text=year_counts.values,
            textposition='outside',
            textfont=dict(color='white', size=14, family='Segoe UI', weight='bold')
        )
    ])
    
    fig_year.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400,
        margin=dict(l=20, r=20, t=20, b=60),
        xaxis=dict(
            showgrid=False,
            showline=True,
            linecolor='#3d5a7d',
            color='white',
            title=dict(text='Year', font=dict(size=14, family='Segoe UI')),
            tickfont=dict(size=12, family='Segoe UI')
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)',
            showline=False,
            color='white',
            title=dict(text='Count', font=dict(size=14, family='Segoe UI')),
            tickfont=dict(size=12, family='Segoe UI')
        )
    )
    
    st.plotly_chart(fig_year, use_container_width=True, key='bar_year')
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------
# CHARTS ROW 2: City Bar Chart + Channel Breakdown (LARGER)
# -----------------------------------------
chart_col3, chart_col4 = st.columns([2, 1])

# BAR CHART - Transactions by City (LARGER)
with chart_col3:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.markdown("<div class='chart-title'>Count of transaction_id by city</div>", unsafe_allow_html=True)
    
    city_counts = df['city'].value_counts().head(10)
    
    fig_city = go.Figure(data=[
        go.Bar(
            x=city_counts.values,
            y=city_counts.index,
            orientation='h',
            marker=dict(
                color='#00bcf2',
                line=dict(color='#0d2847', width=2)
            ),
            text=city_counts.values,
            textposition='outside',
            textfont=dict(color='white', size=12, family='Segoe UI', weight='bold')
        )
    ])
    
    fig_city.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=450,
        margin=dict(l=20, r=80, t=20, b=20),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)',
            showline=False,
            color='white',
            tickfont=dict(size=12, family='Segoe UI')
        ),
        yaxis=dict(
            showgrid=False,
            showline=False,
            color='white',
            tickfont=dict(size=12, family='Segoe UI')
        )
    )
    
    st.plotly_chart(fig_city, use_container_width=True, key='bar_city')
    st.markdown("</div>", unsafe_allow_html=True)

# CHANNEL LIST (LARGER)
with chart_col4:
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.markdown("<div class='chart-title'>channel</div>", unsafe_allow_html=True)
    
    channel_list = df['channel'].dropna().unique().tolist()
    
    for ch in sorted(channel_list):
        count = (df['channel'] == ch).sum()
        st.markdown(f"""
            <div style='padding: 12px; margin: 8px 0; background: linear-gradient(135deg, #1e3a5f 0%, #2d4a6d 100%); border-radius: 6px; border-left: 4px solid #00bcf2; box-shadow: 0 3px 8px rgba(0,0,0,0.3);'>
                <input type='checkbox' style='margin-right: 10px;'>
                <span style='color: #ffffff; font-size: 14px; font-weight: 600;'>{ch}</span>
                <span style='color: #00d4ff; font-size: 13px; font-weight: 700; margin-left: 10px;'>({count})</span>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------
# TRANSACTION TABLE WITH DOWNLOAD
# -----------------------------------------
st.markdown("<div style='margin-top: 30px;'>", unsafe_allow_html=True)
st.markdown("<div class='chart-card'>", unsafe_allow_html=True)

# Header with download button
table_header_col1, table_header_col2 = st.columns([3, 1])
with table_header_col1:
    st.markdown("<div class='chart-title'>📋 Transaction Details</div>", unsafe_allow_html=True)
with table_header_col2:
    csv_filtered = convert_df_to_csv(df)
    st.download_button(
        label="📥 Download Filtered",
        data=csv_filtered,
        file_name=f"filtered_transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
    )

# Format the dataframe for display
display_cols = [col for col in df.columns if col not in ['year']]
st.dataframe(
    df[display_cols].head(100),
    use_container_width=True,
    height=500
)

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------
# FOOTER
# -----------------------------------------
st.markdown("""
    <div style='text-align: center; padding: 40px 0; color: #7d8a9e; font-size: 12px;'>
        <p style='margin: 0; font-weight: 600;'>© 2024 Credit Card Analytics Dashboard</p>
        <p style='margin: 5px 0 0 0;'>Powered by  Streamlit & MySQL | Real-time Fraud Detection System</p>
    </div>
""", unsafe_allow_html=True)