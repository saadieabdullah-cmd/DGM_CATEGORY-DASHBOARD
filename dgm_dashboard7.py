import streamlit as st
import pandas as pd
import plotly.express as px
import io
import requests

# Correct export link
FILE_URL = "https://docs.google.com/spreadsheets/d/1Md7v62OzmWGuZNz-GKzRQgQ2WFSRI7cv/export?format=xlsx"
DEFAULT_SHEET = "CY_vs_LY_Growth"

try:
    # Download Excel file from Google Sheets
    response = requests.get(FILE_URL)
    response.raise_for_status()

    # Read into pandas
    df = pd.read_excel(io.BytesIO(response.content), sheet_name=DEFAULT_SHEET, engine="openpyxl")

    st.success("✅ File loaded successfully!")
    st.dataframe(df.head())

except Exception as e:
    st.error(f"❌ Error reading Excel file: {e}")

DGM_COL = "DGM"
CATEGORY_COL = "Category"
STORE_COL = "Store Name"  # Or "Store ID" if needed

# Updated to match your actual column names
SALES_CY = "Net Sales"
SALES_LY = "Net Sales_LY"
GM_CY = "Gross Margin"
GM_LY = "Gross Margin_LY"
NP_CY = "Net profit / loss"
NP_LY = "Net profit / loss_LY"

# Updated expense columns based on your headers
EXPENSE_MAPPING = {
    "Advertisement": ("Advertisment Expenses", "Advertisment Expenses_LY"),
    "Financial": ("Financial Charges", "Financial Charges_LY"),
    "Variable Cost": ("Total variable cost", "Total variable cost_LY"),
    "Occupancy": ("Total Occupancy cost", "Total Occupancy cost_LY"),
    "Staff": ("Staff related costs", "Staff related costs_LY"),
    "Fixed Cost": ("Total fixed cost (stores related)", "Total fixed cost (stores related)_LY"),
    "Head Office": ("Head office Expenses", "Head office Expenses_LY")
}

DGM_PASSWORDS = {
    "Nadeem Khan": "pass123",
    "Farhan Akram": "pass124",
    "Syed Bilal": "Pass125",
    "Master User": "masterpass"  # Add Master User
}

# -------------------- MAIN APP --------------------
def main():
    current_user = authenticate_user()
    if not current_user:
        return

    df = load_data()
    if df.empty:
        return

    # Dashboard Title
    st.markdown(f"<h1 style='text-align: center;'>📊 Financial Performance Dashboard</h1>", unsafe_allow_html=True)
    
    # MASTER USER ACCESS - Show all data with DGM filter
    if current_user == "Master User":
        st.markdown(f"<h3 style='text-align: center; color: #d62728;'>👑 Master View (CFO/Controller)</h3>", unsafe_allow_html=True)
        
        st.sidebar.header("🔍 Master View Options")
        
        # DGM filter for Master User
        all_dgms = df[DGM_COL].unique()
        selected_dgms = st.sidebar.multiselect(
            "Select DGMs to View", 
            options=all_dgms, 
            default=all_dgms
        )
        df_filtered = df[df[DGM_COL].isin(selected_dgms)]
    else:
        # Regular DGM filtered view
        st.markdown(f"<h3 style='text-align: center; color: #1f77b4;'>DGM: {current_user}</h3>", unsafe_allow_html=True)
        df_filtered = df[df[DGM_COL] == current_user]

    if df_filtered.empty:
        st.warning("⚠️ No data found for the selected filters.")
        return

    # Apply additional filters (store and category)
    st.sidebar.header("🔍 Filter Options")
    
    # Store selection
    all_stores = df_filtered[STORE_COL].unique()
    selected_stores = st.sidebar.multiselect(
        "Select Stores", 
        options=all_stores, 
        default=all_stores
    )
    
    # Category selection
    all_categories = df_filtered[CATEGORY_COL].unique()
    selected_categories = st.sidebar.multiselect(
        "Select Categories", 
        options=all_categories, 
        default=all_categories
    )
    
    # Apply filters
    df_filtered = df_filtered[
        (df_filtered[STORE_COL].isin(selected_stores)) & 
        (df_filtered[CATEGORY_COL].isin(selected_categories))
    ]

    # Dashboard Title
    st.markdown(f"<h1 style='text-align: center;'>📊 Financial Performance Dashboard</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center; color: #1f77b4;'>User: {current_user}</h3>", unsafe_allow_html=True)

