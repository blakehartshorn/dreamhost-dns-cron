# dreamhost-dns-cron

This is a simple script that can be run as a cron to update A/AAAA records at Dreamhost with your system's public IP addresses.

## Requirements
* [requests](https://requests.readthedocs.io/en/latest/)
* [PyYAML](https://pyyaml.org/)

## Usage
```
usage: dreamhost-dns-cron.py [-h] [-c FILENAME] [-l FILENAME]

Dynamically update DNS record at Dreamhost.

options:
  -h, --help   show this help message and exit
  -c FILENAME  Configuration file.
  -l FILENAME  Log file.
```
Rename `dreamhost-dns-cron.yaml-example` to `dreamhost-dns-cron.yaml` and fill it out accordingly. It supports multiple domain records as well as IPv6.

A cron running every 15 minutes could look like this,
```
*/15 * * * *  /opt/dreamhost-dns-cron/dreamhost-dns-cron.py -c /opt/dreamhost-dns-cron/dreamhost-dns-cron.yaml -l /opt/dreamhost-dns-cron/dreamhost-dns-cron.log
```

This will not attempt to create a record that does not already exist. It will check Dreamhost's API for the IP address associated with the record you've included in the configuration, and delete/create the record if your IP address has changed. It does this by querying https://v4.ident.me/ and https://v6.ident.me/ for your public addresses. If the record at Dreamhost matches, it quits.

Some other scripts like this already existed, but I wanted one that would work on multiple records and had IPv6 support.