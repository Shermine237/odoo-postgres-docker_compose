#!/bin/bash
set -e

mkdir -p /var/log/odoo /var/lib/odoo
chown -R odoo:odoo /var/log/odoo /var/lib/odoo

exec /entrypoint.sh "$@"
