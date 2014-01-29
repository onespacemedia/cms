# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Link.new_window'
        db.add_column(u'links_link', 'new_window',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Link.new_window'
        db.delete_column(u'links_link', 'new_window')


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'links.link': {
            'Meta': {'object_name': 'Link'},
            'link_url': ('cms.models.fields.LinkField', [], {'max_length': '1000'}),
            'new_window': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'page': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'+'", 'unique': 'True', 'primary_key': 'True', 'to': u"orm['pages.Page']"})
        },
        u'pages.page': {
            'Meta': {'ordering': "('left',)", 'unique_together': "(('parent', 'url_title'),)", 'object_name': 'Page'},
            'browser_title': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'expiry_date': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_navigation': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_online': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'left': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'meta_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'meta_keywords': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'child_set'", 'null': 'True', 'to': u"orm['pages.Page']"}),
            'publication_date': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'right': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'robots_archive': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'robots_follow': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'robots_index': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'short_title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'sitemap_changefreq': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'sitemap_priority': ('django.db.models.fields.FloatField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'url_title': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['links']