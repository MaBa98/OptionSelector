import asyncio
import nest_asyncio

# abilita asyncio dentro Streamlit (event loop multiplo)
nest_asyncio.apply()
asyncio.set_event_loop(asyncio.new_event_loop())
import streamlit as st
from src.ib_client import IBClient
from src.volatility import HistoricalVolatility
from src.scoring import StrikeScorer
from src.utils import format_percentage, safe_connect

st.set_page_config(page_title="Option Writing Scorer", layout="wide")

# Sidebar: credenziali e connessione IB
st.sidebar.title("🔑 Config IB")
ib_conf = st.secrets.get("IB", {})

host      = ib_conf.get("host", "127.0.0.1")
port      = ib_conf.get("port", 7497)
client_id = ib_conf.get("client_id", 1)

# Avviso in caso di fallback demo
if "IB" not in st.secrets:
    st.warning("⚠️ Nessuna credenziale IB trovata, uso valori di default per demo")

ib = safe_connect(host, port, client_id)

st.sidebar.title("📋 Input Sottostante")
ticker = st.sidebar.text_input("Ticker (es. AAPL)", value="")
exp_date = st.sidebar.date_input("Expiration Date")
st.sidebar.markdown("---")

if not ticker:
    st.info("Inserisci un ticker per iniziare.")
    st.stop()

# Calcolo volatilità storica
hv_calc = HistoricalVolatility(ib)
hv = hv_calc.compute(ticker, windows=[10, 20, 60])

# Scorer di strike
scorer = StrikeScorer(ib, hv)
results = scorer.score_strikes(
    ticker=ticker,
    expiration=exp_date,
    moneyness_perc=[0, -0.01, -0.02, -0.03, -0.05],
    min_open_interest=100,
    min_put_yield=0.015
)

st.title(f"📝 Strike Scoring per {ticker} - Exp: {exp_date}")

if results.empty:
    st.warning("Nessuna opzione soddisfa i filtri.")
else:
    st.dataframe(
        results.assign(
            moneyness=lambda df: df["moneyness"].map(format_percentage),
            put_yield=lambda df: df["put_yield"].map(format_percentage),
            score=lambda df: df["score"].round(3)
        ),
        use_container_width=True
    )

    st.markdown("### 📊 Distribuzione Score")
    st.bar_chart(results.set_index("strike")["score"])
