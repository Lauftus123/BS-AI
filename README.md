# FinAgent - AI Decision Support for Finance

An AI-powered agent that ingests financial data, reasons through it using LLM intelligence, and generates structured decision-support outputs for banking, investment, and risk management.

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Free Groq API Key

### 1. Clone & Install

```bash
git clone <your-repo-url>
cd finagent
pip install -r requirements.txt
```

### 2. Get Free API Key

1. Go to https://console.groq.com/
2. Sign up (free, no credit card)
3. Go to **API Keys**
4. Create a new key

### 3. Configure

Create a `.env` file:
```bash
GROQ_API_KEY=your_key_here
```

### 4. Run Locally

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## ☁️ Deploy to Streamlit Cloud

### Deploy via GitHub

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "FinAgent v1.0"
   git branch -M main
   git remote add origin https://github.com/yourusername/finagent.git
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to https://share.streamlit.io
   - Connect your GitHub account
   - Select your repository
   - Set secrets:
     - `GROQ_API_KEY` = your API key
   - Deploy!

## 📋 Features

- **5 Analysis Types**: Credit Risk, Investment Portfolio, Fraud Detection, Financial Forecasting, Automated Advisory
- **4 Quick Presets**: Small Business, Tech Startup, Individual Investor, Corporate Client
- **Free LLM**: Uses Llama 3 via Groq (no cost, fast)
- **Risk Assessment**: Automated risk scoring with visual indicators
- **Analysis History**: Track previous analyses

## 🎓 Academic Info

**HBF2212 Capstone Project**  
Great Zimbabwe University, School of Business Sciences