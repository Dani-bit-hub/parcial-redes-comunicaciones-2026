import os, re, time
from datetime import datetime
import psycopg2

LOG = "/var/log/joomla/joomla_access.log"
DSN = dict(
    host="database",
    port=5432,
    dbname=os.environ["POSTGRES_DB"],
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
)

DDL = """
CREATE TABLE IF NOT EXISTS apache_logs (
    id          BIGSERIAL PRIMARY KEY,
    time        TIMESTAMPTZ NOT NULL,
    remote_addr TEXT,
    method      TEXT,
    uri         TEXT,
    status      INTEGER,
    bytes       BIGINT,
    referer     TEXT,
    user_agent  TEXT
);
CREATE INDEX IF NOT EXISTS idx_apache_logs_time ON apache_logs (time);
"""

# Formato: XFF %l %u [fecha] "METODO URI PROTO" status bytes "referer" "user-agent"
PATRON = re.compile(
    r'^(\S+) \S+ \S+ \[([^\]]+)\] "(\S+) (\S+)[^"]*" (\d{3}) (\S+) "([^"]*)" "([^"]*)"$'
)


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
    print("Tabla apache_logs lista", flush=True)

    while not os.path.exists(LOG):
        time.sleep(2)

    with open(LOG, "r") as f:
        while True:
            line = f.readline()
            if not line:
                time.sleep(1)
                continue
            m = PATRON.match(line.strip())
            if not m:
                print("Línea ignorada:", line.strip(), flush=True)
                continue
            ip, fecha, metodo, uri, status, nbytes, ref, ua = m.groups()
            ip = None if ip == "-" else ip.split(",")[0].strip()
            nbytes = 0 if nbytes == "-" else int(nbytes)
            try:
                ts = datetime.strptime(fecha, "%d/%b/%Y:%H:%M:%S %z")
                with conn.cursor() as cur:
                    cur.execute(
                        """INSERT INTO apache_logs
                           (time, remote_addr, method, uri, status, bytes, referer, user_agent)
                           VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
                        (ts, ip, metodo, uri, int(status), nbytes,
                         None if ref == "-" else ref, ua),
                    )
            except psycopg2.Error as e:
                print("Error de BD, reconectando:", e, flush=True)
                conn = connect()
            except Exception as e:
                print("Línea ignorada:", e, flush=True)


if __name__ == "__main__":
    main()