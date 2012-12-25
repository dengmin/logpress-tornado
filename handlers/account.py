#!/usr/bin/env python
#coding=utf8

from handlers import BaseHandler

from models import User

class LoginHandler(BaseHandler):

	def get(self):
		self.render('admin/login.html')
	
	def post(self):
		username = self.get_argument('username',None)
		password = self.get_argument('password',None)
		if username and password:
			try:
				user = User.get((User.username==username) | (User.email== username))
				if user.check_password(password):
					self.session['user'] = user
					self.session.save()
					self.redirect('/admin')
					return
				else:
					self.flash('UserName or password invidate!')
			except Exception,e:
				self.flash('%s not Found!' %username)
		self.render('admin/login.html')
		return


class LogoutHandler(BaseHandler):
	def get(self):
		del self.session["user"]
		self.sesison.save()
		self.redirect(self.get_login_url())
		return

routes = [
	(r'/account/login',LoginHandler),
	(r'/account/logout',LogoutHandler),
]