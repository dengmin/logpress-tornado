#!/usr/bin/env python
# coding=utf8
try:
    import psyco
    psyco.full()
except:
    pass
import tornado
import tornado.web
from tornado.httpserver import HTTPServer
from tornado.options import define, options
from tornado.web import url
import sys

from lib import filters, session

from core import jinja_environment, smtp_server
from core import settings
from core import redis_server

define("cmd", default='runserver', metavar="runserver|createuser")
define("port", default=9000, type=int)
define("autoreload", default=False, type=bool)


class Application(tornado.web.Application):

    def __init__(self):
        from urls import routes as handlers

        # init jiaja2 environment
        self.jinja_env = jinja_environment

        # register filters for jinja2
        self.jinja_env.filters.update(filters.register_filters())
        self.jinja_env.tests.update({})

        self.jinja_env.globals['settings'] = settings
        tornado.web.Application.__init__(self, handlers, **settings)
        self.session_store = session.RedisSessionStore(redis_server)
        self.email_backend = smtp_server


def runserver():
    http_server = HTTPServer(Application(), xheaders=True)
    http_server.listen(options.port)
    loop = tornado.ioloop.IOLoop.instance()
    print 'Server running on http://0.0.0.0:%d' % (options.port)
    loop.start()


def createuser():
    username = raw_input('input username: ')
    if username:
        from models import User
        q = User.select().where(User.username == username.strip())
        if q.count() > 0:
            print 'username [ %s ] exists! please choice another one and try it again!' % (username)
            sys.exit(0)
        email = raw_input('input your Email: ')
        password = raw_input('input password: ')
        User.create(username=username, email=email.strip(),
                    password=User.create_password(password))
        print '%s created!' % (username)
    else:
        print 'username is null,exit!'
        sys.exit(0)


def syncdb():
    from lib.helpers import find_subclasses
    from models import db
    models = find_subclasses(db.Model)
    for model in models:
        if model.table_exists():
            model.drop_table()
        model.create_table()
        print 'created table:', model._meta.db_table

if __name__ == '__main__':
    tornado.options.parse_command_line()
    if options.cmd == 'runserver':
        runserver()
    elif options.cmd == 'createuser':
        createuser()
    elif options.cmd == 'syncdb':
        syncdb()
