import json

def md(t): return {"cell_type": "markdown", "metadata": {}, "source": t.splitlines(True)}
def code(t): return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": t.splitlines(True)}

cells = [
    md("# Análisis de tráfico web\nConsulta la tabla `access_logs` de PostgreSQL, alimentada con los logs de nginx."),
    code("import os\nimport pandas as pd\nimport matplotlib.pyplot as plt\nfrom sqlalchemy import create_engine\n\n"
         "url = f\"postgresql+psycopg2://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}@database:5432/{os.environ['POSTGRES_DB']}\"\n"
         "engine = create_engine(url)\n"
         "df = pd.read_sql('SELECT * FROM access_logs', engine)\n"
         "print(f'{len(df)} peticiones cargadas')\ndf.head()"),
    md("## Peticiones por código HTTP"),
    code("df['status'].value_counts().sort_index().plot(kind='bar', title='Peticiones por código HTTP')\n"
         "plt.xlabel('Código'); plt.ylabel('Peticiones'); plt.show()"),
    md("## Peticiones por servicio"),
    code("df['service'].value_counts().plot(kind='pie', autopct='%1.0f%%', title='Peticiones por servicio')\n"
         "plt.ylabel(''); plt.show()"),
    md("## IPs más recurrentes"),
    code("df['remote_addr'].value_counts().head(10)"),
    md("## Peticiones por minuto"),
    code("df['time'] = pd.to_datetime(df['time'])\n"
         "df.set_index('time').resample('1min').size().plot(title='Peticiones por minuto')\nplt.show()"),
]

nb = {
    "cells": cells,
    "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                 "language_info": {"name": "python"}},
    "nbformat": 4, "nbformat_minor": 5,
}

with open("jupyter/notebooks/analisis_datos.ipynb", "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)
print("Notebook creado")