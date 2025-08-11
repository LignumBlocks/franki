# Base image de Freqtrade
FROM freqtradeorg/freqtrade:stable_freqaitorch

# Copiamos e instalamos el SDK de Hyperliquid
COPY ../hyperliquid-python-sdk /hyperliquid-python-sdk
RUN pip install /hyperliquid-python-sdk

# Copia el lanzador multi-instancia y dale permisos
COPY start.sh /start.sh

# Directorio de trabajo de Freqtrade
WORKDIR /freqtrade

# El contenedor arrancará el script (no el binario directo)
ENTRYPOINT ["/start.sh"]