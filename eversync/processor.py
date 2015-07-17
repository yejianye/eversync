# -*- coding: utf-8 -*-

import markdown
import orgco

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
    def body(self):
        return orgco.convert_html(self.raw_content)
