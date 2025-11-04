"""
Archivo integrador generado automaticamente
Directorio: /home/bautista/aqua_manager/src/AquaKeeper/config
Fecha: 2025-11-04 16:32:00
Total de archivos integrados: 3
"""

# ================================================================================
# ARCHIVO 1/3: __init__.py
# Ruta: /home/bautista/aqua_manager/src/AquaKeeper/config/__init__.py
# ================================================================================



# ================================================================================
# ARCHIVO 2/3: configuracion.py
# Ruta: /home/bautista/aqua_manager/src/AquaKeeper/config/configuracion.py
# ================================================================================

# aqua_manager/src/AquaKeeper/config/constantes.py
# Parámetros globales de negocio y umbrales

# Tamaños típicos (L)
PISCINA_CHICA_L   = 12000
PISCINA_MEDIANA_L = 25000
PISCINA_GRANDE_L  = 45000

# Dosis por 10.000 L (referencia)
# (valores estimativos tipo ficha técnica — ajustá a tu cartera real)
DOSIS_CLORO_MANTENIMIENTO_G_10K    = 30     # gr/10kL (diario/mantenimiento)
DOSIS_CLORO_CHOQUE_G_10K           = 120    # gr/10kL (choque)
DOSIS_CLARIFICADOR_ML_10K          = 40     # ml/10kL
DOSIS_ALGUICIDA_ML_10K             = 25     # ml/10kL
DOSIS_ANTISARRO_ML_10K             = 35     # ml/10kL

# Umbrales para decisiones
PH_IDEAL_MIN = 7.2
PH_IDEAL_MAX = 7.6
TURBIDEZ_MAX_PERMITIDA = 30.0   # NTU equivalente (simulado)
ALGAS_UMBRAL_ALERTA    = 0.5    # 0..1

# Stock: mínimos
STOCK_MIN_LOCAL = 2         # en tu local (unidades)
STOCK_MIN_CLIENTE = 1       # cliente suele tener 1 o 2


# ================================================================================
# ARCHIVO 3/3: constantes.py
# Ruta: /home/bautista/aqua_manager/src/AquaKeeper/config/constantes.py
# ================================================================================

PISCINA_CHICA_L   = 12000
PISCINA_MEDIANA_L = 25000
PISCINA_GRANDE_L  = 45000

DOSIS_CLORO_MANTENIMIENTO_G_10K = 30
DOSIS_CLORO_CHOQUE_G_10K        = 120
DOSIS_CLARIFICADOR_ML_10K       = 40
DOSIS_ALGUICIDA_ML_10K          = 25
DOSIS_ANTISARRO_ML_10K          = 35

PH_IDEAL_MIN = 7.2
PH_IDEAL_MAX = 7.6
TURBIDEZ_MAX_PERMITIDA = 30.0
ALGAS_UMBRAL_ALERTA    = 0.5

STOCK_MIN_LOCAL   = 2
STOCK_MIN_CLIENTE = 1


