import hashlib
import os
from pathlib import Path

GIT_DIR = '.ugit'


def init():
  os.makedirs(GIT_DIR)
  os.makedirs(f'{GIT_DIR}/objects')


def set_HEAD(oid):
  Path(f'{GIT_DIR}/HEAD').write_bytes(oid)


def get_HEAD():
  path = Path(f'{GIT_DIR}/HEAD')
  if path.is_file():
    return path.read_bytes().strip()


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
