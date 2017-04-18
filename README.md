druid-redhat7-rpm
---------
A set of scripts to package [Druid](http://druid.io) into an rpm.
Requires CentOS/RedHat 7.

Setup
-----
    sudo yum install make rpmdevtools

Building
--------
    make rpm

Resulting RPM will be avaliable at $(shell pwd)/noarch

Installing and operating
------------------------
    sudo yum install druid*.rpm
    sudo systemctl start <service>
    sudo systemctl enable <service>

The following services are available:
* druid-broker
* druid-coordinator
* druid-historical
* druid-manager
* druid-overlord


Default locations
-----------------
binaries: /opt/druid  
data:     /var/lib/druid  
logs:     /var/log/druid  
configs:  /etc/druid, /etc/sysconfig/druid  
