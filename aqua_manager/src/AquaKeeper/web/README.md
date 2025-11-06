Probar el ping
http://127.0.0.1:8000

Probar la demo desde la API
http://127.0.0.1:8000/docs → botón “Try it out” en POST /run → Execute

Activar entorno virtual
source .venv/bin/activate

Correr demo clasica src/main
python3 src/main.py

Forma B de correr la demo
PYTHONPATH=src python3 -m AquaKeeper

Levantar la API desde entorno
PYTHONPATH=src python -m uvicorn AquaKeeper.web.main:app --reload
