#!/usr/bin/python3

import requests, yaml, argparse, logging

parser = argparse.ArgumentParser(description="Dynamically update DNS record at Dreamhost.")
parser.add_argument("-c", metavar="FILENAME", help="Configuration file.", default="dreamhost-dns-cron.yaml")
parser.add_argument("-l", metavar="FILENAME", help="Log file.", default="dreamhost-dns-cron.log")
args = parser.parse_args()

logging.basicConfig(filename=args.l, level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

try:
    with open(args.c) as f:
        config = yaml.safe_load(f.read())
except Exception as e:
    logging.error("Could not open config file", exc_info=True)


def find_record(records, domain, d_type):
    for record in records:
        if record['record'] == domain['record'] and record['type'] == d_type:
            if record['editable'] == '1':
                return(record)
            else:
                logging.error(f"{record['record']} not editable!")
                exit(1)
    return(False)

def update_record(record, ip_address):
    payload = record
    payload['key'] = config['api_key']
    payload['format'] = 'json'

    if ip_address == record['value']:
        logging.info(f"{record['type']} record for {record['record']} already points to {ip_address}")
        return False
    else:
        try:
            payload['cmd'] = 'dns-remove_record'
            logging.info(f"Deleting old record for {record['record']}...")
            r = requests.get("https://api.dreamhost.com/", params=payload)
            if r.status_code == 200:
                logging.info("Deleted record.")
            else:
                logging.error(f"Could not delete record. Caught status code {r.status_code}")
                exit(1)
        except Exception as e:
                logging.error(f"Could not delete record.", exc_info=True)
                exit(1)
        try:
            payload['cmd'] = 'dns-add_record'
            payload['value'] = ip_address
            logging.info(f"Adding new record for {record['record']}...")
            r = requests.get("https://api.dreamhost.com/", params=payload)
            if r.status_code == 200:
                logging.info("Added record.")
            else:
                logging.error(f"Could not add record. Caught status code {r.status_code}")
                exit(1)
        except Exception as e:
                logging.error(f"Could not add record.", exc_info=True)
                exit(1) 

if not (config['ipv4'] and config['ipv6']):
    logging.warning("You said no to both types of IP address!")
    exit(1)

if config['ipv4']:
    try:
        r = requests.get("https://v4.ident.me/")
        if r.status_code == 200:
            ipv4 = r.text
            logging.info(f"Found IPv4 address {ipv4}")
        else:
            logging.error(f"Could not get IPv4 address. Caught status code {r.status_code}")
            exit(1)
    except Exception as e:
        logging.error(f"Could not get IPv4 address", exc_info=True)
        exit(1)
else:
    ipv4 = False

if config['ipv6']:
    try:
        r = requests.get("https://v6.ident.me/")
        if r.status_code == 200:
            ipv6 = r.text
            logging.info(f"Found IPv6 address {ipv6}")
        else:
            logging.error(f"Could not get IPv6 address. Caught status code {r.status_code}")
            exit(1)
    except Exception as e:
        logging.error(f"Could not get IPv6 address.", exc_info=True)
        exit(1)
else:
    ipv6 = False

logging.info("Getting DNS records from Dreamhost...")
try:
    payload = {
        'key': config['api_key'],
        'cmd': 'dns-list_records',
        'format': 'json',
    }
    r = requests.get("https://api.dreamhost.com/", params=payload)
    if r.status_code == 200:
        records = r.json()['data']
    else:
        logging.error(f"Got status code {r.status_code} trying to fetch records.")
        exit(1)
except Exception as e:
    logging.error(f"Could not fetch record data", exc_info=True)
    exit(1)

for domain in config['domains']:
    if domain['a'] and ipv4:
        a_record = find_record(records, domain, "A")
        if a_record:
            update_record(a_record, ipv4)
    if domain['aaaa'] and ipv6:
        aaaa_record = find_record(records, domain, "AAAA")
        if aaaa_record:
            update_record(aaaa_record, ipv6)
