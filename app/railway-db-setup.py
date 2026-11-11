"""Railway helper: wait for services, migrate as schema owner, provision the restricted runtime role."""
import os, socket, subprocess, sys, time
from urllib.parse import urlsplit

from sqlalchemy import create_engine, text


def wait_tcp(url, default_port, label, tries=150):
    if not url:
        return
    u = urlsplit(url)
    for _ in range(tries):
        try:
            socket.create_connection((u.hostname, u.port or default_port), timeout=3).close()
            return
        except OSError:
            time.sleep(2)
    sys.exit(f'[railway] {label} not reachable at {u.hostname}')


def main(mode):
    runtime = os.environ['DATABASE_URL']
    wait_tcp(runtime, 5432, 'postgres')
    wait_tcp(os.getenv('REDIS_URL', ''), 6379, 'redis')
    if mode == 'migrate':
        owner = os.environ['ALEMBIC_DATABASE_URL']
        for attempt in range(30):  # Postgres accepts TCP slightly before it accepts logins on first init
            try:
                create_engine(owner).connect().close()
                break
            except Exception:
                time.sleep(2)
        print('[railway] applying migrations', flush=True)
        subprocess.run([sys.executable, 'scripts/migrate.py'], check=True, env=os.environ.copy())
        user = os.environ.get('ARGUS_RUNTIME_DB_USER', 'argus_runtime')
        pw = urlsplit(runtime).password or ''
        eng = create_engine(owner, isolation_level='AUTOCOMMIT')
        with eng.connect() as c:
            db = c.execute(text('select current_database()')).scalar()
            q = c.dialect.identifier_preparer.quote
            lit = pw.replace("'", "''")
            exists = c.execute(text('select 1 from pg_roles where rolname=:u'), {'u': user}).scalar()
            verb = 'ALTER' if exists else 'CREATE'
            c.exec_driver_sql(f"{verb} ROLE {q(user)} LOGIN NOINHERIT NOSUPERUSER NOBYPASSRLS PASSWORD '{lit}'")
            for stmt in (
                f'GRANT CONNECT ON DATABASE {q(db)} TO {q(user)}',
                f'GRANT USAGE ON SCHEMA public TO {q(user)}',
                f'GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO {q(user)}',
                f'GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA public TO {q(user)}',
                f'GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO {q(user)}',
                f'ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO {q(user)}',
                f'ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT, UPDATE ON SEQUENCES TO {q(user)}',
            ):
                c.exec_driver_sql(stmt)
        print(f'[railway] runtime role {user} ready', flush=True)
    else:
        for _ in range(180):
            try:
                with create_engine(runtime).connect() as c:
                    c.execute(text('select count(*) from tenants')).scalar()
                return
            except Exception:
                time.sleep(3)
        sys.exit('[railway] schema not ready (is the api service running?)')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'migrate')
