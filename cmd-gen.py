#!/usr/bin/env python3

# This file is a part of cmd-gen.
#
# Copyright (c) 2019 Ian Burgwin
# This file is licensed under The MIT License (MIT).
# You can find the full license text in LICENSE.md in the root of this project.

import argparse
import os
from hashlib import sha256

from pyctr.crypto import CryptoEngine, Keyslot
from pyctr.types.tmd import TitleMetadataReader

parser = argparse.ArgumentParser(description='Generate Nintendo 3DS CMD files.')
parser.add_argument('-t', '--tmd', help='tmd file', required=True)
parser.add_argument('-m', '--movable', help='movable.sed file', required=True)
parser.add_argument('-b', '--boot9', help='boot9 file')
parser.add_argument('--output-id', help='CMD content ID, default 00000001', default='00000001')

a = parser.parse_args()

MISSING = b'\xff\xff\xff\xff'

crypto = CryptoEngine()
crypto.setup_sd_key_from_file(a.movable)
tmd = TitleMetadataReader.from_file(a.tmd)
dirname = os.path.dirname(a.tmd)
if tmd.title_id.startswith('0004008c'):
    content_dir = os.path.join(dirname, '00000000')
else:
    content_dir = dirname

highest_index = 0
content_ids = {}

for chunk in tmd.chunk_records:
    try:
        with open(os.path.join(content_dir, chunk.id + '.app'), 'rb') as f:
            highest_index = chunk.cindex
            f.seek(0x100)
            header = f.read(0x100)

            id_bytes = bytes.fromhex(chunk.id)[::-1]
            data = header + chunk.cindex.to_bytes(4, 'little') + id_bytes
            data_hash = sha256(data)

            c = crypto.create_cmac_object(Keyslot.CMACSDNAND)
            c.update(data_hash.digest())
            content_ids[chunk.cindex] = (id_bytes, c.digest())
    except FileNotFoundError:
        # currently unknown if there's actually a process to generating the cmac for missing contents
        pass

# add content IDs up to the last one
ids_by_index = [MISSING] * (highest_index + 1)
installed_ids = []
cmacs = []
for x in range(len(ids_by_index)):
    try:
        info = content_ids[x]
    except KeyError:
        # the 3DS actually puts either random data, or generates it using an unknown process.
        # probably doesn't matter though, since these contents aren't installed
        cmacs.append(b'\xdd' * 16)
    else:
        ids_by_index[x] = info[0]
        cmacs.append(info[1])
        installed_ids.append(info[0])
installed_ids.sort(key=lambda x: int.from_bytes(x, 'little'))

final = bytes.fromhex(a.output_id)[::-1] \
        + len(ids_by_index).to_bytes(4, 'little') \
        + len(installed_ids).to_bytes(4, 'little') \
        + (1).to_bytes(4, 'little')
c = crypto.create_cmac_object(Keyslot.CMACSDNAND)
c.update(final)
final += c.digest()

final += b''.join(ids_by_index)
final += b''.join(installed_ids)
final += b''.join(cmacs)

os.makedirs(os.path.join(dirname, 'cmd'), exist_ok=True)
with open(os.path.join(dirname, 'cmd', a.output_id + '.cmd'), 'wb') as o:
    o.write(final)
