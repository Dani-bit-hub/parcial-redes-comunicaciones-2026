# Parcial 2 práctico: despliegue multi-contenedor y análisis OSI

Comunicaciones - Ingeniería Mecatrónica, Universidad Militar Nueva Granada.

## Accesos (sin usuario ni contraseña)

| Servicio | URL |
|---|---|
| Página de inicio con botones | http://localhost/inicio |
| Dashboard de Grafana | http://localhost/grafana |
| Cuaderno de Jupyter | http://localhost/jupyter |
| Portal Joomla | http://localhost |

## Arranque

```bash
git clone https://github.com/Dani-bit-hub/parcial-redes-comunicaciones-2026.git
cd parcial-redes-comunicaciones-2026
cp .env.example .env
docker compose up -d
```

-Es necesario tener el docker instalado y abierto para que se creen los 
respectivos contenedores correctamente.
-La primera vez descarga imágenes y construye la de Jupyter (varios minutos).
Después, Joomla se auto-instala sobre PostgreSQL y el cuaderno se ejecuta solo
(unos 3 a 5 minutos en total). Estado: `docker compose ps` (los 5 en `healthy`).

## Servicios

| Contenedor | Imagen | Función | Redes |
|---|---|---|---|
| nginx | nginx:alpine | Proxy inverso, único puerto publicado (80:80) | frontend_net |
| joomla | joomla:latest | CMS sobre PostgreSQL | frontend_net, backend_net |
| database | postgres:16-alpine | PostgreSQL, sin acceso externo | backend_net |
| jupyter | build local sobre quay.io/jupyter/base-notebook | Cuaderno precargado e ingesta de logs | frontend_net, backend_net |
| grafana | grafana/grafana:latest | Dashboard provisionado automáticamente | frontend_net, backend_net |

## Qué ocurre solo al arrancar

- **Grafana:** datasource PostgreSQL y dashboard "Tráfico Joomla" (4 paneles) cargados desde `grafana/provisioning/`. Acceso anónimo de solo lectura.
- **Jupyter:** sin token. `/jupyter` abre `work/analisis_datos.ipynb`, ya ejecutado.
- **Logs:** nginx escribe `access_json.log`; un proceso en Jupyter lo carga en la tabla `access_logs` de PostgreSQL, que consultan Grafana y el cuaderno.
- **Tráfico de calentamiento:** un script genera peticiones para que las gráficas tengan datos desde el primer minuto.

## Estructura

```
├── docker-compose.yml
├── .env.example
├── INFORME.md          # documento técnico y análisis OSI
├── nginx/              # default.conf y página /inicio
├── jupyter/            # Dockerfile, notebooks/, init/, scripts/
├── grafana/provisioning/
└── tools/              # scripts que generaron el cuaderno y el dashboard
```

## Detener y limpiar

```bash
docker compose down        # detiene
docker compose down -v     # detiene y borra datos (reinstala Joomla)
```

Documentación técnica completa: [INFORME.md](INFORME.md)
