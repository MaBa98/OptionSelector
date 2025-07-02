import numpy as np
import pandas as pd
from math import exp

class StrikeScorer:
    """
    Applica scoring avanzato agli strike Put ATM/OTM.
    AS = (IV / HV_avg) * Delta * exp(-k * moneyness)
    """
    def __init__(self, ib_client, hv_dict: dict[int, float]):
        self.ib = ib_client
        self.hv = hv_dict
        # HV media su finestre 10,20,60
        self.hv_avg = np.mean(list(hv_dict.values()))

    def score_strikes(self, ticker: str, expiration, moneyness_perc: list[float],
                      min_open_interest: int, min_put_yield: float) -> pd.DataFrame:
        spot = self.ib.get_underlying_price(ticker)
        chain = self.ib.fetch_option_chain(ticker, expiration.isoformat())
        chain["moneyness"] = (chain["strike"] - spot) / spot
        # Filtri base
        df = chain[chain["oi"] >= min_open_interest].copy()
        # Yield put
        days = (expiration - pd.Timestamp.today().date()).days
        df["mid"] = (df["bid"] + df["ask"]) / 2
        df["put_yield"] = df["mid"] / df["strike"] * (365 / days)
        df = df[df["put_yield"] >= min_put_yield]

        # Scoring
        k = 0.5 / self.hv_avg
        df["score"] = (
            (df["iv"] / self.hv_avg)
            * df["delta"]
            * np.exp(-k * np.abs(df["moneyness"]))
        )

        # Scoriamo solo i livelli richiesti
        df = df[df["moneyness"].isin(moneyness_perc)]
        return df[[
            "strike", "moneyness", "bid", "ask", "mid", "iv", "delta", "oi", "dte", "put_yield", "score"
        ]].sort_values("score", ascending=False)
