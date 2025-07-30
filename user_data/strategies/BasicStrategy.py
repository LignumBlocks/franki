from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame

class BasicStrategy(IStrategy):
    timeframe = '1h'

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["buy"] = 0
        dataframe.loc[dataframe["close"] < dataframe["close"].rolling(10).mean(), "buy"] = 1
        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["sell"] = 0
        dataframe.loc[dataframe["close"] > dataframe["close"].rolling(10).mean(), "sell"] = 1
        return dataframe
