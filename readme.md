# Odoo 18 + PostgreSQL (Docker Compose)

Ready-to-use local stack: Odoo **18.0** + PostgreSQL **16**.

## Requirements

- Docker Desktop (or Docker Engine + Compose v2)
- Free ports: `8069` (Odoo), `5432` (Postgres)

## Start

```bash
docker compose up -d
```

Odoo will be available at: [http://localhost:8069](http://localhost:8069)

On first launch:

1. Create a database (e.g. `odoo18`)
2. Master password (set in `volumes/odoo/conf/odoo.conf`): `admin`
3. Create the Odoo admin user via the setup wizard

## Stop / restart

```bash
docker compose stop
docker compose start
docker compose down          # stops containers; bind-mounted folders stay
docker compose down -v       # note: does not wipe ./volumes bind mounts
```

## Layout

```
.
├── docker-compose.yml
├── docker-entrypoint.sh         # fixes volume permissions, then starts Odoo
├── reset_volumes.py             # wipe runtime data (fresh install)
├── addons/                      # custom modules → /mnt/extra-addons
├── logs/                        # Odoo logs (optional file logging)
└── volumes/
    ├── odoo/
    │   ├── conf/odoo.conf       # Odoo configuration
    │   └── web-data/            # filestore / sessions
    └── postgres-data/           # PostgreSQL data
```

## Custom modules

Put your modules in `addons/`, then:

```bash
docker compose restart odoo
```

In Odoo: enable developer mode → Apps → Update Apps List.

Configured in `odoo.conf`:

```ini
addons_path = /usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons
```

## Credentials (local dev)

| Service     | User | Password |
|-------------|------|----------|
| PostgreSQL  | odoo | odoo     |
| Odoo master | —    | admin    |

**Change `admin_passwd` and DB passwords before any non-local use.**

## Logs

Odoo logs go to stdout by default (visible with Compose):

```bash
docker compose logs -f odoo
docker compose logs -f db
```

The message `Can't find .pfb for face 'Courier'` is harmless (PDF font).

When Odoo is ready, you should see a line like `HTTP service (werkzeug) running on ...8069`.
Then open http://localhost:8069

To log to a file instead, uncomment `logfile` in `odoo.conf`.

## Full data reset

Resets to a fresh install (wipes DB + filestore + logs, keeps `odoo.conf` and `addons/`).
The script **does not** restart the stack.

```bash
python reset_volumes.py
# or without confirmation:
python reset_volumes.py -y
```

On Linux, if directories are owned by root:

```bash
sudo python3 reset_volumes.py -y
```

Then, when you want to start again:

```bash
docker compose up -d
```
