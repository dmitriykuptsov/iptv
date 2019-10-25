#!/bin/bash
echo "Usage: "
echo "$0 <sql user> <sql password>"
SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
# Force clock update
echo "Stopping services..."
service iptv-backend stop
service iptv-capturing stop
echo "Updating clock..."
ntpdate -u 0.ubuntu.pool.ntp.org
cd $SCRIPTPATH
echo "Making directories..."
rm -rf /var/streaming/*
mkdir -p /opt/iptv/capturing/
mkdir -p /opt/iptv/crontasks/
mkdir -p /opt/iptv/service/
echo "Creating database..."
mysql -u $1 -p$2 < ../service/database/schema.sql
echo "Copying files..."
rsync -rv ../capturing/* /opt/iptv/capturing/
rsync -rv ../crontasks/* /opt/iptv/crontasks/
rsync -rv ../service/backend/* /opt/iptv/service/
rsync -rv ../service/frontend/* /var/www/html/
rsync -rv ../streaming/defualt /etc/nginx/sites-enabled/
rsync -rv ../startup/systemd/* /etc/systemd/system/
rsync -rv ../security/iptables /etc/iptables/rules.v4
echo "Reloading daemon..."
systemctl daemon-reload
echo "0	0	*	*	*	root	cd /opt/iptv/crontasks && python crawl_and_parse_schedule.py localhost root root streamtv" >> /etc/crontab
echo "0	0	*	*	*	root	cd /opt/iptv/crontasks && bash update_clock.sh" >> /etc/crontab
echo "Starting services..."
service cron restart
service nginx restart
service iptv-backend restart
service iptv-capturing restart
echo "Enabling services..."
systemctl enable iptv-capturing.service
systemctl enable iptv-backend.service
