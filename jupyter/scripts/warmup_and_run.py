import subprocess
import time
import urllib.error
import urllib.request

BASE = "http://nginx"
NOTEBOOK = "/home/jovyan/work/analisis_datos.ipynb"


def get(path):
    try:
        with urllib.request.urlopen(BASE + path, timeout=15) as r:
            r.read()
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return None


# 1. Esperar a que Joomla termine de auto-instalarse (máx. ~5 min)
for _ in range(100):
    if get("/") == 200:
        break
    time.sleep(3)

# 2. Tráfico de calentamiento: 200, 404 y los otros servicios
rutas = ["/", "/index.php", "/administrator/", "/no-existe", "/otra-pagina",
         "/grafana/login", "/jupyter/api"]
for _ in range(6):
    for r in rutas:
        get(r)

# 3. Dar tiempo a que la ingesta inserte los logs en PostgreSQL
time.sleep(15)

# 4. Ejecutar el cuaderno y guardar las salidas en el mismo archivo
for intento in range(4):
    res = subprocess.run(
        ["jupyter", "nbconvert", "--to", "notebook", "--execute", "--inplace",
         "--ExecutePreprocessor.timeout=180", NOTEBOOK],
        capture_output=True, text=True,
    )
    print(res.stdout, res.stderr, flush=True)
    if res.returncode == 0:
        print("Cuaderno ejecutado", flush=True)
        break
    time.sleep(20)