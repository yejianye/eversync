# -*- coding: utf-8 -*-

import markdown
import orgco
import os

from lxml.html import clean


from eversync import utils

__all__ = ['TextProcessor', 'MarkdownProcessor', 'OrgModeProcessor']
def wrap_ENML(content):
    return '<?xml version="1.0" encoding="UTF-8"?>\n'\
        '<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">\n'\
        '<en-note>{}</en-note>'.format(content)

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
        return wrap_ENML(self.body())

class TextProcessor(NoteFileProcessor):
    def body(self):
        return '<pre>{}</pre>'.format(self.raw_content)

class MarkdownProcessor(NoteFileProcessor):
    def body(self):
        return markdown.markdown(self.raw_content)

class OrgModeProcessor(NoteFileProcessor):
    def _escape(self, html):
        return html.replace('&', '&amp;')

    def _org_ruby_convert(self):
        html = utils.shell_command('org-ruby {} --translate html'.format(self.path))
        cleaner = clean.Cleaner(safe_attrs_only=True, safe_attrs=frozenset())
        return cleaner.clean_html(html)

    def body(self):
        """Convert note from orgmode to html.
        Use org-ruby if available, otherwise use python orgco module"""
        if utils.executable_exists('org-ruby'):
            return self._org_ruby_convert()
        html = orgco.convert_html(self.raw_content)
        return self._escape(html)
