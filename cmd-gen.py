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

crypto = CryptoEngine()
crypto.setup_sd_key_from_file(a.movable)
tmd = TitleMetadataReader.from_file(a.tmd)
dirname = os.path.dirname(a.tmd)

content_ids = []
cmacs = []

for chunk in tmd.chunk_records:
    try:
        with open(os.path.join(dirname, chunk.id + '.app'), 'rb') as f:
            f.seek(0x100)
            header = f.read(0x100)

            id_bytes = bytes.fromhex(chunk.id)[::-1]
            data = header + chunk.cindex.to_bytes(4, 'little') + id_bytes
            data_hash = sha256(data)

            c = crypto.create_cmac_object(Keyslot.CMACSDNAND)
            c.update(data_hash.digest())
            cmacs.append(c.digest())
            content_ids.append(id_bytes)
    except FileNotFoundError:
        exit(f'Could not find {chunk.id}.app. Missing contents is currently not supported.')

final = bytes.fromhex(a.output_id)[::-1] + ((len(content_ids).to_bytes(4, 'little')) * 2) + (1).to_bytes(4, 'little')
c = crypto.create_cmac_object(Keyslot.CMACSDNAND)
c.update(final)
final += c.digest()

final += b''.join(content_ids)
final += b''.join(content_ids[::-1])
final += b''.join(cmacs)

os.makedirs(os.path.join(dirname, 'cmd'), exist_ok=True)
with open(os.path.join(dirname, 'cmd', a.output_id + '.cmd'), 'wb') as o:
    o.write(final)
