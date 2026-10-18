# Odoo 19 + PostgreSQL (Docker Compose)

Ready-to-use local stack: Odoo **19.0** + PostgreSQL **16**.

## Requirements

- Docker Desktop (or Docker Engine + Compose v2)
- Free ports: `8069` (Odoo), `5432` (Postgres)

Shell scripts and `odoo.conf` must use **LF** line endings (not CRLF). A `.gitattributes` file enforces this; if you still see `$'\r': command not found` on Windows, run:

```bash
git add --renormalize .
git checkout -- docker-entrypoint.sh volumes/odoo/conf/odoo.conf
```

## Start

```bash
docker compose up -d
```

Odoo will be available at: [http://localhost:8069](http://localhost:8069)

On first launch:

1. Create a database (e.g. `odoo19` — **do not** name it `master`)
2. Master password (set in `volumes/odoo/conf/odoo.conf`): `admin`
3. Wait until logs show `Modules loaded` (can take several minutes on Windows)
4. Create the Odoo admin user via the setup wizard

If creation was interrupted, drop the incomplete database from `/web/database/manager` and create it again.

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

Clone or copy modules into `addons/`. That folder is bind-mounted; the container **must not** `chown` it, otherwise `git pull` inside a module fails with `cannot open '.git/FETCH_HEAD': Permission denied`.

If that already happened, restore host ownership **once**, then recreate Odoo:

```bash
sudo chown -R "$(id -u):$(id -g)" addons
docker compose up -d --force-recreate odoo
```

Then:

```bash
docker compose restart odoo
```

In Odoo: enable developer mode → Apps → Update Apps List.

Heavy official apps (especially **Accounting**) often time out in the browser on Windows/Docker. Logs then show `Broken pipe` / `connection to client lost`, and:

```text
Skipping database ... because of modules to install/upgrade/remove
```

Finish the install from the CLI instead (Odoo must be able to reach Postgres; do not close the terminal):

```bash
python install_module.py -d master account
```

If the module is already marked "to install/upgrade":

```bash
python install_module.py -d master account --upgrade
```

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

`relation "ir_module_module" does not exist` during **Create database** is usually the cron worker polling a DB that is still initializing. Wait for `Loading module base` then `Modules loaded`. Cron is disabled by default (`max_cron_threads = 0`) to avoid that race.

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
