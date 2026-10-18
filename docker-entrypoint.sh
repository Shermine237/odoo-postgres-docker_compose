#!/bin/bash
# Fix ownership on Odoo data/log volumes, then hand off to the official entrypoint.
# Do not chown /mnt/extra-addons: cloned module .git dirs must stay owned by the host user.
set -e

mkdir -p /var/log/odoo /var/lib/odoo /mnt/extra-addons
chown -R odoo:odoo /var/log/odoo /var/lib/odoo
chmod a+rX /mnt/extra-addons

exec /entrypoint.sh "$@"
