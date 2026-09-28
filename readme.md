# Odoo 18 + PostgreSQL (Docker Compose)

Stack locale prête à l'emploi : Odoo **18.0** + PostgreSQL **16**.

## Prérequis

- Docker Desktop (ou Docker Engine + Compose v2)
- Ports libres : `8069` (Odoo), `5432` (Postgres)

## Démarrage

```bash
docker compose up -d
```

Odoo sera disponible sur : [http://localhost:8069](http://localhost:8069)

Au premier lancement :

1. Crée une base (ex. `odoo18`)
2. Mot de passe master (défini dans `volumes/odoo/conf/odoo.conf`) : `admin`
3. Crée l'utilisateur admin Odoo via l'assistant

## Arrêt / redémarrage

```bash
docker compose stop
docker compose start
docker compose down          # stoppe sans supprimer les volumes bind
docker compose down -v       # attention : n'efface pas les dossiers ./volumes bind
```

## Structure

```
.
├── docker-compose.yml
├── addons/                      # modules custom → /mnt/extra-addons
├── logs/                        # logs Odoo
└── volumes/
    ├── odoo/
    │   ├── conf/odoo.conf       # configuration Odoo
    │   └── web-data/            # filestore / sessions
    └── postgres-data/           # données PostgreSQL
```

## Modules custom

Place tes modules dans `addons/`, puis :

```bash
docker compose restart odoo
```

Dans Odoo : active le mode développeur → Apps → Update Apps List.

Le chemin est déjà configuré dans `odoo.conf` :

```ini
addons_path = /mnt/extra-addons
```

## Identifiants (dev local)

| Service    | User | Password |
|------------|------|----------|
| PostgreSQL | odoo | odoo     |
| Master Odoo| —    | admin    |

**Change `admin_passwd` et les mots de passe DB avant tout usage hors local.**

## Logs

```bash
docker compose logs -f odoo
docker compose logs -f db
# ou fichier :
# logs/odoo-server.log
```

## Reset complet (données)

Comme une nouvelle installation (efface DB + filestore + logs, garde `odoo.conf` et `addons/`).
Le script **ne relance pas** la stack.

```bash
python reset_volumes.py
# ou sans confirmation :
python reset_volumes.py -y
```

Sous Linux si les dossiers appartiennent à root :

```bash
sudo python3 reset_volumes.py -y
```

Puis, quand tu veux :

```bash
docker compose up -d
```
