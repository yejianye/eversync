# -*- coding: utf-8 -*-

import os
import json
import subprocess

from eversync.log import debug

rcfile_path = os.path.join(os.environ['HOME'], '.eversync')
default_ignore_dirs = ['.git']

def get_file_ext(path):
    return path.split('.')[-1]

def path_to_source_url(notebook, path):
    path_uri = path.replace(' ', '-').replace('\\', '/').lower()
    notebook_uri = notebook.name.replace(' ', '-').lower()
    return 'eversync://{}/{}'.format(notebook_uri, path_uri)

def filter_files(root_dir, exts, ignore_dirs=None):
    """Find text files that could be converted to a note.
    Currently, supported file extensions are defined in `supported_file_exts`
    """
    result = []
    if ignore_dirs is None:
        ignore_dirs = default_ignore_dirs
    for path, _, files in os.walk(root_dir):
        rel_path = os.path.relpath(path)
        if any(rel_path.startswith(d) for d in ignore_dirs):
            continue
        for fname in files:
            ext = get_file_ext(fname)
            if ext in exts:
                file_path = os.path.join(rel_path, fname)
                if file_path.startswith('./'):
                    file_path = file_path[2:]
                result.append(file_path)
    return result

def read_setting(key_path):
    """Read setting value given a key path.
    Similar to search node in XML via a key path, this method
    searches the value in the dictionary via a key path.
    The dictionary is stored in $HOME/.eversync with JSON-format.

    Args:
        key_path(list): a list of keys.

    Return:
        obj: the value stored at the end of key path_uri
        None: if at any point, the next key in key path doesn't exist.
    """
    if not os.path.exists(rcfile_path):
        return None
    with open(rcfile_path) as f:
        value = json.load(f, encoding='utf8')
        key_path = [k.decode('utf8') for k in key_path]
        for key in key_path:
            value = value.get(key)
            if not value:
                return None
        return value

def write_setting(key_path, value):
    """Write setting value given a key path.
    If at any point, the next key in key path doesn't exist
    in the dictionary. It will initialize that key with an
    empty dict.

    Settings dictionary would be read from $HOME/.eversync. And
    after updating, the updated dictionary would be written to
    the same file.
    """
    if not os.path.exists(rcfile_path):
        root = settings = {}
    else:
        with open(rcfile_path) as f:
            root = settings = json.load(f)
    key_path = [k.decode('utf8') for k in key_path]
    for key in key_path[:-1]:
        settings = settings.setdefault(key, {})
    settings[key_path[-1]] = value
    with open(rcfile_path, 'w') as f:
        json.dump(root, f, indent=4, encoding='utf8')

class chdir(object):
    def __init__(self, target_dir):
        self.current_dir = os.getcwd()
        self.target_dir = target_dir

    def __enter__(self):
        os.chdir(self.target_dir)

    def __exit__(self, exc_type, exc_value, traceback):
        os.chdir(self.current_dir)

def executable_exists(program):
    return os.popen('which {}'.format(program)) != ''

def shell_command(command):
    with os.popen(command) as f:
        return f.read().decode('utf8')
