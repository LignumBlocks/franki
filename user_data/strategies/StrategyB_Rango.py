from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
import talib.abstract as ta


class StrategyB_Rango(IStrategy):
    """
    Rango ligera:
    - Compra sobreventa en RSI con precio cerca de banda inferior de Bollinger.
    - Vende cuando RSI vuelve a neutro/alto o toca banda media/superior.
    """

    timeframe = "1h"
    can_short = False
    startup_candle_count = 200  # asegúrate de tener suficiente histórico

    # Gestión de riesgo básica
    stoploss = -0.025  # -2.5%
    minimal_roi = {
        "0": 0.02,  # 2%
    }
    trailing_stop = False

    def populate_indicators(self, df: DataFrame, metadata: dict) -> DataFrame:
        # RSI
        df["rsi"] = ta.RSI(df["close"], timeperiod=14)

        # Bandas de Bollinger (TA-Lib requiere floats para nbdevup/nbdevdn)
        upper, mid, lower = ta.BBANDS(
            df["close"],
            timeperiod=20,
            nbdevup=2.0,
            nbdevdn=2.0,
            matype=0,  # 0 = SMA
        )
        df["bb_high"] = upper
        df["bb_mid"] = mid
        df["bb_low"] = lower

        return df

    def populate_entry_trend(self, df: DataFrame, metadata: dict) -> DataFrame:
        df.loc[
            (
                (df["rsi"] < 35) &
                (df["close"] <= df["bb_low"]) &
                (df["volume"] > 0)
            ),
            ["enter_long", "enter_tag"]
        ] = (1, "rsi_bband_entry")
        return df

    def populate_exit_trend(self, df: DataFrame, metadata: dict) -> DataFrame:
        df.loc[
            (
                (df["rsi"] >= 55) |
                (df["close"] >= df["bb_mid"])
            ),
            ["exit_long", "exit_tag"]
        ] = (1, "rsi_bband_exit")
        return df
