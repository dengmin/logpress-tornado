#!/usr/bin/env python
#coding=utf8
try:
    import psyco
    psyco.full()
except:pass
import smtplib
import socket
import threading

class EmailBackend():
	def __init__(self, host=None, port=None, username=None, password=None,
		use_tls=None, fail_silently=False, template_loader=None,**kwargs):
		self.host = host or '127.0.0.1'
		self.port = port or 25
		self.username = username or None
		self.password = password or None
		if use_tls is None:
			self.use_tls = None
		else:
			self.use_tls = use_tls
		self.connection = None
		self.fail_silently = fail_silently
		self.template_loader = template_loader
		self._lock = threading.RLock()

	def open(self):
		if self.connection:
			return False
		try:
			if self.use_tls:
				self.connection = smtplib.SMTP_SSL(self.host, self.port)
			else:
				self.connection = smtplib.SMTP(self.host, self.port)
			if self.username and self.password:
				self.connection.login(self.username, self.password)
			return True
		except:
			if not self.fail_silently:
				raise

	def close(self):
		try:
			try:
				self.connection.quit()
			except socket.sslerror:
				self.connection.close()
			except:
				if self.fail_silently:
					return
				raise
		finally:
			self.connection = None

	def send_message(self,email_messages,callback=None):
		if not email_messages:
			return
		self._lock.acquire()
		try:
			new_conn_created = self.open()
			if not self.connection:
				return
			num_sent = 0
			for message in email_messages:
				sent = self._send(message)
				if sent:
					num_sent += 1
			if new_conn_created:
				self.close()
		finally:
			self._lock.release()
		return num_sent

	def _sanitize(self, email):
		name, domain = email.split('@', 1)
		email = '@'.join([name, domain.encode('idna')])
		return email
	
	def _send(self, email_message):
		if not email_message.recipients():
			return False
		from_email = self._sanitize(email_message.from_email)
		recipients = map(self._sanitize, email_message.recipients())
		try:
			self.connection.sendmail(from_email, recipients,email_message.message().as_string())
		except:
			if not self.fail_silently:
				raise
			return False
		return True
