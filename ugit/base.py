from pathlib import Path
from . import data


def write_tree(directory='.'):
  for entry in Path(directory).iterdir():
    if entry.is_file() and not entry.is_symlink() and not is_ignored(entry):
      with open(entry, 'rb') as f:
        print(data.hash_object(f.read()), entry)
    elif entry.is_dir() and not entry.is_symlink():
      write_tree(entry)


def is_ignored(path):
  return '.ugit' in Path(path).parts
