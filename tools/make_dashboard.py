import json

DS = {"type": "grafana-postgresql-datasource", "uid": "postgres-logs"}

def panel(pid, title, ptype, x, y, w, h, sql, fmt="table", extra=None):
    p = {
        "id": pid, "title": title, "type": ptype,
        "datasource": DS,
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "targets": [{
            "datasource": DS, "refId": "A", "format": fmt,
            "rawQuery": True, "editorMode": "code", "rawSql": sql,
        }],
        "fieldConfig": {"defaults": {}, "overrides": []},
        "options": {},
    }
    if extra:
        p.update(extra)
    return p

panels = [
    panel(1, "Peticiones por minuto (Joomla)", "timeseries", 0, 0, 12, 8,
          "SELECT date_trunc('minute', time) AS time, count(*) AS peticiones "
          "FROM access_logs WHERE service='joomla' AND $__timeFilter(time) "
          "GROUP BY 1 ORDER BY 1", fmt="time_series"),
    panel(2, "Peticiones por código HTTP", "barchart", 12, 0, 12, 8,
          "SELECT status::text AS codigo, count(*) AS peticiones "
          "FROM access_logs WHERE $__timeFilter(time) GROUP BY 1 ORDER BY 1",
          extra={"options": {"xField": "codigo", "legend": {"showLegend": False}}}),
    panel(3, "IPs más recurrentes", "table", 0, 8, 12, 8,
          "SELECT remote_addr AS ip, count(*) AS peticiones "
          "FROM access_logs WHERE $__timeFilter(time) "
          "GROUP BY 1 ORDER BY 2 DESC LIMIT 10"),
    panel(4, "Peticiones por servicio", "piechart", 12, 8, 12, 8,
          "SELECT service AS servicio, count(*) AS peticiones "
          "FROM access_logs WHERE $__timeFilter(time) GROUP BY 1",
                    extra={"options": {"pieType": "pie", "legend": {"displayMode": "list"},
                             "reduceOptions": {"values": True, "calcs": [], "fields": ""}}}),
]

dash = {
    "uid": "joomla-traffic",
    "title": "Tráfico Joomla",
    "tags": ["joomla", "nginx"],
    "timezone": "browser",
    "schemaVersion": 39,
    "version": 1,
    "refresh": "10s",
    "time": {"from": "now-6h", "to": "now"},
    "panels": panels,
}

with open("grafana/provisioning/dashboards/joomla_logs.json", "w", encoding="utf-8") as f:
    json.dump(dash, f, indent=2, ensure_ascii=False)
print("Dashboard creado")