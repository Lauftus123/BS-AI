import streamlit as st
import os
import requests
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

st.set_page_config(page_title="FinAgent - AI Decision Support for Finance", page_icon="🤖", layout="wide")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

PRESETS = {
    "smallbiz": {
        "name": "Harare Trading Co.",
        "sector": "Retail & Trade",
        "revenue": 320000,
        "assets": 480000,
        "liabilities": 290000,
        "profit": 42000,
        "credit": 620,
        "years": 4,
        "context": "Applying for a working capital loan of USD 80,000 to expand inventory ahead of the festive season. Consistent revenue growth of 15% YoY over the past 3 years."
    },
    "startup": {
        "name": "ZimTech Solutions",
        "sector": "Information Technology",
        "revenue": 95000,
        "assets": 210000,
        "liabilities": 150000,
        "profit": -18000,
        "credit": 590,
        "years": 2,
        "context": "Early-stage fintech startup with a SaaS product. Currently pre-profit but has secured seed funding of USD 200,000. High growth trajectory with 3 enterprise clients."
    },
    "individual": {
        "name": "T. Moyo (Individual)",
        "sector": "Personal Finance",
        "revenue": 48000,
        "assets": 125000,
        "liabilities": 65000,
        "profit": 12000,
        "credit": 710,
        "years": 0,
        "context": "Salaried employee looking to invest USD 30,000 in a diversified portfolio. Risk-moderate investor with a 10-year time horizon. Currently holds government bonds and savings."
    },
    "corporate": {
        "name": "AfriMine Resources Ltd",
        "sector": "Mining & Resources",
        "revenue": 8500000,
        "assets": 22000000,
        "liabilities": 14000000,
        "profit": 1200000,
        "credit": 740,
        "years": 12,
        "context": "Large mining corporation seeking acquisition financing for a lithium processing facility. Strong cash flow, some currency risk exposure due to USD-denominated debt."
    }
}

ANALYSIS_LABELS = {
    "credit_risk": "Credit Risk Assessment",
    "investment": "Investment Portfolio Analysis",
    "fraud": "Fraud Detection & Anomaly Analysis",
    "forecast": "Financial Forecasting",
    "advisory": "Automated Advisory Report"
}

def get_risk_level(debt_ratio, credit_score, profit):
    score = 0
    if debt_ratio < 0.4:
        score += 2
    elif debt_ratio < 0.6:
        score += 1
    if credit_score > 700:
        score += 2
    elif credit_score > 600:
        score += 1
    if profit > 0:
        score += 2
    if score >= 5:
        return "low"
    if score >= 3:
        return "medium"
    return "high"

def format_analysis(text):
    lines = text.split("\n")
    formatted = []
    in_list = False
    for line in lines:
        line = line.strip()
        if line.startswith("## "):
            formatted.append(f"<h3>{line[3:]}</h3>")
            in_list = False
        elif line.startswith("1. ") or line.startswith("2. ") or line.startswith("3. ") or line.startswith("4. ") or line.startswith("5. "):
            if not in_list:
                formatted.append("<ul>")
                in_list = True
            formatted.append(f"<li>{line[3:]}</li>")
        elif line.startswith("-"):
            if not in_list:
                formatted.append("<ul>")
                in_list = True
            formatted.append(f"<li>{line[1:].strip()}</li>")
        elif in_list and not line:
            formatted.append("</ul>")
            in_list = False
        elif line:
            if in_list:
                formatted.append("</ul>")
                in_list = False
            formatted.append(f"<p>{line}</p>")
    return "".join(formatted)

if "history" not in st.session_state:
    st.session_state.history = []

