# -*- coding: utf-8 -*-

import markdown
import orgco
import os

from lxml.html import clean

from eversync import utils
from eversync.log import debug

ENML_WRAPPER = u"""\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">
<en-note>{}</en-note>"""

__all__ = ['TextProcessor', 'MarkdownProcessor', 'OrgModeProcessor']
def wrap_ENML(content):
    return ENML_WRAPPER.format(content).encode('utf8')

class NoteFileProcessor(object):
    def __init__(self, path):
        self.path = path
        with open(path) as f:
            self.raw_content = f.read()

    def get_title(self):
        components = self.path.split('/')
        components[-1] = components[-1].rsplit('.', 1)[0]
        components = [c.capitalize().replace('-',' ').replace('_',' ')
                      for c in components]
        return ' - '.join(components)

    def body(self):
        raise NotImplementedError()

    def get_content(self):
        if self.raw_content.strip():
            return wrap_ENML(self.body())
        else:
            return wrap_ENML('')

class TextProcessor(NoteFileProcessor):
    def body(self):
        return '<pre>{}</pre>'.format(self.raw_content)

class MarkdownProcessor(NoteFileProcessor):
    def body(self):
        return markdown.markdown(self.raw_content)

class OrgModeProcessor(NoteFileProcessor):
    styles = {
        'table': '-evernote-table:true;border-collapse:collapse;width:100%;table-layout:fixed;margin-left:0px;',
        'th': 'border-style:solid;border-width:1px;border-color:rgb(219,219,219);padding:10px;margin:0px;width:50%;',
        'td': 'border-style:solid;border-width:1px;border-color:rgb(219,219,219);padding:10px;margin:0px;width:50%;',
    }
    def _escape(self, html):
        return html.replace('&', '&amp;')

    def _convert_todo_item(self, html):
        html = html.replace('<li>[ ]', '<li><en-todo/>')
        html = html.replace('<li>[X]', '<li><en-todo checked="true"/>')
        return html

    def _add_styles(self, html):
        for tag, style in self.styles.iteritems():
            html = html.replace('<{}>'.format(tag),
                         "<{} style='{}'>".format(tag, style))
        return html

    def _org_ruby_convert(self):
        html = utils.shell_command('org-ruby {} --translate html'.format(self.path))
        cleaner = clean.Cleaner(safe_attrs_only=True, safe_attrs=frozenset())
        return cleaner.clean_html(html)

    def body(self):
        """Convert note from orgmode to html.
        Use org-ruby if available, otherwise use python orgco module"""
        if utils.executable_exists('org-ruby'):
            html = self._org_ruby_convert()
        else:
            html = orgco.convert_html(self.raw_content)
            html = self._escape(html)
        html = self._convert_todo_item(html)
        return self._add_styles(html)
