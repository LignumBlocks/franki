# Base image de Freqtrade
FROM freqtradeorg/freqtrade:stable_freqaitorch

# Copiamos e instalamos el SDK de Hyperliquid
COPY ../hyperliquid-python-sdk /hyperliquid-python-sdk
RUN pip install /hyperliquid-python-sdk

# Copiamos tu configuración y estrategias
WORKDIR /freqtrade
