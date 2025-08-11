#!/usr/bin/env bash
set -e

# Ruta base
BASE=/freqtrade
UD=$BASE/user_data

# Asegura carpetas de logs
mkdir -p $UD/instances/live/logs $UD/instances/a/logs $UD/instances/b/logs $UD/instances/d/logs

# Comando base (comparten datadir)
CMD="trade --datadir $UD/data/hyperliquid"

# Lanza cada instancia en background (mergea common + override)
freqtrade $CMD -c $UD/config.common.json -c $UD/instances/live/config.live.json &
PID_LIVE=$!

freqtrade $CMD -c $UD/config.common.json -c $UD/instances/a/config.a.json &
PID_A=$!

freqtrade $CMD -c $UD/config.common.json -c $UD/instances/b/config.b.json &
PID_B=$!

freqtrade $CMD -c $UD/config.common.json -c $UD/instances/d/config.d.json --freqaimodel LightGBMRegressor &
PID_D=$!

# Espera a que terminen (mantiene el contenedor vivo)
wait -n $PID_LIVE $PID_A $PID_B $PID_D
