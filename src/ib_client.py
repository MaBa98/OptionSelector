from ib_insync import IB, Stock, Option
import pandas as pd

class IBClient:
    """
    Wrapper per connessione a Interactive Brokers tramite ib_insync.
    In modalità demo, restituisce DataFrame vuoti o dati di esempio.
    """
    def __init__(self, ib: IB):
        self.ib = ib

    @classmethod
    def connect(cls, host: str, port: int, client_id: int):
        ib = IB()
        try:
            ib.connect(host, port, clientId=client_id)
        except Exception:
            ib = None
        return cls(ib)

    def get_underlying_price(self, symbol: str) -> float:
        ticker = self.ib.reqMktData(Stock(symbol, "SMART", "USD"), "", False, False)
        self.ib.sleep(0.5)
        return float(ticker.marketPrice())

    def fetch_option_chain(self, symbol: str, expiration: str):
        """
        Ritorna un DataFrame con strike, right, bid, ask, iv, oi, delta, dte.
        """
        opts = self.ib.reqSecDefOptParams(symbol, "", "STK", 0)
        chain = []
        for exp in opts:
            if exp.expirations and expiration in exp.expirations:
                for strike in exp.strikes:
                    contract = Option(symbol, expiration, strike, 'P', 'SMART')
                    ticker = self.ib.reqMktData(contract, "", False, False)
                    self.ib.sleep(0.1)
                    chain.append({
                        "strike": strike,
                        "bid": ticker.bid,
                        "ask": ticker.ask,
                        "iv": ticker.impliedVolatility,
                        "oi": ticker.openInterest,
                        "delta": ticker.modelGreeks.delta,
                        "dte": exp.lastTradeDateOrContractMonth  # semplificato
                    })
        return pd.DataFrame(chain).dropna()
