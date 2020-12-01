#!/usr/bin/env python3

import json
import os
import subprocess
import sys
import tempfile
from fdroidserver import common, index


def exit_with_value(value):
    if value != 0:
        print('exit with changes')
    os.remove('signed')
    os.remove('unsigned')
    sys.exit(value)

with open('repo/index-v1.json') as fp:
    unsigned = json.load(fp)

index.config = {'jarsigner': '/usr/bin/jarsigner'}
common.config = index.config
signed, _i, _i = index.get_index_from_jar('repo/index-v1.jar')

unsigned['repo']['timestamp'] = signed['repo']['timestamp']

tmpdir = tempfile.mkdtemp()
os.chdir(tmpdir)
with open('signed', 'w') as fp:
    json.dump(signed, fp, indent=2)

with open('unsigned', 'w') as fp:
    json.dump(unsigned, fp, indent=2)

if os.path.getsize('signed') != os.path.getsize('unsigned'):
    print('differ by size')
    exit_with_value(1)

p = subprocess.run(['diff', '-uw', 'signed', 'unsigned'])
exit_with_value(p.returncode)
