#!/usr/bin/env python
#encoding=utf-8
import os

DEBUG = True

BLOG_NAME = u'Logpress'
SITE_KEYWORDS=""""""
SITE_DESC= """blog powered by tornado,jinja2,peewee"""
DOMAIN='http://0.0.0.0:9000'

THEME_NAME = 'fluid-blue'

DB_ENGINE = 'peewee.SqliteDatabase'  # peewee.SqliteDatabase,peewee.MySQLDatabase
DB_HOST= '0.0.0.0'
DB_USER = 'root'
DB_PASSWD = 'root'
DB_NAME = os.path.join(os.path.dirname(__file__),'blog.db')  #db file if DB_ENGINE is SqliteDatabase

ADMIN_EMAIL = '594611460@qq.com'
SMTP_SERVER ='smtp.qq.com'
SMTP_PORT = 587
SMTP_USER = 'noreply@szgeist.com'
SMTP_PASSWORD = ''
SMTP_USETLS = True
