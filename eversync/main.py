#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sync local directory to evernote notebook
"""
import argparse
import os
import sys
from collections import Counter

from evernote.api.client import EvernoteClient
from evernote.edam.notestore import NoteStore
from evernote.edam.type.ttypes import Notebook, Note, NoteAttributes

from eversync import utils
from eversync.log import log, error
from eversync.processor import TextProcessor, MarkdownProcessor, OrgModeProcessor

service_host = os.environ.get('EVERNOTE_SERVICE_HOST',
                              'app.yinxiang.com')
dev_token = os.environ.get('EVERNOTE_DEV_TOKEN')
supported_file_exts = ['txt', 'md', 'markdown', 'org']
note_processors = {
    'txt': TextProcessor,
    'md': MarkdownProcessor,
    'markdown': MarkdownProcessor,
    'org': OrgModeProcessor,
}
max_note_count = 10000

def tset_notebook(store, name):
    """Return notebook with specific name.
    Create a new notebook if there isn't one existing.
    """
    notebooks = store.listNotebooks()
    notebook = [nb for nb in notebooks if nb.name == name]
    if notebook:
        log('Found notebook {}'.format(name))
        return notebook[0]
    else:
        notebook = Notebook()
        notebook.name = name
        notebook.defaultNotebook = False
        log('Create new notebook {}'.format(name))
        return store.createNotebook(dev_token, notebook)

def update_note(store, note, path):
    ext = utils.get_file_ext(path)
    processor_cls = note_processors.get(ext)
    processor = processor_cls(path)
    note.title = processor.get_title()
    note.content = processor.get_content()
    note.updated = os.path.getmtime(path) * 1000
    store.updateNote(dev_token, note)
    return note

def create_note(store, path, notebook):
    ext = utils.get_file_ext(path)
    processor_cls = note_processors.get(ext)
    processor = processor_cls(path)
    note = Note()
    note.title = processor.get_title()
    note.content = processor.get_content()
    attributes = NoteAttributes()
    attributes.sourceURL = utils.path_to_source_url(notebook, path)
    note.attributes = attributes
    note.notebookGuid = notebook.guid
    return store.createNote(dev_token, note)

def upsert_notes(store, files, notebook):
    """Create or update notes from content in local files.
    Technical notes:
    We store file path in sourceURL attribute of a note. And
    use this sourceURL to match notes and files.
    """
    result = Counter({'created':0, 'updated':0, 'removed':0})
    note_filter = NoteStore.NoteFilter()
    note_filter.words = 'notebook:{}'.format(notebook.name)
    existing_notes = store.findNotes(dev_token, note_filter, 0, max_note_count).notes
    # Remove notes
    file_urls = set(utils.path_to_source_url(notebook, f) for f in files)
    removed_notes = [n for n in existing_notes if n.attributes.sourceURL not in file_urls]
    for n in removed_notes:
        log('Removed note [{}]({})'.format(n.title, notebook.name))
        store.deleteNote(dev_token, n.guid)
    result.update({'removed': len(removed_notes)})
    # Create or update notes
    url_to_notes = {n.attributes.sourceURL: n for n in existing_notes}
    for f in files:
        url = utils.path_to_source_url(notebook, f)
        note = url_to_notes.get(url)
        last_modified = os.path.getmtime(f)
        if note:
            if last_modified * 1000 > note.updated:
                update_note(store, note, f)
                log('Updated [{}](Notebook:{}) from {}'.format(
                    note.title, notebook.name, f))
                result.update({'updated': 1})
        else:
            note = create_note(store, f, notebook)
            log('Created [{}](Notebook:{}) from {}'.format(
                note.title, notebook.name, f))
            result.update({'created': 1})
    return result

def sync(local_dir, notebook_name):
    if not os.path.exists(local_dir):
        error("{} doesn't exist", local_dir)
    os.chdir(local_dir)
    client = EvernoteClient(service_host=service_host, token=dev_token)
    store = client.get_note_store()
    notebook = tset_notebook(store, notebook_name)
    files = utils.filter_files('.', supported_file_exts)
    log('Found {} note files under {}'.format(
        len(files), os.getcwd()))
    result = upsert_notes(store, files, notebook)
    log('''Sync completed.
    Created:{created}
    Updated:{updated}
    Removed:{removed}'''.format(**result))

def main():
    if not dev_token:
        print 'Please set your evernote developer token in EVERNOTE_DEV_TOKEN.'
        sys.exit(1)
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--dir", default='.', help="Local directory path (default: .)")
    parser.add_argument("--notebook", default="Eversync", help="Notebook in Evernote that local files would be synced to (default: Eversync) ")
    args = parser.parse_args()
    sync(args.dir, args.notebook)

if __name__ == '__main__':
    main()
