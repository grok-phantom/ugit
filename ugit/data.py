import hashlib
import os
from pathlib import Path

GIT_DIR = '.ugit'


def init():
  os.makedirs(GIT_DIR)
  os.makedirs(f'{GIT_DIR}/objects')


def hash_object(data, type_='blob'):
  obj = type_.encode() + b'\x00' + data
  oid = hashlib.sha1(obj).hexdigest()
  Path(f'{GIT_DIR}/objects/{oid}').write_bytes(obj)
  return oid


def get_object(oid, expected='blob'):
  obj = Path(f'{GIT_DIR}/objects/{oid}').read_bytes()

  type_, _, content = obj.partition(b'\x00')
  type_ = type_.decode()

  if expected is not None:
    assert type_ == expected, f'Expected {expected}, got {type_}'
  return content
