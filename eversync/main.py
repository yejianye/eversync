#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sync local directory to evernote notebook
"""
import argparse
import os
import sys
import time
from collections import Counter

from evernote.api.client import EvernoteClient
from evernote.edam.notestore import NoteStore
from evernote.edam.type.ttypes import Notebook, Note, NoteAttributes
from evernote.edam.error.ttypes import EDAMUserException
from evernote.edam.error.constants import EDAMErrorCode

from eversync import utils
from eversync.log import log, error, debug, debug_mode
from eversync.processor import TextProcessor, MarkdownProcessor, OrgModeProcessor

service_host = os.environ.get('EVERNOTE_SERVICE_HOST',
                              'app.yinxiang.com')
dev_token = os.environ.get('EVERNOTE_DEV_TOKEN')
note_processors = {
    'txt': TextProcessor,
    'md': MarkdownProcessor,
    'markdown': MarkdownProcessor,
    'org': OrgModeProcessor,
    'org_archive': OrgModeProcessor
}
supported_file_exts = note_processors.keys()
max_note_count = 10000

def tset_notebook(store, name):
    """Return notebook with specific name.
    Create a new notebook if there isn't an existing one.
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

def evernote_api_error(e, note):
    error(e)
    if e.errorCode == EDAMErrorCode.ENML_VALIDATION:
        error("Invalid note content:")
        error(note.content)
    sys.exit(1)

def update_note(store, note, path):
    """Update a note from the content in a local file
    """
    ext = utils.get_file_ext(path)
    processor_cls = note_processors.get(ext)
    processor = processor_cls(path)
    note.title = processor.get_title()
    note.content = processor.get_content()
    note.updated = os.path.getmtime(path) * 1000
    try:
        store.updateNote(dev_token, note)
    except EDAMUserException as e:
        evernote_api_error(e, note)
    return note

def create_note(store, path, notebook):
    """Create a note from the content in a local file
    """
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
    try:
        return store.createNote(dev_token, note)
    except EDAMUserException as e:
        evernote_api_error(e, note)

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
                debug('{} has been modified since last sync.'.format(f))
                update_note(store, note, f)
                log('Updated [{}](Notebook:{}) from {}'.format(
                    note.title, notebook.name, f))
                result.update({'updated': 1})
        else:
            debug('{} is a new note file.'.format(f))
            note = create_note(store, f, notebook)
            log('Created [{}](Notebook:{}) from {}'.format(
                note.title, notebook.name, f))
            result.update({'created': 1})
    return result

def sync_key(local_dir, notebook_name):
    return '{}({})'.format(os.path.abspath(local_dir), notebook_name)

def changed_since_last_sync(local_dir, notebook_name):
    sync_time = last_sync_time(local_dir, notebook_name)
    files = utils.filter_files(local_dir, supported_file_exts)
    modified_time = max(os.path.getmtime(f) for f in files)
    return modified_time > sync_time

def last_sync_time(local_dir, notebook_name):
    key = sync_key(local_dir, notebook_name)
    return utils.read_setting(['sync_time', key])

def save_sync_time(local_dir, notebook_name):
    key = sync_key(local_dir, notebook_name)
    utils.write_setting(['sync_time', key], time.time())

def sync(local_dir, notebook_name):
    if not os.path.exists(local_dir):
        error("{} doesn't exist".format(local_dir))
    with utils.chdir(local_dir):
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
        log('Please set your evernote developer token in EVERNOTE_DEV_TOKEN.')
        sys.exit(1)
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--dir", default='.', help="Local directory path (default: .)")
    parser.add_argument("--notebook", default="Eversync",
                        help="Notebook in Evernote that local files would be synced to (default: Eversync) ")
    parser.add_argument("--force", default=False, action="store_true",
                        help="Force sync with evernote even there's no change after last sync (default: False)")
    parser.add_argument("--debug", default=False, action="store_true",
                        help="Print debug information")
    args = parser.parse_args()
    if args.debug:
        debug_mode(True)

    if args.force or changed_since_last_sync(args.dir, args.notebook):
        sync(args.dir, args.notebook)
        save_sync_time(args.dir, args.notebook)
    else:
        log("No changes found after last sync time.".format(
            last_sync_time(args.dir, args.notebook)
        ))

if __name__ == '__main__':
    main()
