#!/usr/bin/env python
#coding=utf8

import os
from jinja2 import Environment, FileSystemLoader
from lib.helpers import setting_from_object
from lib.database import Database
from lib.mail import EmailBackend
import config
import redis

redis_server = redis.StrictRedis()

settings = setting_from_object(config)

settings.update({
		'template_path':os.path.join(os.path.dirname(__file__),'templates'),
		'static_path':os.path.join(os.path.join(os.path.dirname(__file__),'static')),
		'cookie_secret':"NjAzZWY2ZTk1YWY5NGE5NmIyYWM0ZDAzOWZjMTg3YTU=|1355811811|3245286b611f74805b195a8fec1beea7234d79d6",
		'login_url':'/account/login',
		"xsrf_cookies": True,
		'autoescape':None
	})

jinja_environment = Environment(
			loader = FileSystemLoader(settings['template_path']),
			auto_reload = settings['debug'],
			autoescape = True)

db = Database({'db':settings['db_name'],'engine':settings['db_engine']})

smtp_server = EmailBackend(
			settings['smtp_server'],settings['smtp_port'],
			settings['smtp_user'],settings['smtp_password'],settings['smtp_usetls'],
			template_loader=jinja_environment,fail_silently=True)