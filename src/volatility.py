import numpy as np
import pandas as pd

class HistoricalVolatility:
    """
    Calcola volatilità storica su finestre multiple.
    """
    def __init__(self, ib_client):
        self.ib = ib_client

    def compute(self, symbol: str, windows: list[int]) -> dict[str, float]:
        # Recupera prezzo storico demo / placeholder
        # Qui si integrerebbe con dati reali (IB o altra fonte)
        df = pd.DataFrame()  # demo
        df["close"] = np.random.lognormal(mean=0, sigma=0.02, size=100)

        log_ret = np.log(df["close"] / df["close"].shift(1)).dropna()
        result = {}
        for w in windows:
            hv = log_ret.rolling(w).std() * np.sqrt(252)
            result[w] = float(hv.mean())
        return result
