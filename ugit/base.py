from pathlib import Path
from . import data


def write_tree(directory='.'):
  entries = []
  for entry in Path(directory).iterdir():
    if is_ignored(entry):
      continue
    if entry.is_file() and not entry.is_symlink():
      type_ = 'blob'
      with open(entry, 'rb') as f:
        oid = data.hash_object(f.read())
    elif entry.is_dir() and not entry.is_symlink():
      type_ = 'tree'
      oid = write_tree(entry)
    entries.append((entry.name, oid, type_))

  tree = ''.join(f'{type_} {oid} {name}\n'
                 for name, oid, type_
                 in sorted(entries))
  return data.hash_object(tree.encode(), 'tree')


def _iter_tree_entries(oid):
  if not oid:
    return
  tree = data.get_object(oid, 'tree')
  for entry in tree.decode().splitlines():
    type_, oid, name = entry.split(' ', 2)
    yield type_, oid, name


def get_tree(oid, base_path=''):
  result = {}
  for type_, oid, name in _iter_tree_entries(oid):
    assert '/' not in name
    assert name not in ('..', '.')
    path = base_path + name
    if type_ == 'blob':
      result[path] = oid
    elif type_ == 'tree':
      result.update(get_tree(oid, f'{path}/'))
    else:
      assert False, f'Unknown tree entry {type_}'
  return result


def read_tree(tree_oid):
  for path, oid in get_tree(tree_oid, base_path='./').items():
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'wb') as f:
      f.write(data.get_object(oid))


def is_ignored(path):
  return '.ugit' in Path(path).parts
