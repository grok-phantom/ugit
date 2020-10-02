from pathlib import Path
from . import data


def write_tree(directory='.'):
  for entry in Path(directory).iterdir():
    if entry.is_file() and not entry.is_symlink():
      print(entry)
    elif entry.is_dir() and not entry.is_symlink():
      write_tree(entry)
