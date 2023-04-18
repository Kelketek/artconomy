#!/usr/bin/python3
#   WANT_JSON
import json
import os
import subprocess
import sys

changed = True

# read the argument string from the arguments file
args_file = sys.argv[1]
args_data = open(args_file).read()

args = json.loads(args_data)

os.chdir(args['directory'])
current_hash = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).strip().decode('utf-8')
old_hash_file = args['hash_file']


if os.path.isfile(old_hash_file):
    old_hash = open(old_hash_file).read().strip()
    if old_hash == current_hash:
        changed = False

print(json.dumps({'changed': changed, 'digest': current_hash}))
