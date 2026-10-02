import json, os, time
import psycopg2

LOG = "/var/log/nginx/access_json.log"
DSN = dict(
    host="database",
    port=5432,
    dbname=os.environ["POSTGRES_DB"],
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
)

DDL = """
CREATE TABLE IF NOT EXISTS access_logs (
    id           BIGSERIAL PRIMARY KEY,
    time         TIMESTAMPTZ NOT NULL,
    remote_addr  TEXT,
    method       TEXT,
    uri          TEXT,
    status       INTEGER,
    bytes        BIGINT,
    request_time DOUBLE PRECISION,
    referer      TEXT,
    user_agent   TEXT,
    service      TEXT
);
CREATE INDEX IF NOT EXISTS idx_access_logs_time ON access_logs (time);
"""

def connect():
    while True:
        try:
            conn = psycopg2.connect(**DSN)
            conn.autocommit = True
            return conn
        except Exception as e:
            print("Esperando a PostgreSQL:", e, flush=True)
            time.sleep(3)

def main():
    conn = connect()
    with conn.cursor() as cur:
        cur.execute(DDL)
    print("Tabla access_logs lista", flush=True)

    while not os.path.exists(LOG):
        time.sleep(2)

    with open(LOG, "r") as f:
        while True:
            line = f.readline()
            if not line:
                time.sleep(1)
                continue
            try:
                d = json.loads(line)
                with conn.cursor() as cur:
                    cur.execute(
                        """INSERT INTO access_logs
                           (time, remote_addr, method, uri, status, bytes,
                            request_time, referer, user_agent, service)
                           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                        (d["time"], d["remote_addr"], d["method"], d["uri"],
                         d["status"], d["bytes"], d["request_time"],
                         d["referer"], d["user_agent"], d["service"]),
                    )
            except psycopg2.Error as e:
                print("Error de BD, reconectando:", e, flush=True)
                conn = connect()
            except Exception as e:
                print("Línea ignorada:", e, flush=True)

if __name__ == "__main__":
    main()