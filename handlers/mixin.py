#!/usr/bin/env python
# coding=utf8
try:
    import psyco
    psyco.full()
except:
    pass
from pygments import highlight
from pygments.lexers import get_lexer_for_filename
from pygments.formatters import HtmlFormatter
import traceback
import sys
import os
import httplib
import tornado


class FlashMessagesMixin(object):

    @property
    def messages(self):
        if not hasattr(self, '_messages'):
            messages = self.get_secure_cookie('flash_messages')
            self._messages = []
            if messages:
                self._messages = tornado.escape.json_decode(messages)
        return self._messages

    def flash(self, message, type='error'):
        self.messages.append((type, message))
        self.set_secure_cookie(
            'flash_messages', tornado.escape.json_encode(self.messages))

    def get_flashed_messages(self):
        messages = self.messages
        self._messages = []
        self.clear_cookie('flash_messages')
        return messages


class ExceptionMixin(object):

    def get_error_html(self, status_code, **kwargs):
        def get_snippet(fp, target_line, num_lines):
            if fp.endswith('.html'):
                fp = os.path.join(self.get_template_path(), fp)
            half_lines = (num_lines / 2)
            try:
                with open(fp) as f:
                    all_lines = [line for line in f]
                    code = ''.join(
                        all_lines[target_line - half_lines:target_line + half_lines])
                    formatter = HtmlFormatter(
                        linenos=True, linenostart=target_line - half_lines, hl_lines=[half_lines + 1])
                    lexer = get_lexer_for_filename(fp)
                    return highlight(code, lexer, formatter)
            except Exception, ex:
                return ''

        if self.application.settings.get('debug', False) is False:
            full_message = kwargs.get('exception', None)
            if not full_message or unicode(full_message) == '':
                full_message = 'Sky is falling!'
            return "<html><title>%(code)d: %(message)s</title><body><h1>%(code)d: %(message)s</h1>%(full_message)s</body></html>" % {
                "code": status_code,
                "message": httplib.responses[status_code],
                "full_message": full_message,
            }
        else:
            exception = kwargs.get('exception', None)
            return self.render_string('errors/exception.html', sys=sys, traceback=traceback, os=os,
                                      get_snippet=get_snippet, exception=exception, status_code=status_code, kwargs=kwargs)
