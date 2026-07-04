#!/bin/bash
set -e
cd $(dirname $0)
cd ..
appdir=$(pwd)
appname=$(basename $appdir)

mkdir -p $HOME/var/systemd-unit-files
cd $HOME/var/systemd-unit-files

cat <<EOF > $appname-django.service
[Unit]
Description=Django service for $appname
After=postgresql.service rabbitmq-server.service
BindsTo=postgresql.service rabbitmq-server.service

[Service]
WorkingDirectory=$appdir/back-end
ExecStart=$appdir/utils/uwsgi.sh
User=$(whoami)
Group=$(whoami)
Restart=on-failure
KillSignal=SIGQUIT
Type=notify
NotifyAccess=all

[Install]
WantedBy=multi-user.target

EOF

cat <<EOF > $appname-celery.service
[Unit]
Description=Celery Service for $appname
After=postgresql.service rabbitmq-server.service
BindsTo=postgresql.service rabbitmq-server.service

[Service]
Type=simple
User=$(whoami)
Group=$(whoami)
WorkingDirectory=$appdir/back-end
ExecStart=$appdir/utils/celery.sh
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

cat <<EOF > $appname-minion.service
[Unit]
Description=$appname Amuse Compiler workers
BindsTo=postgresql.service
After=postgresql.service

[Service]
Type=simple
User=$(whoami)
Group=$(whoami)
WorkingDirectory=$appdir/amusecompile
ExecStart=$appdir/amusecompile/script/amusecompile minion worker -m production -j 1
KillMode=process
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

cat <<EOF > $appname-amc.service
[Unit]
Description=$appname Amuse Compiler
BindsTo=postgresql.service
After=postgresql.service

[Service]
Type=forking
User=$(whoami)
Group=$(whoami)
WorkingDirectory=$appdir/amusecompile
PIDFile=$appdir/amusecompile/script/hypnotoad.pid
ExecStart=/usr/bin/hypnotoad  $appdir/amusecompile/script/amusecompile
ExecReload=/usr/bin/hypnotoad  $appdir/amusecompile/script/amusecompile
KillMode=process
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

cat <<EOF> $appname-cron.service
[Unit]
Description=$appname Cron wrapper

[Service]
Type=oneshot
User=$(whoami)
Group=$(whoami)
WorkingDirectory=$appdir
ExecStart=$appdir/utils/cron.sh
EOF

cat <<EOF> $appname-cron.timer
[Unit]
Description=Run the $appname cron wrapper

[Timer]
OnBootSec=10min
OnUnitInactiveSec=30min
Persistent=true
EOF


echo "Please install the files in $(pwd) into /etc/systemd/system and start/enable them"

