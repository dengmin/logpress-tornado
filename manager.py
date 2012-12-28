#!/usr/bin/env python
#coding=utf8

import tornado
import tornado.web
from tornado.httpserver import HTTPServer
from tornado.options import define,options
from tornado.web import url
import os,sys
from jinja2 import Environment, FileSystemLoader
from lib import filters,session
from lib.helpers import setting_from_object
from lib.mail import EmailBackend
import config
import redis

define("cmd", default='runserver', metavar="runserver|createuser")
define("port",default=9000,type=int)
define("autoreload",default=False,type=bool)

class Application(tornado.web.Application):
	def __init__(self):
		from urls import routes as handlers
		settings = setting_from_object(config)
		settings.update({
			'template_path':os.path.join(os.path.dirname(__file__),'templates'),
			'static_path':os.path.join(os.path.join(os.path.dirname(__file__),'static')),
			'cookie_secret':"NjAzZWY2ZTk1YWY5NGE5NmIyYWM0ZDAzOWZjMTg3YTU=|1355811811|3245286b611f74805b195a8fec1beea7234d79d6",
			'login_url':'/account/login',
			'autoescape':None
		})
		#init jiaja2 environment
		self.jinja_env = Environment(
			loader = FileSystemLoader(settings['template_path']),
			auto_reload = settings['debug'],
			autoescape = False)

		#register filters for jinja2
		self.jinja_env.filters.update(filters.register_filters())
		self.jinja_env.tests.update({})
		
		self.jinja_env.globals['settings'] = settings
		tornado.web.Application.__init__(self,handlers,**settings)
		self.redis = redis.StrictRedis()
		self.session_store = session.RedisSessionStore(self.redis)
		
		self.email_backend = EmailBackend(
			settings['smtp_server'],settings['smtp_port'],
			settings['smtp_user'],settings['smtp_password'],settings['smtp_usetls'],
			template_loader=self.jinja_env)

def runserver():
	http_server = HTTPServer(Application(),xheaders=True)
	http_server.listen(options.port)
	loop = tornado.ioloop.IOLoop.instance()
	print 'Server running on http://0.0.0.0:%d'%(options.port)
	loop.start()

def createuser():
	username = raw_input('input username: ')
	if username:
		from models import User
		q = User.select().where(User.username==username.strip())
		if q.count()>0:
			print 'username [ %s ] exists! please choice another one and try it again!'%(username)
			sys.exit(0)
		email = raw_input('input your Email: ')
		password = raw_input('input password: ')
		User.create(username=username,email=email.strip(),password=User.create_password(password))
		print '%s created!'%(username)
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
		print 'created table:',model._meta.db_table

if __name__ == '__main__':
	tornado.options.parse_command_line()
	if options.cmd == 'runserver':
		runserver()
	elif options.cmd == 'createuser':
		createuser()
	elif options.cmd == 'syncdb':
		syncdb()
