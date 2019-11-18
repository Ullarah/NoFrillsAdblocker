#!/bin/python

import json
import os
import re

from urllib import error, request


location = '/etc/unbound/unbound.conf.d/adblock/'


def is_valid_hostname(hostname):
    if hostname.endswith("."):
        hostname = hostname[:-1]

    if len(hostname) > 253:
        return False

    if re.match(r"[\d.]+$", hostname):
        return False

    allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(x) for x in hostname.split("."))


def download_list(url):
    print(('\t:: URL Download: ' + url))

    req = request.Request(url)
    req.add_header('User-Agent', 'NoFrillsAdblocker; github; pass')

    contents = ''
    decode = True

    try:
        response = request.urlopen(req)
        contents = response.read()

    except error.URLError as e:
        decode = False
        if hasattr(e, 'reason'):
            print('\t:: Failed to reach a server')
            print('\t:: Reason:', e.reason, '\n')
        elif hasattr(e, 'code'):
            print('\t:: The server could not fulfill the request')
            print('\t:: Error:', e.code, '\n')
        else:
            print('\t:: Unknown Error\n')

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

    print('\t:: Parsing domains')
    print('\t\t:: Stripping unnecessary sections')

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

    print('\t\t:: Sorting domain list')

    list_output = [_f for _f in list_output if _f]
    list_output = list(set(list_output))

    list_output = list(filter(is_valid_hostname, list_output))
    list_output = sorted(list_output, key=str.lower)

    print('\t\t:: Parsed ' + str(len(list_output)) + ' domains')

    if len(list_output) < 1:
        print('\t\t:: 0 domains? Check configuration')

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
        print('\t:: Error:', os.strerror(e.errno))

    return len(list_output)


def main():
    list_count = 0

    for key, value in sorted(json.load(open('blocklist.json')).items()):
        print(('\n' + key))
        list_raw = download_list(value['url'])

        if list_raw is not None:
            list_processed = process_list(value['id'], list_raw)
            list_count += list_processed

    print('Total blocklist size: ' + str(list_count) + '\n')

    print('Checking configuration...')
    os.system('/usr/sbin/unbound-checkconf')

    print('\nRestarting \'unbound\' service...')
    os.system('systemctl restart unbound')

    exit('\n')


if __name__ == '__main__':
    if not os.path.isfile('/usr/sbin/unbound-checkconf'):
        exit('\n\t:: Error: Requires unbound service to run\n')

    if os.geteuid() != 0:
        exit('\n\t:: Error: Requires root privileges to run\n')

    if not os.path.exists(location):
        os.makedirs(location)

    main()
