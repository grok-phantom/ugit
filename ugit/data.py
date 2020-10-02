import hashlib
import os
from pathlib import Path

GIT_DIR = '.ugit'


def init():
  os.makedirs(GIT_DIR)
  os.makedirs(f'{GIT_DIR}/objects')


def update_ref(ref, oid):
  path = Path(f'{GIT_DIR}/{ref}')
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(oid)


def get_ref(ref):
  path = Path(f'{GIT_DIR}/{ref}')
  if path.is_file():
    return path.read_text().strip()


def iter_refs():
  refs = ['HEAD']
  path = Path(f'{GIT_DIR}/refs/tags')
  refs.extend([x.relative_to(GIT_DIR) for x in path.iterdir()])

  for refname in refs:
    yield refname, get_ref(refname)


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
