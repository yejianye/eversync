#!/usr/bin/env python
"""
Test markdown and orgmode processors.

This isn't really unit-tests. They just print out the generated ENML from
sample markdown and orgmode file, so that we could easily check whether the
processors work properly.
"""
import os
import sys
print sys.path

from eversync.processor import MarkdownProcessor, OrgModeProcessor
import eversync.processor
print eversync.processor.__file__

test_dir = os.path.dirname(__file__)
markdown_file = os.path.join(test_dir, 'test.md')
orgmode_file = os.path.join(test_dir, 'test.org')

def test_markdown():
    title = "Generated ENML from {}".format(markdown_file)
    print "{}\n{}".format(title, '='*len(title))
    print MarkdownProcessor(markdown_file).get_content()

def test_orgmode(backend):
    title = "Generated ENML from {} using {}".format(orgmode_file, backend)
    print "{}\n{}".format(title, '='*len(title))
    print OrgModeProcessor(orgmode_file, backend).get_content()

if __name__ == '__main__':
    test_markdown()
    print '\n'
    test_orgmode('org_ruby')
    print '\n'
    test_orgmode('orgco')
