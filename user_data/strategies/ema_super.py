from freqtrade.strategy import IStrategy

class ema_super(IStrategy):
    timeframe = '1h'
    minimal_roi = {"0": 0.10}
    stoploss = -0.02
    trailing_stop = False

    def populate_indicators(self, df, metadata):
        # Añade indicadores técnicos o features externos ya fusionados
        return df

    def populate_entry_trend(self, df, metadata):
        # Placeholder: reemplaza con tu lógica real + filtro FreqAI score
        df.loc[:, 'enter_long'] = False
        return df

    def populate_exit_trend(self, df, metadata):
        df.loc[:, 'exit_long'] = False
        return df