# -------------------- AUTH FUNCTION --------------------
def authenticate_user():
    st.title("🔐 DGM Secure Dashboard Login")
    username = st.text_input("👤 Enter your DGM name")
    password = st.text_input("🔑 Enter password", type="password")
    
    if username in DGM_PASSWORDS and DGM_PASSWORDS[username] == password:
        st.success(f"✅ Welcome {username}!")
        return username
    elif username and password:
        st.error("❌ Invalid credentials")
        return None
    else:
        return None

# -------------------- LOAD DATA --------------------
@st.cache_data
def load_data():
    try:
        # Download the file from Google Sheets (direct XLSX export link)
        response = requests.get(FILE_URL)
        response.raise_for_status()  # Raise error if request failed

        # Load into pandas from in-memory buffer
        data = pd.read_excel(io.BytesIO(response.content), sheet_name=DEFAULT_SHEET, engine="openpyxl")

        st.success(f"Loaded sheet: {DEFAULT_SHEET}")

        return data

    except Exception as e:
        st.error(f"❌ Error reading Excel file: {e}")
        return None


# -------------------- KPI CARDS --------------------
def render_kpi_cards(df):
    # Current year metrics
    total_sales_cy = df[SALES_CY].sum()
    total_sales_ly = df[SALES_LY].sum()
    total_gross_cy = df[GM_CY].sum()
    total_gross_ly = df[GM_LY].sum()
    total_net_cy = df[NP_CY].sum()
    total_net_ly = df[NP_LY].sum()
    
    # Calculate YoY changes
    sales_yoy = total_sales_cy - total_sales_ly
    gross_yoy = total_gross_cy - total_gross_ly
    net_yoy = total_net_cy - total_net_ly
    
    sales_yoy_pct = (sales_yoy / total_sales_ly * 100) if total_sales_ly != 0 else 0
    gross_yoy_pct = (gross_yoy / total_gross_ly * 100) if total_gross_ly != 0 else 0
    net_yoy_pct = (net_yoy / total_net_ly * 100) if total_net_ly != 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 Net Sales (CY)", f"{total_sales_cy:,.0f}", 
                 delta=f"{sales_yoy_pct:.1f}% ({sales_yoy:,.0f})",
                 help="Current Year vs Last Year")
    
    with col2:
        st.metric("📊 Gross Margin (CY)", f"{total_gross_cy:,.0f}", 
                 delta=f"{gross_yoy_pct:.1f}% ({gross_yoy:,.0f})")
    
    with col3:
        st.metric("💵 Net Profit (CY)", f"{total_net_cy:,.0f}", 
                 delta=f"{net_yoy_pct:.1f}% ({net_yoy:,.0f})")
    
    with col4:
        store_count = df[STORE_COL].nunique()
        st.metric("🏬 Stores", store_count, 
                 help="Number of stores in selection")

