import hashlib
import os
from pathlib import Path
from collections import namedtuple

GIT_DIR = '.ugit'


def init():
  os.makedirs(GIT_DIR)
  os.makedirs(f'{GIT_DIR}/objects')


RefValue = namedtuple('RefValue', ['symbolic', 'value'])


def update_ref(ref, value, deref=True):
  ref = _get_ref_internal(ref, deref)[0]

  assert value.value
  if value.symbolic:
    value = f'ref: {value.value}'
  else:
    value = value.value

  path = Path(f'{GIT_DIR}/{ref}')
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(value)


def get_ref(ref, deref=True):
  return _get_ref_internal(ref, deref)[1]


def _get_ref_internal(ref, deref):
  path = Path(f'{GIT_DIR}/{ref}')
  value = None
  if path.is_file():
    value = path.read_text().strip()

  symbolic = bool(value) and value.startswith('ref:')
  if symbolic:
    value = value.split(':', 1)[1].strip()
    if deref:
      return _get_ref_internal(value, deref=True)

  return ref, RefValue(symbolic=symbolic, value=value)


def iter_refs(prefix='', deref=True):
  refs = ['HEAD']
  path = Path(f'{GIT_DIR}/refs/tags')
  refs.extend([x.relative_to(GIT_DIR) for x in path.iterdir()])

  for refname in refs:
    if not str(refname).startswith(prefix):
      continue
    yield refname, get_ref(refname, deref=deref)


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
