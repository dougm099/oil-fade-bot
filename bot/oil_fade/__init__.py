"""Oil-fade package: strategy core + simulator + live runner."""
from .strategy import Bar, OilFadeConfig, OilFadeStrategy, TradeSignal

__all__ = ["Bar", "OilFadeConfig", "OilFadeStrategy", "TradeSignal"]
