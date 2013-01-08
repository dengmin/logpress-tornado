#!/usr/bin/env python
#coding=utf8
try:
    import psyco
    psyco.full()
except:pass
import time
import os
import socket
import random
from email.MIMEText import MIMEText
from email.Header import Header
from email import Charset, Encoders
from email.Utils import formatdate, getaddresses, formataddr, parseaddr
from .encoding import smart_str, force_unicode
from tornado import gen

DEFAULT_CHARSET = 'utf8'
DEFAULT_FROM_EMAIL = 'noreply@localhost'

class BadHeaderError(ValueError):
	pass

class CachedDnsName(object):
    def __str__(self):
        return self.get_fqdn()

    def get_fqdn(self):
        if not hasattr(self, '_fqdn'):
            self._fqdn = socket.getfqdn()
        return self._fqdn

DNS_NAME = CachedDnsName()

def forbid_multi_line_headers(name, val, encoding):
	encoding = encoding or DEFAULT_CHARSET
	val = force_unicode(val)
	if '\n' in val or '\r' in val:
		raise BadHeaderError("Header values can't contain newlines (got %r for header %r)" % (val, name))
	try:
		val = val.encode('ascii')
	except UnicodeEncodeError:
		if name.lower() in ('to', 'from', 'cc'):
			val = ', '.join(sanitize_address(addr, encoding) for addr in getaddresses((val,)))
		else:
			val = str(Header(val, encoding))
	else:
		if name.lower() == 'subject':
			val = Header(val)
	return name, val


def sanitize_address(addr, encoding):
    if isinstance(addr, basestring):
        addr = parseaddr(force_unicode(addr))
    nm, addr = addr
    nm = str(Header(nm, encoding))
    try:
        addr = addr.encode('ascii')
    except UnicodeEncodeError:  # IDN
        if u'@' in addr:
            localpart, domain = addr.split(u'@', 1)
            localpart = str(Header(localpart, encoding))
            domain = domain.encode('idna')
            addr = '@'.join([localpart, domain])
        else:
            addr = str(Header(addr, encoding))
    return formataddr((nm, addr))


class SafeMIMEText(MIMEText):
	def __init__(self, text, subtype, charset):
		self.encoding = charset
		MIMEText.__init__(self, text, subtype, charset)

	def __setitem__(self, name, val):
		name, val = forbid_multi_line_headers(name, val, self.encoding)
		MIMEText.__setitem__(self, name, val)

class EmailMessage(object):
	content_subtype = 'plain'
	mixed_subtype = 'mixed'
	encoding = None
	def __init__(self, subject, body='', from_email=None, to=None, cc=None,
		connection=None):

		if to:
			assert not isinstance(to, basestring), '"to" argument must be a list or tuple'
			self.to = list(to)
		else:
			self.to = []
		if cc:
			assert not isinstance(cc, basestring), '"cc" argument must be a list or tuple'
			self.cc = list(cc)
		else:
			self.cc = []
		self.from_email = from_email or DEFAULT_FROM_EMAIL
		self.subject = subject
		self.body = body
		self.connection = connection

	def message(self):
		encoding = self.encoding or DEFAULT_CHARSET
		msg = SafeMIMEText(smart_str(self.body, encoding),
				self.content_subtype, encoding)
		msg['Subject'] = self.subject
		msg['From'] = self.from_email
		msg['To'] = ', '.join(self.to)
		if self.cc:
			msg['Cc'] = ', '.join(self.cc)
		return msg

	def recipients(self):
		return self.to + self.cc

	@gen.engine
	def send(self):
		yield gen.Task(self.connection.send_message, [self])


class TemplateEmailMessage(EmailMessage):
	content_subtype = "html"
	def __init__(self, subject, template, from_email=None, to=None, cc=None,
		connection=None, params={}):
		if not connection.template_loader:
			raise Exception("Must to set a template_loader to EmailBackend")

		body = connection.template_loader.get_template(template).render(**params)
		
		super(TemplateEmailMessage, self).__init__(subject, body, from_email, to,
            cc, connection)

