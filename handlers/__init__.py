#!/usr/bin/env python
#coding=utf8

from tornado.web import RequestHandler,HTTPError
from handlers.mixin import FlashMessagesMixin,ExceptionMixin
from lib.session import Session
import os

class BaseHandler(RequestHandler,FlashMessagesMixin,ExceptionMixin):

	def render_string(self, template_name, **context):
		context.update({
			'xsrf': self.xsrf_form_html,
			'request': self.request,
			'user': self.current_user,
			'static': self.static_url,
			'handler': self,}
        )

		return self._jinja_render(path = self.get_template_path(),filename = template_name,
            auto_reload = self.settings['debug'], **context)

	def _jinja_render(self,path,filename, **context):
		template = self.application.jinja_env.get_template(filename,parent=path)
		self.write(template.render(**context))

	@property
	def is_xhr(self):
		return self.request.headers.get('X-Requested-With', '').lower() == 'xmlhttprequest'

	@property
	def session(self):
		if hasattr(self, '_session'):
			return self._session
		else:
			sessionid = self.get_secure_cookie('sid')
			self._session = Session(self.application.session_store, sessionid, expires_days=1)
			if not sessionid:
				self.set_secure_cookie('sid', self._session.id, expires_days=1)
			return self._session
	
	def get_current_user(self):
		return self.session['user'] if 'user' in self.session else None

	def get_object_or_404(self,model,**kwargs):
	    try:
	        return model.get(**kwargs)
	    except model.DoesNotExist:
	        raise HTTPError(404)
	@property
	def next_url(self):
		return self.get_argument("next", None)



class ErrorHandler(BaseHandler):
	def prepare(self):
		self.set_status(404)
		raise HTTPError(404)