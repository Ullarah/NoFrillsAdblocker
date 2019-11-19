#!/bin/python

import argparse
import json
import os
import re
import subprocess
import sys
import time

from math import floor
from urllib import error, request


quiet = False
force = False
skip_hints = False
skip_unbound = False
unbound_dir = '/etc/unbound'
list_json = sys.path[0] + '/blocklist.json'
location = unbound_dir + '/unbound.conf.d/adblock/'
user_agent = 'NoFrillsAdblocker; github; pass'
root_hints_url = 'https://www.internic.net/domain/named.root'


def verbose(*message):
    if not quiet:
        print(' '.join(message))


def is_valid_hostname(hostname):
    if hostname.endswith("."):
        hostname = hostname[:-1]

    if len(hostname) > 253 or re.match(r"[\d.]+$", hostname):
        return False

    allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(x) for x in hostname.split("."))


def is_recent(list_id):
    filename = location + list_id + '.domain.conf'

    if os.path.isfile(filename):
        return floor(time.time() - os.path.getmtime(filename)) < 604800

    return False


def download_list(url):
    verbose(('\t:: URL Download: ' + url))

    req = request.Request(url)
    req.add_header('User-Agent', user_agent)

    contents = ''
    decode = True

    try:
        response = request.urlopen(req)
        contents = response.read()

    except error.URLError as e:
        decode = False
        if hasattr(e, 'reason'):
            verbose('\t:: Failed to reach a server')
            verbose('\t:: Reason:', e.reason)
        elif hasattr(e, 'code'):
            verbose('\t:: The server could not fulfill the request')
            verbose('\t:: Error:', e.code)
        else:
            verbose('\t:: Unknown Error')

    if decode:
        try:
            return contents.decode(encoding='UTF-8')
        except:
            return contents.decode(encoding='ISO-8859-1')


def process_list(list_id, contents):
    if contents is None:
        return None

    redirect = '0.0.0.0'
    filename = list_id + '.domain.conf'
    output = str(contents)

    verbose('\t:: Parsing domains')
    verbose('\t\t:: Stripping unnecessary sections')

    for o in ['::', '0.0.0.0', '127.0.0.1']:
        output = re.sub(o, '', output)

    list_output = output.split('\n')

    for c in ['#', ']', '[', ',']:
        list_output = [x for x in list_output if c not in x]

    list_output = list(map(str.strip, list_output))

    for p in ['0.0.0.0', '127.0.0.1', '255.255.255.255', '1', 'fe801%lo0']:
        list_output = [x for x in list_output if x != p]

    for i in range(999):
        list_output = [x for x in list_output if x != f"ff{i:03}"]

    verbose('\t\t:: Sorting domain list')

    list_output = [_f for _f in list_output if _f]
    list_output = list(set(list_output))

    list_output = list(filter(is_valid_hostname, list_output))
    list_output = sorted(list_output, key=str.lower)

    verbose('\t\t:: Parsed ' + str(len(list_output)) + ' domains')

    if len(list_output) < 1:
        verbose('\t\t:: 0 domains? Check URL for errors')

    try:
        with open(location + filename, 'w') as f:

            f.write('server:\n')

            for item in list_output:
                f.write('local-data: \"')
                f.write("%s" % item)
                f.write(' A ' + redirect + '\"')
                f.write('\n')

            f.close()

    except IOError as e:
        verbose('\t:: Error:', os.strerror(e.errno))

    return len(list_output)


def main():
    list_count = 0
    dl_count = 0

    if not skip_hints:
        verbose('\t:: Downloading recent root.hints...')
        subprocess.run(['wget', '-qO', '/var/lib/unbound/root.hints',
                                root_hints_url])

    if not os.path.isfile(list_json):
        verbose('\n\t:: Error: Blocklist file does not exist at:')
        exit('\t:: ' + list_json + '\n')

    for key, value in sorted(json.load(open(list_json)).items()):
        verbose(('\n' + key))

        if is_recent(value['id']) and not force:
            verbose('\t:: Skipping recent download')
            time.sleep(0.25)
        else:
            list_raw = download_list(value['url'])
            if list_raw is not None:
                list_processed = process_list(value['id'], list_raw)
                list_count += list_processed
                dl_count += 1

    if dl_count > 0:
        verbose('\nTotal blocklist size: ' + str(list_count) + '\n')

        if not skip_unbound:
            verbose('Checking configuration...')
            os.system('/usr/sbin/unbound-checkconf')

            verbose('\nRestarting \'unbound\' service...')
            os.system('systemctl restart unbound')
    else:
        verbose('\nNo changes...')

    if quiet:
        exit()
    else:
        exit('\n')


if __name__ == '__main__':

    a_parser = argparse.ArgumentParser(prog='adblock-update')

    a_parser.add_argument('-q', '--quiet',
                          action='store_true',
                          help='quiet output')

    a_parser.add_argument('-f', '--force',
                          action='store_true',
                          help='force blocklist download')

    a_parser.add_argument('-Sh', '--skip-hints',
                          action='store_true',
                          help='skip root.hints download')

    a_parser.add_argument('-Su', '--skip-unbound',
                          action='store_true',
                          help='skip unbound service update')

    a_parser.add_argument('-Au', '--alt-unbound',
                          action='store', type=str,
                          help='use alternative unbound directory')

    a_parser.add_argument('-Ab', '--alt-blocklist',
                          action='store', type=str,
                          help='use alternative blocklist json file')

    a_parser.add_argument('-Ah', '--alt-hints-url',
                          action='store', type=str,
                          help='use alternative root hints url')

    a_parser.add_argument('-u', '--user-agent',
                          action='store', type=str,
                          help='use a different user agent for downloads')

    args = a_parser.parse_args()

    quiet = args.quiet
    force = args.force
    skip_hints = args.skip_hints
    skip_unbound = args.skip_unbound

    if args.alt_unbound is not None:
        unbound_dir = args.alt_unbound

    if args.alt_blocklist is not None:
        list_json = args.alt_blocklist

    if args.alt_hints_url is not None:
        root_hints_url = args.alt_hints_url

    if args.user_agent is not None:
        user_agent = args.user_agent

    if not os.path.exists(unbound_dir):
        exit('\n\t:: Error: Requires unbound service to run\n')

    if os.geteuid() != 0:
        exit('\n\t:: Error: Requires root privileges to run\n')

    if not os.path.exists(location):
        os.makedirs(location)

    verbose('\nNo Frills Adblocker')
    main()
