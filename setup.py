#!/usr/bin/env python
#coding: utf-8

from distutils.core import setup

setup(
	name = "cms",
	author = "Daniel Samuels",
	author_email = "daniel@onespacemedia.com",
	version = "1.0.0",
	license = "BSD",
	url = "https://github.com/onespacemedia/cms",
	download_url = "https://github.com/onespacemedia/cms",
	description = "Onespacemedia's CMS for Django, forked from Etianen's CMS",
	py_modules = ['cms'],
	packages = ['cms', 'cms.apps', 'cms.apps.links', 'cms.apps.links.migrations', 'cms.apps.media', 'cms.apps.media.migrations', 'cms.apps.news', 'cms.apps.news.migrations', 'cms.apps.news.templatetags', 'cms.apps.pages', 'cms.apps.pages.migrations', 'cms.apps.pages.templatetags', 'cms.bin', 'cms.models', 'cms.project_template.project_name', 'cms.project_template.project_name.apps', 'cms.project_template.project_name.apps.site', 'cms.project_template.project_name.apps.site.migrations', 'cms.project_template.project_name.settings', 'cms.templatetags'],
	install_requires = ['psycopg2', 'django-suit', 'django-optimizations', 'Pillow', 'django-reversion', 'django-usertools', 'django-historylinks', 'django-watson', 'South'],
	scripts = ['cms/bin/start_cms_project.py']
)
