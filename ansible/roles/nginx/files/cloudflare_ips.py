#! /usr/bin/env python3
from __future__ import print_function

import hashlib
import os
from itertools import chain
from sys import exit, stderr

import requests

try:
    response_ip4 = requests.get("https://www.cloudflare.com/ips-v4")
    response_ip4.raise_for_status()
except Exception as err:
    print("Could not reach IP4 list: {}".format(err), file=stderr)
    exit(1)

try:
    response_ip6 = requests.get("https://www.cloudflare.com/ips-v6")
    response_ip6.raise_for_status()
except Exception as err:
    print("Could not reach IP6 list: {}".format(err), file=stderr)
    exit(2)

result = ""
for line in chain(response_ip4.content.split("\n"), response_ip6.content.split("\n")):
    line = line.strip()
    if not line:
        continue
    result += "set_real_ip_from {};\n".format(line)
result += "real_ip_header CF-Connecting-IP;\n"
new_hasher = hashlib.md5()
new_hasher.update(result)
old_hasher = hashlib.md5()
with open("/etc/nginx/includes/real_ip.conf", "r") as f:
    old_hasher.update(f.read())
if new_hasher.hexdigest() == old_hasher.hexdigest():
    exit(0)
with open("/etc/nginx/includes/real_ip.conf", "w") as f:
    f.write(result)
    f.flush()
os.system("service nginx reload >/dev/null")
