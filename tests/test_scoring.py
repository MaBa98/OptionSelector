import pandas as pd
import numpy as np
from src.scoring import StrikeScorer

def test_score_computation():
    # HV di esempio
    hv = {10:0.2, 20:0.18, 60:0.22}
    class DummyIB:
        def get_underlying_price(self, sym): return 100
        def fetch_option_chain(self, sym, exp):
            data = {
                "strike": [100],
                "bid":[2.0], "ask":[2.2],
                "iv":[0.25], "oi":[200], "delta":[-0.4], "dte":[30]
            }
            return pd.DataFrame(data)
    scorer = StrikeScorer(DummyIB(), hv)
    df = scorer.score_strikes("DUMMY", pd.Timestamp.today().date(), [0], 100, 0.01)
    assert not df.empty
    # Score positivo
    assert df["score"].iloc[0] > 0
