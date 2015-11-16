#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Jason Owen'
SITENAME = u'Jason Owen'
SITEURL = ''

TIMEZONE = 'America/Los_Angeles'

DEFAULT_LANG = u'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None

# Blogroll
LINKS =  ()

# Social widget
SOCIAL = (
  ('GitHub', 'https://github.com/jasonaowen'),
  ('Twitter', 'https://twitter.com/jasonaowen'),
)

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
RELATIVE_URLS = True

#SUMMARY_MAX_LENGTH = 50

ARTICLE_URL = '{date:%Y}/{date:%b}/{date:%d}/{slug}/'
ARTICLE_SAVE_AS = '{date:%Y}/{date:%b}/{date:%d}/{slug}/index.html'

PLUGIN_PATH = '../pelican-plugins/'
PLUGINS = ['neighbors', 'summary']
