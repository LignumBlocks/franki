# noqa: F401
from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
import talib.abstract as ta


class StrategyA_Tendencial(IStrategy):
    """
    Tendencial ligera:
    - Entra cuando EMA rápida cruza sobre EMA lenta con ADX > umbral.
    - Sale por cruce inverso o por TP/SL.
    """

    timeframe = "1h"
    can_short = False  # Mantén long-only al inicio. Luego puedes habilitar shorts.
    startup_candle_count = 200

    # Gestión de riesgo básica
    stoploss = -0.03  # -3%
    minimal_roi = {
        "0": 0.03,     # 3% desde el inicio (simple)
    }
    trailing_stop = False

    def populate_indicators(self, df: DataFrame, metadata: dict) -> DataFrame:
        # EMAs
        df["ema_fast"] = ta.EMA(df["close"], timeperiod=20)
        df["ema_slow"] = ta.EMA(df["close"], timeperiod=50)
        # ADX para confirmar tendencia
        df["adx"] = ta.ADX(df["high"], df["low"], df["close"], timeperiod=14)
        return df

    def populate_entry_trend(self, df: DataFrame, metadata: dict) -> DataFrame:
        df.loc[
            (
                (df["ema_fast"] > df["ema_slow"]) &
                (df["ema_fast"].shift(1) <= df["ema_slow"].shift(1)) &  # cruce
                (df["adx"] > 20) &  # evita laterales
                (df["volume"] > 0)
            ),
            ["enter_long", "enter_tag"]
        ] = (1, "ema_cross_adx")
        return df

    def populate_exit_trend(self, df: DataFrame, metadata: dict) -> DataFrame:
        # Salida por cruce inverso o debilidad de ADX
        df.loc[
            (
                (df["ema_fast"] < df["ema_slow"]) |
                (df["adx"] < 15)
            ),
            ["exit_long", "exit_tag"]
        ] = (1, "ema_cross_down_or_weak_trend")
        return df