# -------------------- VISUALIZATIONS --------------------
def render_sales_profit_comparison(df):
    # Group by store and calculate sums
    store_summary = df.groupby(STORE_COL)[[
        SALES_CY, SALES_LY, 
        NP_CY, NP_LY
    ]].sum().reset_index()
    
    # Sort by current year sales
    store_summary = store_summary.sort_values(SALES_CY, ascending=False)
    
    fig = go.Figure()
    
    # Add bars for CY and LY sales
    fig.add_trace(go.Bar(
        x=store_summary[STORE_COL],
        y=store_summary[SALES_CY],
        name='Net Sales (CY)',
        marker_color='#1f77b4',
        text=store_summary[SALES_CY].apply(lambda x: f"{x:,.0f}"),
        textposition='auto'
    ))
    
    fig.add_trace(go.Bar(
        x=store_summary[STORE_COL],
        y=store_summary[SALES_LY],
        name='Net Sales (LY)',
        marker_color='#aec7e8',
        text=store_summary[SALES_LY].apply(lambda x: f"{x:,.0f}"),
        textposition='auto'
    ))
    
    # Add lines for profit
    fig.add_trace(go.Scatter(
        x=store_summary[STORE_COL],
        y=store_summary[NP_CY],
        name='Net Profit (CY)',
        mode='lines+markers+text',
        text=store_summary[NP_CY].apply(lambda x: f"{x:,.0f}"),
        textposition="top center",
        line=dict(color='#2ca02c', width=3),
        yaxis='y2'
    ))
    
    fig.add_trace(go.Scatter(
        x=store_summary[STORE_COL],
        y=store_summary[NP_LY],
        name='Net Profit (LY)',
        mode='lines+markers',
        line=dict(color='#98df8a', width=3),
        yaxis='y2'
    ))
    
    fig.update_layout(
        title='Store Performance: Sales vs Profit (CY vs LY)',
        xaxis_title='Store',
        yaxis_title='Net Sales ()',
        yaxis2=dict(
            title='Net Profit/Loss ()',
            overlaying='y',
            side='right'
        ),
        barmode='group',
        template='plotly_white',
        hovermode='x unified',
        height=600,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_yoy_growth(df):
    # Calculate YoY growth for each store
    store_summary = df.groupby(STORE_COL)[[
        SALES_CY, SALES_LY,
        GM_CY, GM_LY,
        NP_CY, NP_LY
    ]].sum().reset_index()
    
    store_summary['Sales Growth %'] = ((store_summary[SALES_CY] - store_summary[SALES_LY]) / 
                                      store_summary[SALES_LY]) * 100
    store_summary['Profit Growth %'] = ((store_summary[NP_CY] - store_summary[NP_LY]) / 
                                      store_summary[NP_LY]) * 100
    
    # Sort by sales growth
    store_summary = store_summary.sort_values('Sales Growth %', ascending=False)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=store_summary[STORE_COL],
        y=store_summary['Sales Growth %'],
        name='Sales Growth %',
        marker_color='#17becf',
        text=store_summary['Sales Growth %'].apply(lambda x: f"{x:.1f}%"),
        textposition='auto'
    ))
    
    fig.add_trace(go.Bar(
        x=store_summary[STORE_COL],
        y=store_summary['Profit Growth %'],
        name='Profit Growth %',
        marker_color='#bcbd22',
        text=store_summary['Profit Growth %'].apply(lambda x: f"{x:.1f}%"),
        textposition='auto'
    ))
    
    fig.update_layout(
        title='Year-over-Year Growth by Store',
        xaxis_title='Store',
        yaxis_title='Growth Percentage (%)',
        barmode='group',
        height=500,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_expense_comparison(df):
    # Prepare expense data
    expense_data = []
    for category, (cy_col, ly_col) in EXPENSE_MAPPING.items():
        cy_total = df[cy_col].sum()
        ly_total = df[ly_col].sum()
        yoy_change = cy_total - ly_total
        yoy_pct = (yoy_change / ly_total * 100) if ly_total != 0 else 0
        
        expense_data.append({
            'Expense Category': category,
            'Current Year': cy_total,
            'Last Year': ly_total,
            'YoY Change': yoy_change,
            'YoY %': yoy_pct
        })
    
    expense_summary = pd.DataFrame(expense_data)
    
    fig = make_subplots(rows=1, cols=2, 
                       specs=[[{"type": "bar"}, {"type": "bar"}]],
                       subplot_titles=('Expense Amounts', 'Year-over-Year Change'))
    
    # Expense amounts
    fig.add_trace(go.Bar(
        x=expense_summary['Expense Category'],
        y=expense_summary['Current Year'],
        name='Current Year',
        marker_color='#1f77b4',
        text=expense_summary['Current Year'].apply(lambda x: f"{x:,.0f}"),
        textposition='auto'
    ), row=1, col=1)
    
    fig.add_trace(go.Bar(
        x=expense_summary['Expense Category'],
        y=expense_summary['Last Year'],
        name='Last Year',
        marker_color='#aec7e8',
        text=expense_summary['Last Year'].apply(lambda x: f"{x:,.0f}"),
        textposition='auto'
    ), row=1, col=1)
    
    # YoY change
    colors = ['green' if x <= 0 else 'red' for x in expense_summary['YoY Change']]
    fig.add_trace(go.Bar(
        x=expense_summary['Expense Category'],
        y=expense_summary['YoY Change'],
        name='YoY Change',
        marker_color=colors,
        text=expense_summary['YoY Change'].apply(lambda x: f"{x:,.0f}"),
        textposition='auto'
    ), row=1, col=2)
    
    fig.update_layout(
        title_text='Expense Comparison: Current Year vs Last Year',
        barmode='group',
        showlegend=False,
        height=500
    )
    
    fig.update_yaxes(title_text="Amount ()", row=1, col=1)
    fig.update_yaxes(title_text="YoY Change ()", row=1, col=2)
    
    st.plotly_chart(fig, use_container_width=True)

def render_category_performance(df):
    category_summary = df.groupby(CATEGORY_COL)[[
        SALES_CY, SALES_LY,
        NP_CY, NP_LY
    ]].sum()
    
    # Calculate growth metrics
    category_summary['Sales Growth'] = category_summary[SALES_CY] - category_summary[SALES_LY]
    category_summary['Profit Growth'] = category_summary[NP_CY] - category_summary[NP_LY]
    category_summary['Sales Growth %'] = (category_summary['Sales Growth'] / category_summary[SALES_LY]) * 100
    category_summary['Profit Margin %'] = (category_summary[NP_CY] / category_summary[SALES_CY]) * 100
    
    category_summary = category_summary.sort_values(SALES_CY, ascending=False)
    
    # Create subplots
    fig = make_subplots(rows=2, cols=1, 
                        specs=[[{"type": "bar"}], [{"type": "bar"}]],
                        subplot_titles=('Sales Performance', 'Profitability'))
    
    # Sales bar chart - CY vs LY
    fig.add_trace(go.Bar(
        x=category_summary.index,
        y=category_summary[SALES_CY],
        name='Current Year Sales',
        marker_color='#1f77b4',
        text=category_summary[SALES_CY].apply(lambda x: f"{x:,.0f}"),
        textposition='auto'
    ), row=1, col=1)
    
    fig.add_trace(go.Bar(
        x=category_summary.index,
        y=category_summary[SALES_LY],
        name='Last Year Sales',
        marker_color='#aec7e8',
        text=category_summary[SALES_LY].apply(lambda x: f"{x:,.0f}"),
        textposition='auto'
    ), row=1, col=1)
    
    # Profit bar chart - CY vs LY
    fig.add_trace(go.Bar(
        x=category_summary.index,
        y=category_summary[NP_CY],
        name='Current Year Profit',
        marker_color='#2ca02c',
        text=category_summary[NP_CY].apply(lambda x: f"{x:,.0f}"),
        textposition='auto'
    ), row=2, col=1)
    
    fig.add_trace(go.Bar(
        x=category_summary.index,
        y=category_summary[NP_LY],
        name='Last Year Profit',
        marker_color='#98df8a',
        text=category_summary[NP_LY].apply(lambda x: f"{x:,.0f}"),
        textposition='auto'
    ), row=2, col=1)
    
    fig.update_layout(
        title_text='Category Performance Analysis',
        height=800,
        barmode='group',
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig, use_container_width=True)

# -------------------- FINANCIAL INSIGHTS --------------------
def generate_financial_insights(df):
    st.subheader("🧠 Financial Controller's Insights")
    
    # Calculate key metrics with zero division handling
    total_sales_cy = df[SALES_CY].sum()
    total_sales_ly = df[SALES_LY].sum()
    total_net_cy = df[NP_CY].sum()
    total_net_ly = df[NP_LY].sum()
    
    sales_yoy = total_sales_cy - total_sales_ly
    sales_yoy_pct = (sales_yoy / total_sales_ly * 100) if total_sales_ly != 0 else 0
    
    net_yoy = total_net_cy - total_net_ly
    net_yoy_pct = (net_yoy / total_net_ly * 100) if total_net_ly != 0 else 0
    
    # Generate insights
    insights = []
    
    # Sales performance
    if sales_yoy > 0:
        insights.append(f"📈 **Sales Growth:** Total sales increased by **{sales_yoy:,.0f} ({sales_yoy_pct:.1f}%)** compared to last year")
    else:
        insights.append(f"⚠️ **Sales Decline:** Total sales decreased by **{abs(sales_yoy):,.0f} ({abs(sales_yoy_pct):.1f}%)** compared to last year")
    
    # Profitability performance
    if net_yoy > 0:
        insights.append(f"💰 **Profit Growth:** Net profit increased by **{net_yoy:,.0f} ({net_yoy_pct:.1f}%)** compared to last year")
    else:
        insights.append(f"⚠️ **Profit Decline:** Net profit decreased by **{abs(net_yoy):,.0f} ({abs(net_yoy_pct):.1f}%)** compared to last year")
    
    # Store performance
    store_profits = df.groupby(STORE_COL)[NP_CY].sum()
    top_store = store_profits.idxmax()
    bottom_store = store_profits.idxmin()
    insights.append(f"🏬 **Store Performance:** '{top_store}' is the top performing store, while '{bottom_store}' needs attention")
    
    # Expense analysis
    
    # Display insights
    for insight in insights:
        st.info(insight)
    
    # Actionable recommendations
    st.subheader("🎯 Recommended Actions")
    
    if net_yoy > 0:
        actions = [
            "🚀 Continue successful strategies from top-performing categories",
            "📊 Analyze what's working in high-growth stores and replicate",
            "💰 Invest in marketing for categories with highest profit margins",
            "🏆 Recognize top-performing store managers"
        ]
    else:
        actions = [
            "🔍 Investigate cost structure of underperforming stores",
            "📉 Review pricing strategy for low-margin categories",
            "🔄 Optimize inventory to reduce carrying costs",
            "📝 Develop turnaround plan for bottom-performing stores"
        ]
    
    for action in actions:
        st.markdown(f"- {action}")

# -------------------- MAIN APP --------------------
def main():
    current_dgm = authenticate_user()
    if not current_dgm:
        return

    df = load_data()
    if df.empty:
        return

    # Filter by DGM
    df_filtered = df[df[DGM_COL] == current_dgm]

    if df_filtered.empty:
        st.warning("⚠️ No data found for your stores.")
        return

    # Apply additional filters
    st.sidebar.header("🔍 Filter Options")
    
    # Store selection
    all_stores = df_filtered[STORE_COL].unique()
    selected_stores = st.sidebar.multiselect(
        "Select Stores", 
        options=all_stores, 
        default=all_stores
    )
    
    # Category selection
    all_categories = df_filtered[CATEGORY_COL].unique()
    selected_categories = st.sidebar.multiselect(
        "Select Categories", 
        options=all_categories, 
        default=all_categories
    )
    
    # Apply filters
    df_filtered = df_filtered[
        (df_filtered[STORE_COL].isin(selected_stores)) & 
        (df_filtered[CATEGORY_COL].isin(selected_categories))
    ]

    # Dashboard Title
    st.markdown(f"<h1 style='text-align: center;'>📊 Financial Performance Dashboard</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center; color: #1f77b4;'>DGM: {current_dgm}</h3>", unsafe_allow_html=True)
    
    # KPI Cards with YoY comparison
    render_kpi_cards(df_filtered)
    
    # Financial Insights
    generate_financial_insights(df_filtered)
    
    # Visualization Section
    st.header("📈 Performance Visualizations")
    
    # Create tabs for different visualizations
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Sales vs Profit", 
        "YoY Growth", 
        "Expense Analysis", 
        "Category Performance",
        "Detailed Data"
    ])
    
    with tab1:
        render_sales_profit_comparison(df_filtered)
    
    with tab2:
        render_yoy_growth(df_filtered)
    
    with tab3:
        render_expense_comparison(df_filtered)
    
    with tab4:
        render_category_performance(df_filtered)
    
    with tab5:
        st.header("🔍 Detailed Data View")
        
        # Format currency columns
        formatted_df = df_filtered.copy()
        currency_cols = [
            SALES_CY, SALES_LY, GM_CY, GM_LY, NP_CY, NP_LY,
            "Cost of Sales", "Cost of Sales_LY",
            "Advertisment Expenses", "Advertisment Expenses_LY",
            "Financial Charges", "Financial Charges_LY",
            "Total variable cost", "Total variable cost_LY",
            "Total Occupancy cost", "Total Occupancy cost_LY",
            "Staff related costs", "Staff related costs_LY",
            "Total fixed cost (stores related)", "Total fixed cost (stores related)_LY",
            "Head office Expenses", "Head office Expenses_LY"
        ]
        
        for col in currency_cols:
            if col in formatted_df.columns:
                formatted_df[col] = formatted_df[col].apply(lambda x: f"{x:,.0f}" if pd.notnull(x) else "")
        
        st.dataframe(formatted_df, height=600)
        
        # Download button
        csv = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Filtered Data",
            data=csv,
            file_name=f'financial_report_{current_dgm}.csv',
            mime='text/csv'
        )

# -------------------- RUN APP --------------------
if __name__ == "__main__":
    st.set_page_config(
        page_title="DGM Financial Dashboard", 
        page_icon="📊", 
        layout="wide"
    )
    main()



