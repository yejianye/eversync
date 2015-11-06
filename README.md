Eversync
========

Sync your local directories with evernote notebooks.

Note, this script has only been tested with Evernote China (印象笔记) on Mac OSX.

Installation
------------
Git clone this repo and run setup in its root directory
```bash
python setup.py install
```

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
- Display TODO items correctly
