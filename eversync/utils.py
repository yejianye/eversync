# -*- coding: utf-8 -*-

import os

def get_file_ext(path):
    return path.split('.')[-1]

def path_to_source_url(notebook, path):
    path_uri = path.replace(' ', '-').replace('\\', '/').lower()
    notebook_uri = notebook.name.replace(' ', '-').lower()
    return 'eversync://{}/{}'.format(notebook_uri, path_uri)

def filter_files(root_dir, exts):
    """Find text files that could be converted to a note.
    Currently, supported file extensions are defined in `supported_file_exts`
    """
    result = []
    for path, _, files in os.walk(root_dir):
        for fname in files:
            ext = get_file_ext(fname)
            if ext in exts:
                relative_path = os.path.relpath(os.path.join(path, fname))
                result.append(relative_path)
    return result

