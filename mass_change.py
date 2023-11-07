import os
import re
import sys

with open(sys.argv[1]) as input_file:
    lines = input_file.readlines()

has_import = False
last_import_line = None
script_close_tag_line = None
extension_name = ""
class_line = ""
class_line_index = None
mixin_names = ""
mixin_line = ""
mixin_line_index = None

for index, line in enumerate(lines):
    if not has_import:
        has_import = bool(re.match("import .*describe.*from", line))
    if re.match("import .*", line):
        last_import_line = index

if has_import:
    print(f"Skipping {sys.argv[1]}: File already updated.")
    sys.exit(0)

if last_import_line is None:
    print("No imports!")
    sys.exit(0)

lines.insert(last_import_line + 1, "import {describe, expect, test} from 'vitest'\n")

with open(f"{sys.argv[1]}.new", "w") as target_file:
    target_file.writelines(lines)
os.replace(f"{sys.argv[1]}.new", f"{sys.argv[1]}")
