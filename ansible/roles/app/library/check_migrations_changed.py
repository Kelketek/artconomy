#!/usr/bin/python3
#   WANT_JSON
import glob
import hashlib
import json
import os
import sys

changed = True


def hash_migration(dir_name, hasher):
    files = sorted(glob.glob(os.path.join(dir_name, '*.py')))
    hasher.update(str(files).encode('utf-8'))


def explore_path(dir_name, hasher):
    # Preserve ordering.
    files = sorted(os.listdir(dir_name))
    for f in files:
        path = os.path.join(dir_name, f)
        if os.path.isdir(path):
            migrations_path = os.path.join(path, 'migrations')
            if os.path.isdir(migrations_path):
                hash_migration(migrations_path, hasher)
    hasher.update(args.get('tilt', '0').encode('utf-8'))
    return hasher.hexdigest()


# read the argument string from the arguments file
args_file = sys.argv[1]
args_data = open(args_file).read()

args = json.loads(args_data)

os.chdir(args['directory'])
current_hash = explore_path(args['directory'], hasher=hashlib.sha1())
old_hash_file = args['hash_file']


if os.path.isfile(old_hash_file):
    old_hash = open(old_hash_file).read().strip()
    if old_hash == current_hash:
        changed = False

print(json.dumps({'changed': changed, 'digest': current_hash}))
