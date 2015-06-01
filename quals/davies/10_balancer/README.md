Compile
=======

gcc -lcrypto daemon.c -O3 -o /opt/daemon1

Upstart
=======

/etc/systemd/system/balancer1.service

    [Unit]
    Description=Balancer task First
    After=network.target
    
    [Service]
    ExecStart=/opt/daemon1
    Restart=always
    RestartSec=0
    [Install]
    WantedBy=multi-user.target



    systemctl enable balancer1.service
    systemctl daemon-reload
    systemctl restart balancer1.service
