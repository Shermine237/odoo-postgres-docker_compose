#!/bin/bash
# Fix ownership on bind-mounted volumes, then hand off to the official Odoo entrypoint.
set -e

mkdir -p /var/log/odoo /var/lib/odoo /mnt/extra-addons
chown -R odoo:odoo /var/log/odoo /var/lib/odoo /mnt/extra-addons

exec /entrypoint.sh "$@"