st.markdown("""
<style>
    :root {
        --bg: #0a0e17;
        --surface: #111827;
        --surface2: #1a2235;
        --border: #1e2d45;
        --accent: #00d4aa;
        --accent2: #3b82f6;
        --accent3: #f59e0b;
        --danger: #ef4444;
        --text: #e2e8f0;
        --muted: #64748b;
        --green: #10b981;
        --red: #ef4444;
    }
    .stApp {
        background: var(--bg);
        color: var(--text);
    }
    .main-header {
        text-align: center;
        padding: 40px 0 30px;
    }
    .main-header h1 {
        font-family: 'Syne', sans-serif;
        font-size: 2.5rem;
        font-weight: 800;
        margin: 10px 0;
    }
    .main-header h1 em {
        color: var(--accent);
    }
    .workflow-box {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        margin-bottom: 30px;
    }
    .workflow-steps {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        flex-wrap: wrap;
    }
    .workflow-step {
        background: var(--surface2);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 12px 16px;
    }
    .score-card {
        background: var(--surface2);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 14px;
        text-align: center;
    }
    .risk-badge {
        display: inline-flex;
        align-items: center;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .risk-low { background: rgba(16,185,129,0.15); color: #10b981; border: 1px solid rgba(16,185,129,0.3); }
    .risk-medium { background: rgba(245,158,11,0.15); color: #f59e0b; border: 1px solid rgba(245,158,11,0.3); }
    .risk-high { background: rgba(239,68,68,0.15); color: #ef4444; border: 1px solid rgba(239,68,68,0.3); }
    .analysis-content h3 {
        font-family: 'Syne', sans-serif;
        font-size: 1rem;
        color: var(--accent);
        margin: 20px 0 8px;
        padding-bottom: 6px;
        border-bottom: 1px solid rgba(0,212,170,0.15);
    }
    .analysis-content p { margin-bottom: 10px; }
    .analysis-content ul { padding-left: 20px; margin-bottom: 10px; }
    .analysis-content li { margin-bottom: 4px; }
    .history-item {
        background: var(--surface2);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 8px;
    }
    .thinking-step {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 6px 0;
        color: var(--muted);
    }
    .thinking-step.done { color: var(--green); }
    .thinking-step.active { color: var(--accent); }
    .step-dot {
        width: 6px; height: 6px;
        border-radius: 50%;
        background: currentColor;
    }
    .step-dot.spinning {
        animation: spin 0.8s linear infinite;
        border-radius: 0;
        background: none;
        border: 2px solid currentColor;
        border-top-color: transparent;
    }
    @keyframes spin { to { transform: rotate(360deg); } }
    .positive { color: var(--green); }
    .negative { color: var(--red); }
    .neutral { color: var(--accent3); }
    .stButton>button {
        background: linear-gradient(135deg, var(--accent), #00b894);
        border: none;
        border-radius: 10px;
        color: #0a0e17;
        font-family: 'Syne', sans-serif;
        font-weight: 700;
        padding: 12px 24px;
        width: 100%;
    }
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 8px 24px rgba(0,212,170,0.25);
    }
    .stButton>button:disabled {
        opacity: 0.5;
    }
    .preset-btn {
        background: var(--surface2);
        border: 1px solid var(--border);
        border-radius: 6px;
        color: var(--muted);
        font-size: 0.75rem;
        padding: 6px 12px;
        cursor: pointer;
    }
    .preset-btn:hover { border-color: var(--accent); color: var(--accent); }
    .about-box {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 20px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>Intelligent <em>Financial</em> Analysis Agent</h1>
    <p style="color: var(--muted); max-width: 600px; margin: 0 auto;">
        An AI-powered agent that ingests financial data, reasons through it using LLM intelligence, and generates structured decision-support outputs for banking, investment, and risk management.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

col1, col2 = st.columns([2, 1], gap="large")

with col1:
    st.markdown("### 📋 Financial Data Input")
    
    analysis_type = st.selectbox("Analysis Type", list(ANALYSIS_LABELS.keys()), format_func=lambda x: ANALYSIS_LABELS[x])
    
    # Excel Upload Option
    st.markdown("**Or Upload Excel File**")
    uploaded_file = st.file_uploader("Upload Excel file with financial data", type=['xlsx', 'xls'])
    
    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            st.dataframe(df, use_container_width=True)
            st.session_state.excel_data = df
            st.success(f"Loaded {len(df)} rows from Excel file")
        except Exception as e:
            st.error(f"Error reading Excel: {e}")
    
    st.markdown("**Quick Presets**")
    preset_cols = st.columns(4)
    with preset_cols[0]:
        if st.button("Small Business", key="preset_smallbiz"):
            st.session_state.preset = "smallbiz"
    with preset_cols[1]:
        if st.button("Tech Startup", key="preset_startup"):
            st.session_state.preset = "startup"
    with preset_cols[2]:
        if st.button("Individual", key="preset_individual"):
            st.session_state.preset = "individual"
    with preset_cols[3]:
        if st.button("Corporate", key="preset_corporate"):
            st.session_state.preset = "corporate"

    if "preset" in st.session_state:
        p = PRESETS[st.session_state.preset]
        entity_name = st.text_input("Entity / Client Name", p["name"])
        sector = st.text_input("Industry / Sector", p["sector"])
        revenue = st.number_input("Annual Revenue (USD)", value=p["revenue"])
        assets = st.number_input("Total Assets (USD)", value=p["assets"])
        liabilities = st.number_input("Total Liabilities (USD)", value=p["liabilities"])
        profit = st.number_input("Net Profit / Loss (USD)", value=p["profit"])
        credit_score = st.number_input("Credit Score", value=p["credit"], min_value=300, max_value=850)
        years = st.number_input("Years in Operation", value=p["years"], min_value=0)
        context = st.text_area("Additional Context / Notes", p["context"])
    else:
        entity_name = st.text_input("Entity / Client Name", "Harare Trading Co.")
        sector = st.text_input("Industry / Sector", "Retail & Trade")
        revenue = st.number_input("Annual Revenue (USD)", value=320000)
        assets = st.number_input("Total Assets (USD)", value=480000)
        liabilities = st.number_input("Total Liabilities (USD)", value=290000)
        profit = st.number_input("Net Profit / Loss (USD)", value=42000)
        credit_score = st.number_input("Credit Score", value=620, min_value=300, max_value=850)
        years = st.number_input("Years in Operation", value=4, min_value=0)
        context = st.text_area("Additional Context / Notes", "Applying for a working capital loan of USD 80,000 to expand inventory.")

    run_btn = st.button("🚀 Run AI Agent Analysis")

with col2:
    st.markdown("### 📁 Analysis History")
    if st.session_state.history:
        for h in st.session_state.history[:6]:
            st.markdown(f"""
            <div class="history-item">
                <strong>{h['entity']}</strong><br>
                <small style="color: var(--muted)">{h['type']}</small><br>
                <span class="risk-badge risk-{h['risk']}" style="font-size: 0.65rem; padding: 2px 6px;">{h['risk'].upper()}</span>
                <span style="float: right; font-size: 0.7rem; color: var(--muted);">{h['time']}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("<p style='color: var(--muted); font-size: 0.85rem;'>No analyses run yet.</p>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div class="about-box">
        <p style="font-size: 0.85rem; font-weight: 600; margin-bottom: 8px;">ℹ️ About This Agent</p>
        <p style="font-size: 0.8rem; color: var(--muted); line-height: 1.6;">
            This AI agent uses <strong>Llama 3 via OpenRouter</strong> as its free LLM reasoning engine.
        </p>
        <p style="font-size: 0.8rem; color: var(--muted); margin-top: 8px;">
            <strong>HBF2212 Capstone Project</strong> — Great Zimbabwe University
        </p>
    </div>
    """, unsafe_allow_html=True)

if run_btn:
    # Use Excel data if uploaded, otherwise use form inputs
    if "excel_data" in st.session_state and st.session_state.excel_data is not None:
        df = st.session_state.excel_data
        # Extract data from first row of Excel
        entity_name = str(df.iloc[0].get("Entity Name", df.iloc[0].get("entity", "Excel Entity")))
        sector = str(df.iloc[0].get("Sector", df.iloc[0].get("sector", "General")))
        revenue = float(df.iloc[0].get("Revenue", df.iloc[0].get("revenue", 0)))
        assets = float(df.iloc[0].get("Assets", df.iloc[0].get("assets", 0)))
        liabilities = float(df.iloc[0].get("Liabilities", df.iloc[0].get("liabilities", 0)))
        profit = float(df.iloc[0].get("Profit", df.iloc[0].get("profit", 0)))
        credit_score = int(df.iloc[0].get("Credit Score", df.iloc[0].get("credit_score", 650)))
        years = int(df.iloc[0].get("Years", df.iloc[0].get("years", 1)))
        context = str(df.iloc[0].get("Context", df.iloc[0].get("context", "Excel data analysis")))
    
    debt_ratio = assets / assets if assets > 0 else 0
    profit_margin = (profit / revenue * 100) if revenue > 0 else 0
    equity = assets - liabilities
    current_risk = get_risk_level(debt_ratio, credit_score, profit)
    analysis_label = ANALYSIS_LABELS[analysis_type]

    with st.spinner("🤔 Agent is analyzing..."):
        thinking_phases = [
            "Ingesting and validating financial data...",
            "Computing financial ratios and indicators...",
            "Building analysis context for LLM reasoning engine...",
            "Running LLM analysis and generating insights...",
            "Structuring decision-support output..."
        ]
        
        progress_bar = st.progress(0)
        for i, phase in enumerate(thinking_phases):
            st.markdown(f"<div class='thinking-step active'><div class='step-dot spinning'></div> {phase}</div>", unsafe_allow_html=True)
            progress_bar.progress((i + 1) / len(thinking_phases))
        
        prompt = f"""You are an expert AI financial analyst and decision-support agent for a financial institution.

Analyse the following financial data and produce a comprehensive {analysis_label} report.

CLIENT DATA:
- Entity: {entity_name}
- Sector: {sector}
- Years in Operation: {years}
- Annual Revenue: USD {revenue:,}
- Total Assets: USD {assets:,}
- Total Liabilities: USD {liabilities:,}
- Net Profit/Loss: USD {profit:,}
- Equity: USD {equity:,}
- Debt-to-Asset Ratio: {debt_ratio*100:.1f}%
- Profit Margin: {profit_margin:.1f}%
- Credit Score: {credit_score}
- Additional Context: {context}

ANALYSIS TYPE: {analysis_label}

Produce a structured report with these sections:
1. **Executive Summary** - 2-3 sentence overview
2. **Key Financial Metrics** - Interpret the ratios
3. **Risk Assessment** - Identify specific risks with reasoning
4. **Opportunities** - Identify financial opportunities or strengths
5. **Recommendations** - 3-5 concrete actionable recommendations
6. **Limitations & Ethical Considerations** - Note data limitations
7. **Conclusion** - Overall decision-support verdict

Use specific numbers. Be analytical, professional, and precise."""

    if not GROQ_API_KEY:
        st.error("⚠️ GROQ_API_KEY not set. Please configure your API key.")
        st.info("Get a free API key from https://console.groq.com/keys")
    else:
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.1-8b-instant",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 1200
                },
                timeout=60
            )
            
            if response.status_code != 200:
                st.error(f"API Error: {response.text}")
            else:
                data = response.json()
                text = data["choices"][0]["message"]["content"]
                
                st.session_state.history.insert(0, {
                    "entity": entity_name,
                    "type": analysis_label,
                    "time": datetime.now().strftime("%H:%M"),
                    "risk": current_risk
                })
                
                risk_class = f"risk-{current_risk}"
                risk_emoji = "🟢" if current_risk == "low" else "🟡" if current_risk == "medium" else "🔴"
                
                st.markdown("---")
                st.markdown("### 📊 Agent Output & Decision Support Report")
                
                col_s1, col_s2, col_s3 = st.columns(3)
                with col_s1:
                    st.markdown(f"""
                    <div class="score-card">
                        <div class="score-val {'positive' if profit >= 0 else 'negative'}">{profit_margin:.1f}%</div>
                        <div class="score-label">Profit Margin</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_s2:
                    st.markdown(f"""
                    <div class="score-card">
                        <div class="score-val {'positive' if debt_ratio < 0.5 else 'neutral' if debt_ratio < 0.7 else 'negative'}">{debt_ratio*100:.0f}%</div>
                        <div class="score-label">Debt Ratio</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_s3:
                    st.markdown(f"""
                    <div class="score-card">
                        <div class="score-val {'positive' if credit_score >= 700 else 'neutral' if credit_score >= 600 else 'negative'}">{credit_score}</div>
                        <div class="score-label">Credit Score</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style="margin: 16px 0;">
                    <span class="risk-badge {risk_class}">{risk_emoji} {current_risk.upper()} RISK</span>
                    <span style="font-size: 0.8rem; color: var(--muted); margin-left: 10px;">{analysis_label} · {entity_name}</span>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"<div class='analysis-content'>{format_analysis(text)}</div>", unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"Agent Error: {str(e)}")