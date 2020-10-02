from pathlib import Path
from . import data


def write_tree(directory='.'):
  entries = []
  for entry in Path(directory).iterdir():
    if is_ignored(entry):
      continue
    if entry.is_file() and not entry.is_symlink():
      type_ = 'blob'
      oid = data.hash_object(entry.read_bytes())
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


def _empty_current_directory():
  paths = list(Path('.').glob('**/*'))[::-1]
  for path in paths:
    if is_ignored(path):
      continue
    if path.is_file():
      path.unlink()
    else:
      try:
        path.rmdir()
      except (FileNotFoundError, OSError):
        pass


def read_tree(tree_oid):
  _empty_current_directory()
  for path, oid in get_tree(tree_oid, base_path='./').items():
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data.get_object(oid))


def commit(message):
  commit = f'tree {write_tree()}\n'

  HEAD = data.get_HEAD()
  if HEAD:
    commit += f'parent {HEAD}\n'

  commit += '\n'
  commit += f'{message}\n'

  oid = data.hash_object(commit.encode(), 'commit')
  data.set_HEAD(oid)
  return oid


def is_ignored(path):
  return '.ugit' in Path(path).parts
