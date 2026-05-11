#!/bin/sh
# Alertmanager 0.27+ removed {{ env }} support.
# Inject SLACK_WEBHOOK_URL from env into config at startup.
if [ -n "$SLACK_WEBHOOK_URL" ]; then
    sed -i "s|{{SLACK_WEBHOOK_URL}}|$SLACK_WEBHOOK_URL|g" \
        /etc/alertmanager/alertmanager.yml.tmpl > /etc/alertmanager/alertmanager.yml
else
    cp /etc/alertmanager/alertmanager.yml.tmpl /etc/alertmanager/alertmanager.yml
fi
exec /bin/alertmanager "$@"
