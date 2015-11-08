# -*- coding: utf-8 -*-

import markdown2
import orgco

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

    def post_process(self, html):
        raise html

    def get_content(self):
        if self.raw_content.strip():
            html = self.post_process(self.body())
            return wrap_ENML(html)
        else:
            return wrap_ENML('')

class TextProcessor(NoteFileProcessor):
    def body(self):
        return '<pre>{}</pre>'.format(self.raw_content)


class MarkdownProcessor(NoteFileProcessor):
    def body(self):
        return markdown2.markdown(self.raw_content, extras=['tables'])

    def post_process(self, html):
        return HTMLPostProcessor(html).run()


class OrgModeProcessor(NoteFileProcessor):
    def __init__(self, path, backend=None):
        super(OrgModeProcessor, self).__init__(path)
        self.backend = backend

    def get_title(self):
        title = super(OrgModeProcessor, self).get_title()
        ext = self.path.rsplit('.', 1)[-1]
        if ext == 'org_archive':
            title += ' Archive'
        return title

    def _escape(self, html):
        return html.replace('&', '&amp;')

    def _org_ruby_convert(self):
        html = utils.shell_command('org-ruby {} --translate html'.format(self.path))
        cleaner = clean.Cleaner(safe_attrs_only=True, safe_attrs=frozenset())
        html = cleaner.clean_html(html)
        # Fix horizontal rule.
        # With org-ruby, it converts dash-lines to '<hr>', which is invalid invalid
        # ENML, converting it to <hr/>
        html = html.replace('<hr>', '<hr/>')
        return html

    def _orgco_convert(self):
        html = orgco.convert_html(self.raw_content)
        return self._escape(html)

    def _select_backend(self):
        """Select backend for converting orgmode to html
        Use org-ruby if available, otherwise use python orgco module
        """
        if utils.executable_exists('org-ruby'):
            return 'org_ruby'
        else:
            return 'orgco'

    def body(self):
        """Convert note from orgmode to html."""
        if not self.backend:
            self.backend = self._select_backend()
        convert_func = getattr(self, '_{}_convert'.format(self.backend))
        return convert_func()

    def post_process(self, html):
        return HTMLPostProcessor(html).run()


class HTMLPostProcessor(object):
    """Post process html content to match evernote style"""
    styles = {
        'table': '-evernote-table:true;border-collapse:collapse;width:100%;table-layout:fixed;margin-left:0px;',
        'th': 'border-style:solid;border-width:1px;border-color:rgb(219,219,219);padding:10px;margin:0px;width:50%;',
        'td': 'border-style:solid;border-width:1px;border-color:rgb(219,219,219);padding:10px;margin:0px;width:50%;',
    }

    def __init__(self, html):
        self.input = html

    def _convert_todo_item(self, html):
        html = html.replace('<li>[ ]', '<li><en-todo/>')
        html = html.replace('<li>[X]', '<li><en-todo checked="true"/>')
        return html

    def _add_styles(self, html):
        for tag, style in self.styles.iteritems():
            html = html.replace('<{}>'.format(tag),
                         "<{} style='{}'>".format(tag, style))
        return html

    def run(self):
        html = self._convert_todo_item(self.input)
        return self._add_styles(html)
