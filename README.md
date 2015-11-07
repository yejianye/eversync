Eversync
========

Sync your local directories with evernote notebooks.

Note, this script has only been tested with Evernote China (印象笔记) on Mac OSX.

Features
--------
- Sync all org, markdown and plain-text files under a local directory to an evernote notebook
- Incremental sync, only modified orgmode files will be uploaded to evernote 
- Support both Evernote International and Evernote China (印象笔记)
- Support evernote style tables and todo items

Installation
------------
Git clone this repo and run setup in its root directory

```bash
python setup.py install
```

It's also recommended to install [org-ruby](https://github.com/wallyqs/org-ruby), because it's one of the most matured project for converting org files to html. Github uses it to generate org previews on github.com. To install

```bash
gem install org-ruby
```

If `org-ruby` is available, `eversync` will use it to convert orgmode file to html. Otherwise, it will use [orgco](https://github.com/paetzke/orgco), which is a python package for converting orgmode file to other formats.

How to use
----------
First, you need get a developer authentication token at
China: https://dev.yinxiang.com/doc/articles/dev_tokens.php
International: https://www.evernote.com/api/DeveloperToken.action

Setup environment variable for developer token and service host. For example

```bash
export EVERNOTE_DEV_TOKEN="XXXXXX"
# Evernote China
export EVERNOTE_SERVICE_HOST="app.yinxiang.com"
# Evernote International
export EVERNOTE_SERVICE_HOST="www.evernote.com"
```

To sync a local directory to evernote notebook,

```bash
eversync --dir [local-directory-path] --notebook [notebook-name]
```

TODO
----
- Inline image support
