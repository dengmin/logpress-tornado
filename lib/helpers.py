#!/usr/bin/env python
#coding=utf8

from markdown import Markdown
from random import choice
import string
import sys

def create_token(length=16):
    chars = list(string.letters + string.digits)
    salt = ''.join([choice(chars) for i in range(length)])
    return salt

def load_class(s):
    path, klass = s.rsplit('.', 1)
    __import__(path)
    mod = sys.modules[path]
    return getattr(mod, klass)

def setting_from_object(obj):
    settings = dict()
    for key in dir(obj):
        if key.isupper():
            settings[key.lower()] = getattr(obj, key)
    return settings

class ObjectDict(dict):
	def __getattr__(self, key):
		if key in self:
			return self[key]
		return None
	def __setattr__(self, key, value):
		self[key] = value

class cached_property(object):
    def __init__(self, func, name=None, doc=None):
        self.__name__ = name or func.__name__
        self.__module__ = func.__module__
        self.__doc__ = doc or func.__doc__
        self.func = func

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        value = obj.__dict__.get(self.__name__, None)
        if value is None:
            value = self.func(obj)
            obj.__dict__[self.__name__] = value
        return value


def find_subclasses(klass, include_self=False):
    accum = []
    for child in klass.__subclasses__():
        accum.extend(find_subclasses(child, True))
    if include_self:
        accum.append(klass)
    return accum