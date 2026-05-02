# Daily Market Pulse Dashboard

A Streamlit web dashboard for US market sentiment:

- S&P 500 / Nasdaq / Dow / SPY / QQQ price trend
- VIX live/latest value and playbook
- CNN Fear & Greed live/latest value via unofficial endpoint, with manual fallback
- Correlation between market return, VIX change, and Fear & Greed change
- Strategy card based on VIX + Fear & Greed + index trend

## Run

```bash
cd ~/Desktop/market_sentiment_tool_v2
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open:

```text
http://localhost:8501
```

If port 8501 is occupied:

```bash
streamlit run app.py --server.port 8502
```

## Notes

CNN Fear & Greed has no stable official public API. This dashboard uses a best-effort unofficial endpoint. If CNN blocks or changes the endpoint, the app will use your manual fallback value and mark the data source clearly.

This is for information and research only, not investment advice.
